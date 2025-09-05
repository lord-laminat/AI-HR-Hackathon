from vosk import Model, KaldiRecognizer
import pyaudio
import json
import time

STOP_WORDS = {"стоп", "конец"}
SEGMENT_DURATION_SECONDS = 30

def offline_speech_recognition(model_path="vosk-model-small-ru-0.22"):
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Говорите... (Ctrl+C для выхода)")
    
    segments = []
    current_segment_text = ""
    segment_start_time = time.time()

    try:
        while True:
            data = stream.read(4000)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get("text", "").strip()
                if text:
                    print(f"Распознано: {text}")
                    #Saivong at segment
                    current_segment_text += " " + text
                    
                    #Checking stop-word
                    if any(stop_word in text.lower() for stop_word in STOP_WORDS):
                      print("Стоп-слово обнаружено, сегмент завершен.")
                      segments.append(current_segment_text.strip())
                      current_segment_text = ""
                      segment_start_time = time.time()
                      continue
                    
                    #Checking time over
                    if time.time() - segment_start_time > SEGMENT_DURATION_SECONDS:
                      print("Превышена длина сегмента, сегмент завершен.")
                      segments.append(current_segment_text.strip())
                      current_segment_text = ""
                      segment_start_time = time.time()
                      
    except KeyboardInterrupt:
        print("\nЗавершение работы")
        # Добавляем последний накопленный сегмент при выходе
        if current_segment_text.strip():
            segments.append(current_segment_text.strip())
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
        
    print("\nСобранные сегменты:")
    for i, seg in enumerate(segments, 1):
        print(f"Сегмент {i}: {seg}")

    # Возвращаем список сегментов для дальнейшей обработки и отправки
    return segments

if __name__ == "__main__":
    offline_speech_recognition()
