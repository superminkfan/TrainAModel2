import json
import re
import ollama
import json
from deep_translator import GoogleTranslator

import sys
import time
import threading
import itertools

error_msg = "error in translation"

def animate():
    symbols = itertools.cycle("/|\\-")  # Циклическая смена символов
    while not stop_event.is_set():
        sys.stdout.write(f"\r[{next(symbols)}] Идет обработка... ")
        sys.stdout.flush()
        time.sleep(0.2)  # Интервал смены символов

# Флаг для остановки анимации
stop_event = threading.Event()

# Запускаем анимацию в отдельном потоке
animation_thread = threading.Thread(target=animate)
animation_thread.start()

# Файл с входными данными
input_file = "faq.md"
output_file = "faq_newStyle.json"

# Регулярные выражения для разделов
section_pattern = re.compile(r"^### (.+)", re.MULTILINE)
subsection_pattern = re.compile(r"^#### (.+)", re.MULTILINE)


#Функция говна на палке (с регуляркой)
def remove_code_block_markers(text):
    # Удаляем первую строку
    text = re.sub(r"^.*\n", "", text, count=1)
    # Удаляем последнюю строку (если есть `\n`, то просто удалится, иначе удалится ` ``` `)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()

# Функция разбиения текста на части фиксированного размера (5000 символов)
def split_text(text, max_length=4999):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Функция перевода текста с разбиением длинных текстов
def translate_to_english(text):
    try:
        chunks = split_text(text)
        translated_chunks = [GoogleTranslator(source='ru', target='en').translate(chunk) for chunk in chunks]
        return " ".join(translated_chunks)
    except:
        print("Error in translation!")
        return text

# Функция для генерации осмысленных вопросов (3 шт)
def generate_three_questions(text):
    system_prompt_for_question = (f"You are a helpful AI assistant. "
                                  f"Your task is to help a user understand how to use Apache Ignite. "
                                  f"Carefully examine the documentation snippet and generate 3 questions a medium to experienced Apache Ignite user could ask. "
                                  f"Questions must be answerable from the information in the snippet. "
                                  f"Do not assume anything about Apache Ignite that is not discussed in the snippet. "
                                  f"If the snippet is too short or contains too little information, output an empty string."
                                  f"Generate only questions as an array as text with no formating. Your response must be like this:"
                                  f"[question_1, question_2, question_3]")

    prompt = (f"Generate a clear and concise questions based on the topic: {text}."
              f"Do the output as python array.")
    if topic == error_msg:
        return error_msg

    #Должен возвращать список (посмотрим)
    return do_ollama_magic(prompt, system_prompt_for_question)

# Функция для генерации ответов
def generate_answer(topic, question):
    system_prompt_for_question = (f"You are a helpful AI assistant. "
                                  f"Your task is to help a user understand how to use Apache Ignite. "
                                  f"Carefully examine the documentation snippet and answer the question."
                                  f"Do not assume anything about Apache Ignite that is not discussed in the snippet. "
                                  f"If the snippet is too short or contains too little information, output an empty string.")

    prompt = (f"Generate a clear and concise answer based on the topic: {topic}."
              f"The question is: {question}")

    return do_ollama_magic(prompt, system_prompt_for_question)

#Функция генерации с помощью нейронки
def do_ollama_magic(prompt, system_prompt_for_question):
    response = ollama.chat(model='phi4', messages=[
        {"role": "system", "content": system_prompt_for_question},
        {"role": "user", "content": prompt}])

    return response['message']['content'].strip()


# Читаем файл
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# Разбиваем файл на разделы
sections = section_pattern.split(content)[1:]
faq_list = []

# for i in range(0, len(sections), 2):
count = 0
for i in range(0, len(sections), 2):
    print("==== Iteration " + str(count) + " ====")

    russian_title = sections[i].strip()
    text = sections[i + 1].strip()

    # Объединяем все подразделы в один ответ
    text_parts = subsection_pattern.split(text)[1:]
    russian_text = "\n".join(part.strip() for part in text_parts[1::2])

    try:
        topic = translate_to_english(text)
    except Exception as e:  # Ловит любые исключения:
        print("Error in translation!!! text = " + str(text))
        topic = error_msg

    try:
        generated_response = remove_code_block_markers(generate_three_questions(topic))
        questions_array = json.loads(generated_response)

        print(questions_array)

        for question in questions_array:
            print("Question = " + question)

            answer = generate_answer(topic, question)

            print()
            print("Answer = " + answer)

            faq_list.append({"prompt": question, "response": answer})
    except Exception as e:
        print(f"Another exception! {e} \nquestions_array = " + str(questions_array))
        pass


    print("==== Iteration " + str(count) + " completed ====")
    count += 1

# Записываем в JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(faq_list, f, ensure_ascii=False, indent=2)

print(f"JSON файл сохранен: {output_file}")



# Останавливаем анимацию
stop_event.set()
animation_thread.join()

# Очищаем строку анимации
sys.stdout.write("\rГотово!            \n")
sys.stdout.flush()