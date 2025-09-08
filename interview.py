import asyncio
import os
from voice import recognize_speech_segment
from langchain_gigachat import GigaChat
from dotenv import load_dotenv
#import requests
#import base64
import simpleaudio as sa
import urllib3
#import uuid
#import wave
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
API_KEY = os.getenv("GIGACHAT_API_KEY")
YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")
if not API_KEY:
  raise ValueError("Отсутствует ключ GIGACHAT_API_KEY в .env")
elif not YANDEX_TOKEN:
  raise ValueError("Отсутствует ключ CLIENT_IDs в .env")

EXTENDED_SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Ты – виртуальный HR-ассистент, ведущий собеседование на вакансию Python-разработчика. Твоя задача — проводить интервью профессионально, вежливо и эффективно, сохраняя доброжелательный тон.

Основные правила:
- Первые три вопроса — фиксированные вводные, не отвечай на них, а только слушай и запоминай.
- После трёх ответов начинай задавать вопросы, адаптируясь под полученные ответы.
- Если кандидат уклоняется от ответа или говорит много без сути, мягко возвращай к теме: "Спасибо за развернутый ответ. А теперь расскажите подробнее о..."
- Если кандидат долго думает или испытывает стресс, используй фразы снижающие напряжение: "Не торопитесь, возьмите время для ответа", "Это сложный вопрос, не переживайте, расскажите, что знаете".
- При ответах "не знаю" или "не могу ответить" поддерживай кандидата и направляй тактично: "Понимаю, такой опыт может быть редким, расскажите про что-то похожее, с чем сталкивались".
- Политика, семейное положение и религиозные темы — не поднимай, вопросы и обсуждения на эти темы запрещены.
- При использовании мата — сначала предупреди: "Пожалуйста, избегайте нецензурной лексики, чтобы сохранить дружелюбную атмосферу". Если продолжается — корректно заверши диалог.
- Если кандидат напрямую выражает желание закончить собеседование, либо при критических случаях (мат, агрессия) — завершай диалог с вежливым прощанием.
- Старайся реагировать быстро, в идеале не более чем за 5 секунд после ответа.
- Внимательно улавливай нюансы в речи, чтобы лучше адаптировать вопросы и поддержку.

Примеры поведения:

1. Кандидат долго думает:
- "Не торопитесь, я понимаю, что вопрос сложный."
- "Можете рассказать то, что приходит в голову, это поможет понять ваш уровень."

2. Кандидат говорит уклончиво:
- "Спасибо за мысль, а теперь пожалуйста расскажите подробнее про конкретный опыт."

3. Кандидат отвечает "не знаю":
- "Такое часто встречается. Можете ли вы привести похожий пример из практики?"

4. Кандидат использует мат:
- "Пожалуйста, избегайте нецензурной лексики."
- Если продолжается — "К сожалению, нам придется завершить собеседование. Спасибо за понимание."

5. Кандидат хочет завершить:
- "Понимаю, если вы хотите прервать разговор, мы можем продолжить в другой раз. Спасибо за уделенное время."

Ведите собеседование живо, уважительно и профессионально, помогайте кандидату раскрыть свои возможности.
"""
}

#Sysrem promt
SYSTEM_PROMPT = {
  "role": "system",
  "content": (
      "Ты ИИ HR, тебе нужно провести собеседование на вакансию Python разработчика. "
      "Первые 3 ответа — вводные, не отвечай на них. "
      "После — задавай по одному вопросу, оценивай ответы, максимум 10-12 вопросов."
  )
}

INITIAL_QUESTIONS = [
    "Где вы работали и чем занимались?",
    "Расскажите о своем опыте с библиотекой pandas.",
    "Какой уровень знания SQL у вас и как часто вы им пользуетесь?"
]

llm = GigaChat(
  credentials=API_KEY,
  model="GigaChat-Pro",
  top_p=0,
  timeout=120,
  verify_ssl_certs=False
)
"""
def tts_yandex(text, voice="lera", format="lpcm", sample_rate_hz=48000):
    
    #text : str - текст для озвучивания
    #voice: str - голос, например 'lera', 'alena'
    #format: str - формат аудио ('lpcm' или 'ogg')
    #sample_rate_hz: int - частота дискретизации
    
    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    
    headers = {
        "Authorization": f"Bearer {YANDEX_TOKEN}"
    }
    
    data = {
        "text": text,
        "voice": voice,
        "format": format,
        "sampleRateHertz": sample_rate_hz,
        "speed": 1.0
    }
    
    response = requests.post(url, headers=headers, data=data)  # <- тут data, а не json
    response.raise_for_status()
    audio_content = response.content

    # Воспроизведение LPCM через simpleaudio
    if format == "lpcm":
        wave_obj = sa.WaveObject(audio_content, num_channels=1, bytes_per_sample=2, sample_rate=sample_rate_hz)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    else:
        with open("output.ogg", "wb") as f:
            f.write(audio_content)
        print("Аудио сохранено в output.ogg")
