from dotenv import load_dotenv
import os
import requests
from elevenlabs.api import User
import base64

# Load environment variables
load_dotenv()

# Set API key for ElevenLabs
ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")

# Voice IDs for ElevenLabs
ELEVENLABS_VOICE_IDS = {
    "LUKE": "hebTAnd8Ry07PXF07TBK",    # Young American Male
    "KNIGHTLY": "9fT2atdGVNMs9eOSAEWZ", # Old British Male
    "DAN": "OZCcpR3NOKIgWxketgTO",      # Young American Male
}


def get_user_info(api_key=ELEVEN_LABS_API_KEY):
    """
    Retrieves the current user's used character count and subscription character limit.
    """
    url = "https://api.elevenlabs.io/v1/user"

    headers = {"xi-api-key": f'{api_key}'}

    response = requests.request("GET", url, headers=headers)

    return response.json()["subscription"]["character_count"], response.json()["subscription"]["character_limit"]

def check_character_limit(text, used_characters, character_limit):
    """
    Checks if the addition of text will exceed the character limit.

    Parameters:
    text (str): Text to be converted to speech.
    used_characters (int): Number of characters already used.
    character_limit (int): Maximum allowed characters.

    Returns:
    bool: True if limit is exceeded, False otherwise.
    """
    text_character_limit = len(text)
    if used_characters + text_character_limit > character_limit:
        total_characters = used_characters + text_character_limit
        error_message = (f"You will exceed the character limit for ElevenLabs. "
                         f"Current used characters: {used_characters}, "
                         f"Text character count: {text_character_limit}, "
                         f"Total if allowed: {total_characters}, "
                         f"Character limit: {character_limit}")
        raise ValueError(error_message)
    return False


def elevenLabs_text_to_speech(
    text,
    voice_id=ELEVENLABS_VOICE_IDS["LUKE"],
    api_key=ELEVEN_LABS_API_KEY,
    model_id="eleven_monolingual_v1",
    stability=0.5,
    similarity_boost=0.5,
    output_file="output.mp3",
    overwrite=False
):
    if os.path.exists(output_file) and not overwrite:
        print(f"File already exists at {output_file}. Skipping audio generation...")
        return

    used_characters, character_limit = get_user_info()
    if check_character_limit(text, used_characters, character_limit):
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
        },
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error in request to ElevenLabs API: {response.text}")

        # Convert binary response data to base64
        base64_encoded_data = base64.b64encode(response.content)
        base64_message = base64_encoded_data.decode('utf-8')
        # base64_message now contains your base64-encoded data
        # You can use it as needed for your API
        return base64_message
    except Exception as e:
        # Log the error or return a message
        error_message = f"Error in request to ElevenLabs API: {e}"
        print(error_message)
        return error_message  # or handle it as per your application's error handling policy

def write_base64_audio_to_file(base64_data, output_audio_path, chunk_size=1024):
    """
    Decode base64 audio data and write it to a file in chunks.

    :param base64_data: Base64 encoded audio data.
    :param output_audio_path: Path to save the decoded audio file.
    :param chunk_size: Size of chunks to write to file (in bytes).
    """
    audio_bytes = base64.b64decode(base64_data)

    with open(output_audio_path, "wb") as f:
        for i in range(0, len(audio_bytes), chunk_size):
            f.write(audio_bytes[i:i+chunk_size])