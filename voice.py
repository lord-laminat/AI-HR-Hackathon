from vosk import Model, KaldiRecognizer
import pyaudio
import json
import time

STOP_WORDS = {"стоп", "конец"}
SEGMENT_DURATION_SECONDS = 30

def recognize_speech_segment(model_path="vosk-model-small-ru-0.22"):
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Говорите... (стоп-слово или 30 сек для окончания сегмента)")
    current_segment_text = ""
    segment_start_time = time.time()

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get("text", "").strip()
                if text:
                    print(f"Распознано: {text}")
                    current_segment_text += " " + text

                    if any(stop_word in text.lower() for stop_word in STOP_WORDS):
                        print("Стоп-слово обнаружено, сегмент завершен.")
                        return current_segment_text.strip()

                    if time.time() - segment_start_time > SEGMENT_DURATION_SECONDS:
                        print("Превышена длина сегмента, сегмент завершен.")
                        return current_segment_text.strip()
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nЗавершение работы")
        return current_segment_text.strip()
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()

if __name__ == "__main__":
    text = recognize_speech_segment()
    print(f"Сегмент: {text}")