"""
async def send_to_gigachat(messages):
  #Асинхронный вызов модели с передачей списка сообщений(проверяем синхронный без await)
  response = llm.invoke(messages)
  # respone имеет поле content с текстом ответа
  return response.content

# Функция синтеза и воспроизведения речи с SaluteSpeech
"""def tts_salute(text, token):
    url = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        "text": text,
        "voice": "Ost_24000",  # Александра 24кГЦ
        "format": "wav"
    }
    response = requests.post(url, json=payload, headers=headers,verify=False)
    response.raise_for_status()
    audio_base64 = response.json().get("payload", {}).get("audio", "")
    if not audio_base64:
      raise ValueError("Не удалось получить аудио из ответа SaluteSpeech")
    
    audio_data = base64.b64decode(audio_base64)
    wave_obj = sa.WaveObject(audio_data, 1, 2, 48000)
    play_obj = wave_obj.play()
    play_obj.wait_done()
"""
async def interview_flow():
  messages = [SYSTEM_PROMPT]
  
  # 1. Задаем фиксированные вопросы и принимаем ответы
  for i, question in enumerate(INITIAL_QUESTIONS):
      print(f"Вопрос #{i+1}: {question}")
      messages.append({"role": "assistant", "content": question})
      #tts_yandex(question, voice="lera") #Озвучиваем фиксированный вопрос
      print(f"Ожидание ответа на вопрос #{i+1} (или 'q' для выхода)...")
      
      answer = recognize_speech_segment()  # <- получаем ответ
      if not answer:
        answer = ""  # если распознавание вернуло None
      
      if answer.lower() in ["q", "exit"]:
          print("Кандидат досрочно завершил собеседование.")
          messages.append({"role": "user", "content": "[досрочное завершение]"})
          break
      messages.append({"role": "user", "content": answer})

  questions_asked = len(INITIAL_QUESTIONS)
  max_questions = 12  # всего вопросов (фиксированных + адаптивных)

    # 2. Задаем вопросы от ИИ, адаптируя их под ответы
  while questions_asked < max_questions:
      print(f"Ожидание очередного вопроса №{questions_asked + 1} от ИИ...")
      
      ai_question = await send_to_gigachat(messages)
      print(f"ИИ спрашивает: {ai_question}")
      messages.append({"role": "assistant", "content": ai_question})
      #tts_yandex(ai_question, voice="lera")# Вызов озвучивания вопроса нейросети
      print(f"Ожидание ответа на вопрос №{questions_asked + 1}...")
      answer = recognize_speech_segment()
      if not answer:
        answer = ""  # если распознавание вернуло None
      
      if answer.lower() in ["q", "exit"]:
          print("Кандидат досрочно завершил собеседование.")
          messages.append({"role": "user", "content": "[досрочное завершение]"})
          break

      # Отправляем ответ кандидата + предыдущие сообщения на проверку мата в нейросеть
      check_prompt = [
          {"role": "system", "content": "Проверяй ответы кандидата на нецензурную лексику."},
          {"role": "user", "content": answer}]
      result = await send_to_gigachat(check_prompt)
      # Если нейросеть вернула команду бан — прерываем собеседование
      if "[бан_за_мат]" in result:
          print("Кандидат использовал нецензурную лексику. Собеседование завершено.")
          messages.append({"role": "assistant", "content": result})
          break

      print(f"Ответ кандидата: {answer}")
      messages.append({"role": "user", "content": answer})
      questions_asked += 1

      
  # 3. Генерация итогового отчета
  report_prompt = [
      SYSTEM_PROMPT,  # system message должен быть первым
      {"role": "user", "content": "На основе всей истории собеседования составь итоговый отчет в формате JSON. "
                                "Выдели сильные стороны, навыки для улучшения, замечания (например, мат). "
                                "Выведи JSON, например: "
                                "{'candidate':'Имя','strengths':[],'improvements':[],'warnings':[]}"},
      {"role": "user", "content": json.dumps(messages)}  # передаем всю историю собеседования
  ]

  final_report_text = await send_to_gigachat(report_prompt)

  # Преобразуем текст отчета в JSON и сохраняем
  try:
      report_json = json.loads(final_report_text)
  except json.JSONDecodeError:
      report_json = {"candidate": "Не указано", "interview_report": final_report_text}

  report_filename = os.path.join(os.getcwd(), "interview_report.json")
  with open(report_filename, "w", encoding="utf-8") as f:
      json.dump(report_json, f, ensure_ascii=False, indent=4)

  print(f"Отчет сохранен в {report_filename}")


if __name__ == "__main__":
    asyncio.run(interview_flow())
