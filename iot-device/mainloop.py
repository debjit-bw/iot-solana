import json, sys, time, random, threading, asyncio
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
from aiocoap import *
import aiocoap.resource as resource
import aiocoap
from command_line_utils import CommandLineUtils

cmdData = CommandLineUtils.parse_sample_input_pubsub()

# MQTT Setup for AWS IoT
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")

def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"Connection resumed. return_code: {return_code} session_present: {session_present}")
    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe results: {resubscribe_results}")
    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")

def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print(f"Received message from topic '{topic}': {payload}")

def on_connection_success(connection, callback_data):
    print(f"Connection Successful with return code: {callback_data.return_code} session present: {callback_data.session_present}")

def on_connection_failure(connection, callback_data):
    print(f"Connection failed with error code: {callback_data.error}")

def on_connection_closed(connection, callback_data):
    print("Connection closed")

# python3 mainloop.py --endpoint a1y59rmca2fvva-ats.iot.eu-central-1.amazonaws.com --ca_file keyfiles/root-CA.crt --cert keyfiles/test-solana.cert.pem --key keyfiles/test-solana.private.key --client_id basicPubSub --topic sdk/test/python
def start_mqtt_connection():
    proxy_options = None
    if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
        proxy_options = http.HttpProxyOptions(
            host_name=cmdData.input_proxy_host,
            port=cmdData.input_proxy_port)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=cmdData.input_endpoint,
        port=cmdData.input_port,
        cert_filepath=cmdData.input_cert,
        pri_key_filepath=cmdData.input_key,
        ca_filepath=cmdData.input_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=cmdData.input_clientId,
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=proxy_options,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed)
    print("Connecting to AWS IoT...")
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("Connected to AWS IoT!")

    return mqtt_connection

def publish_data(mqtt_connection):
    while True:
        temperature = random.uniform(20, 30)
        humidity = random.uniform(40, 60)
        data = {
            "temperature": temperature,
            "humidity": humidity
        }
        message_json = json.dumps(data)
        mqtt_connection.publish(
            # topic="sdk/test/python",
            topic="weather/data",
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(f"Published message: {message_json}")
        time.sleep(1)

# CoAP Resource using aiocoap
class WeatherResource(resource.Resource):
    async def render_get(self, request):
        temperature = random.uniform(20, 30)
        humidity = random.uniform(40, 60)
        payload = f"Temperature: {temperature} C, Humidity: {humidity} %"
        return aiocoap.Message(content_format=0, payload=payload.encode('utf-8'))

# CoAP Server
async def start_coap_server():
    root = aiocoap.resource.Site()
    root.add_resource(['weather'], WeatherResource())

    asyncio.Task(aiocoap.Context.create_server_context(root, bind=("0.0.0.0", 5683)))

    # Run forever
    await asyncio.get_running_loop().create_future()

def start_mqtt_and_coap():
    mqtt_connection = start_mqtt_connection()
    mqtt_thread = threading.Thread(target=publish_data, args=(mqtt_connection,))
    mqtt_thread.start()

    # asyncio.run(start_coap_server())

# Start MQTT connection and CoAP server
if __name__ == "__main__":
    start_mqtt_and_coap()
