import os
from dotenv import load_dotenv
from elevenlabs import play, stream
from elevenlabs.client import ElevenLabs
import asyncio


# Load environment variables
load_dotenv()

# Get API key from environment
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # Default voice, you can change this

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
# ralles: testing long speeches
PARAGRAPHS = "The advent of technology has transformed countless sectors, with education standing out as one of the most significantly impacted fields. In recent years, educational technology, or EdTech, has revolutionized the way. e advent of technology has transformed countless sectors, with education standing out as one of the most significantly impacted fields. In recent years, educational technology, or EdTech, has revolutionized the way. e advent of technology has transformed countless sectors, with education standing out as one of the most significantly impacted fields. In recent years, educational technology, or EdTech, has revolutionized the way"


def speak(text):
    try:
        audio = client.generate(
            text=text, voice=ELEVENLABS_VOICE_ID, model="eleven_monolingual_v1"
        )
        play(audio)
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")


continue_talking = True


def interrupt():
    global continue_talking
    continue_talking = False


def uninterrupt():
    global continue_talking
    continue_talking = True


def wrap_stream(audio):
    global continue_talking
    for x in audio:
        # ralles: allows us to manually interrupt the stream
        if not continue_talking:
            return
        yield x


# ralles: enabling streaming is especially helpful for long responses
async def speak_stream(text):
    try:
        audio = client.generate(
            text=text,
            voice=ELEVENLABS_VOICE_ID,
            model="eleven_monolingual_v1",
            stream=True,
        )
        stream(audio)
    except OSError as e:
        if e.errno == 32:
            print("successfully interrupted")
        else:
            print(f"Error in text-to-speech: {str(e)}")
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
