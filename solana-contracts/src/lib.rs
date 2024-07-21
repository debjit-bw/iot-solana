use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    pubkey::Pubkey,
    msg,
    program_error::ProgramError,
    program_pack::{IsInitialized, Pack, Sealed},
};

entrypoint!(process_instruction);

#[derive(BorshSerialize, BorshDeserialize, Debug, Default)]
pub struct WeatherData {
    pub is_initialized: bool,
    pub temperature: f32,
    pub humidity: f32,
}

impl Sealed for WeatherData {}

impl IsInitialized for WeatherData {
    fn is_initialized(&self) -> bool {
        self.is_initialized
    }
}

impl Pack for WeatherData {
    const LEN: usize = 9; // 1 byte for bool + 4 bytes for f32 + 4 bytes for f32
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> {
        let data = WeatherData::try_from_slice(src).map_err(|_| ProgramError::InvalidAccountData)?;
        Ok(data)
    }
    fn pack_into_slice(&self, dst: &mut [u8]) {
        let mut dst_mut = &mut dst[..];
        self.serialize(&mut dst_mut).unwrap();
    }
}

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account = next_account_info(accounts_iter)?;

    if account.owner != program_id {
        return Err(ProgramError::IncorrectProgramId);
    }

    let mut weather_data = WeatherData::unpack_unchecked(&account.data.borrow())?;
    let (temperature, humidity) = instruction_data.split_at(4);
    weather_data.temperature = f32::from_le_bytes(temperature.try_into().unwrap());
    weather_data.humidity = f32::from_le_bytes(humidity.try_into().unwrap());
    weather_data.is_initialized = true;
    WeatherData::pack(weather_data, &mut account.data.borrow_mut())?;

    msg!("Weather data updated!");
    Ok(())
}
