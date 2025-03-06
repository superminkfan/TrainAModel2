import re
import ollama
import translators as ts
import json

error_msg = "error in translation"

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
    chunks = split_text(text)
    # translated_chunks = [GoogleTranslator(source='ru', target='en').translate(chunk) for chunk in chunks]
    translated_chunks = [ts.translate_text(chunk, 'google', 'auto', 'en') for chunk in chunks]

    #return translated_chunks
    return " ".join(translated_chunks)


#Функция генерации с помощью нейронки
def do_ollama_magic(prompt, system_prompt_for_question):
    response = ollama.chat(model='phi4', messages=[
        {"role": "system", "content": system_prompt_for_question},
        {"role": "user", "content": prompt}])
    responsss = response['message']['content'].strip()
    return responsss

# Функция для генерации осмысленных вопросов (5 шт)
def generate_five_questions(title, text):
    system_prompt_for_question = (f"You are a helpful AI assistant. "
                                  f"Your task is to help a user understand how to use DataGrid (fork of Apache Ignite). "
                                  f"You are given a snippet of documentation and a short title to it. "
                                  f"Carefully examine the documentation snippet and generate 5 questions a medium to experienced DataGrid user could ask. "
                                  f"Questions must be answerable from the information in the snippet. "
                                  f"Do not assume anything about DataGrid that is not discussed in the snippet. "
                                  f"If the snippet is too short or contains too little information, generate 1 question"
                                  f"Generate only questions as an array. Your response must be like this:"
                                  f"[question_1, question_2, question_3, question_4, question_5]")

    prompt = (f"Generate a clear and concise questions based on the topic. Title of the topic is {title}. Topic:\n {text}."
              f"Do the output as python array.")

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

print(type(structured_data))

for i, (section, topic) in enumerate(structured_data.items()):
    if i == 0:
        continue  # Пропускаем первую итерацию (потому что она готова)

    print(f"=== {section} ===")
    english_topic = translate_to_english(topic)
    english_section = translate_to_english(section)

    print(english_section)
    print(english_topic)

    questions = generate_five_questions(english_section, english_topic)

    print(questions)

    fine_questions = json.loads(remove_code_block_markers(questions))

    print(fine_questions)

    for question in fine_questions:
        print(question)
        answer = generate_answer(english_topic, question)

        faq_list.append({"prompt": question, "response": answer})

        # Записываем JSON **на каждой итерации**
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(faq_list, f, ensure_ascii=False, indent=2)





