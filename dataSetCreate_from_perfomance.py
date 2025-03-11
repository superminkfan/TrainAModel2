import re

import ollama
import translators as ts
import json

from openai import OpenAI

error_msg = "error in translation"

#Функция говна на палке (с регуляркой)
def remove_code_block_markers(text):
    # Удаляем первую строку
    text = re.sub(r"^.*\n", "", text, count=1)
    # Удаляем последнюю строку (если есть `\n`, то просто удалится, иначе удалится ` ``` `)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()

#Функция разбиения текста на части фиксированного размера (5000 символов)
def split_text(text, max_length=5000):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Разбиваем по точке, восклицательному или вопросительному знаку + пробел
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:  # +1 для пробела
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())  # Сохраняем накопленный кусок
            current_chunk = sentence  # Начинаем новый кусок

    if current_chunk:
        chunks.append(current_chunk.strip())  # Добавляем последний кусок

    return chunks


# Функция перевода текста с разбиением длинных текстов
def translate_to_english(text):
    chunks = split_text(text)
    translated_chunks = [ts.translate_text(chunk, 'google', 'auto', 'en') for chunk in chunks]

    return " ".join(translated_chunks)


#Функция генерации с помощью нейронки
def do_ollama_magic(prompt, system_prompt_for_question):
    response = ollama.chat(model='phi4', messages=[
        {"role": "system", "content": system_prompt_for_question},
        {"role": "user", "content": prompt}])
    res = response['message']['content'].strip()
    print("+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print("Ollama response:")
    print(res)
    print("+=+=+=+=+=+=+=+=+=+=+=+=+=END+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    return res

def do_chatgpt_magic(prompt, system_prompt_for_question):
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": system_prompt_for_question},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    res = completion.choices[0].message
    print("+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    print("ChatGPT response:")
    print(res)
    print()
    print("+=+=+=+=+=+=+=+=+=+=+=+=+=END+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    return res

# Функция для генерации осмысленных вопросов (5 шт)
def generate_five_questions(title, text):
    # system_prompt_for_question = (f"You are a helpful AI assistant. "
    #                               f"Your task is to help a user understand how to use DataGrid (fork of Apache Ignite). "
    #                               f"You are given a snippet of documentation and a short title to it. "
    #                               f"Carefully examine the documentation snippet and generate 5 questions a medium to experienced DataGrid user could ask. "
    #                               f"Questions must be answerable from the information in the snippet. "
    #                               f"Do not assume anything about DataGrid that is not discussed in the snippet. "
    #                               f"If the snippet is too short or contains too little information, generate 1 question. ")

    system_prompt_for_question = (f"You are a helpful AI assistant. "
                                  f"Your task is to help a user understand how to use DataGrid (fork of Apache Ignite).  "
                                  f"You are given a snippet of documentation and a short title.  "
                                  f"Carefully examine the documentation snippet and generate exactly 7 distinct and meaningful questions that an intermediate or experienced DataGrid user could ask.  "
                                  f"Your questions must be strictly answerable from the given information — do not assume anything that is not explicitly stated.  "
                                  f"If the snippet is too short or contains insufficient information, generate exactly 3 question instead of 7.  "
                                  f"Always follow the requested format. ")

    # prompt = (f"Generate questions based on the topic. Do the output as python array ONLY. "
    #           f"Your response must be like this:"
    #           f"[question_1, question_2, question_3, question_4, question_5]. "
    #           f"Title of the topic is {title}. Topic:\n {text}.")
    prompt = (f"Analyze the provided topic and generate questions based strictly on its content.  "
              f"Your response must be strictly a valid Python list with exactly 7 questions (or 3 if the content is too short).  "
              f"Format your response as follows:  "
              f"```python"
              f"[question_1, question_2, question_3, question_4, question_5]. "
              f"Do not add explanations, summaries, or any other text."
              f"Title: {title}."
              f"Topic: {text}.")

    return do_ollama_magic(prompt, system_prompt_for_question)
    # return do_chatgpt_magic(prompt,system_prompt_for_question)

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
    # return do_chatgpt_magic(prompt,system_prompt_for_question)



error_count = 0

# Загружаем файл
file_path = "performance-tuning.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Разбиваем документ на строки
lines = content.split("\n")

# Обрабатываем документ
structured_data = {}
current_section = None
faq_list = []
output_file = "performance-tuning_qa.json"
section_text = []

for line in lines:
    # Обнаружение заголовков второго уровня (##)
    match_section = re.match(r"^##\s+(.+)", line)
    if match_section:
        if current_section:
            structured_data[current_section] = "\n".join(section_text).strip()
        current_section = match_section.group(1).strip("# ")  # Убираем #
        section_text = [current_section]  # Начинаем новый раздел
        continue

    # Добавляем все строки в текущий раздел
    if current_section is not None:
        section_text.append(line.strip("# "))  # Убираем # в подзаголовках

# Добавляем последний обработанный раздел
if current_section and section_text:
    structured_data[current_section] = "\n".join(section_text).strip()

for i, (section, topic) in enumerate(structured_data.items()):
    if i == 0:
        print("continue iter = " + str(i))
        continue
    if i == 4:
        print("Breaking operation on iter = " + str(i))
        break

    print(f"=== {section} ===")
    english_topic = translate_to_english(topic)
    english_section = translate_to_english(section)

    print(english_topic)
    print("+++++++++++++++++++++++++++++++++++++++")

    # questions = generate_five_questions(english_section, english_topic)

    # try:
    #     fine_questions = json.loads(remove_code_block_markers(questions))
    # except json.JSONDecodeError:
    #     print("Ошибка: модель вернула некорректный JSON")
    #     error_count += 1
    #     fine_questions = []
    #
    # print(fine_questions)
    #
    # for question in fine_questions:
    #     print(question)
    #     answer = generate_answer(english_topic, question)
    #
    #     faq_list.append({"prompt": question, "response": answer})
    #
    #     # Записываем JSON **на каждой итерации**
    #     with open(output_file, "w", encoding="utf-8") as f:
    #         json.dump(faq_list, f, ensure_ascii=False, indent=2)

    print("Error_count = " + str(error_count))





