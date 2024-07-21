# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Install python3 -m pip install ./aws-iot-device-sdk-python-v2
RUN pip install ./keyfiles/aws-iot-device-sdk-python-v2

# Make port 5683 available to the world outside this container (CoAP port)
EXPOSE 5683

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "mainloop.py", "--endpoint", "a1y59rmca2fvva-ats.iot.eu-central-1.amazonaws.com", "--ca_file", "keyfiles/root-CA.crt", "--cert", "keyfiles/test-solana.cert.pem", "--key", "keyfiles/test-solana.private.key", "--client_id", "SensorNode"]