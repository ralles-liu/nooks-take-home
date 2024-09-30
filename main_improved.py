import asyncio
import subprocess
import time
import pyaudio as pa
import numpy as np
from packages.sales_chatbot import SalesChatbot
from packages.nemo_stt import (
    StreamingTranscription,
)  # Update the class name if different
from packages.elevenlabs_tts import (
    speak_stream,
)  # Update the class name if different
import subprocess


SAMPLE_RATE = 16000
CHUNK_SIZE = 160  # ms
WAIT_TIME = 500  # ms

transcriber = StreamingTranscription()
chatbot = SalesChatbot()

state = {
    "last_text": "",
    "silence_duration": 0,
    "background_task": None,
}
loop = asyncio.new_event_loop()


async def handle_text(text):
    if text != "":
        ai_response = await chatbot.async_generate_response(text)
        while True:
            if state["silence_duration"] >= WAIT_TIME:
                break
            await asyncio.sleep(0.1)

        print(f"USER: {state['last_text']}")
        print(f"AI: {ai_response}")
        await speak_stream(ai_response)


def callback(in_data, *_):
    global loop
    signal = np.frombuffer(in_data, dtype=np.int16)
    text = transcriber.transcribe_chunk(signal)
    # uncomment to easily track whats going on in callback
    # print("ralles text", text)
    if text != state["last_text"]:
        print("ralles reset state in callback")
        state["last_text"] = text
        state["silence_duration"] = 0
        if state["background_task"]:
            state["background_task"].cancel()
            state["background_task"] = None
        # ralles: immediately cancel the audio that is playing
        if text != "":
            subprocess.run(["pkill", "mpv"])
        state["background_task"] = asyncio.run_coroutine_threadsafe(
            handle_text(text), loop
        )
    else:
        state["silence_duration"] += CHUNK_SIZE / 1.5
        if state["silence_duration"] >= WAIT_TIME and len(state["last_text"]) > 0:
            transcriber.reset_transcription_cache()
    return (in_data, pa.paContinue)


p = pa.PyAudio()
print("Available audio input devices:")
input_devices = []
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get("maxInputChannels"):
        input_devices.append(i)
        print(i, dev.get("name"))

if len(input_devices):
    dev_idx = -2
    while dev_idx not in input_devices:
        print("Please type input device ID:")
        dev_idx = int(input())

    # ralles: tried manipulating inputs but got cursed results
    stream = p.open(
        format=pa.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=dev_idx,
        stream_callback=callback,
        frames_per_buffer=int(SAMPLE_RATE * CHUNK_SIZE / 1000) - 1,
    )

    print("Listening...")
    asyncio.set_event_loop(loop)
    stream.start_stream()

    try:
        loop.run_forever()
        while stream.is_active():
            time.sleep(0.1)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        loop.stop()

        print()
        print("PyAudio stopped")
else:
    print("ERROR: No audio input device found.")
