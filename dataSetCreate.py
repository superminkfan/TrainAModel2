import json
import re
import ollama
from deep_translator import GoogleTranslator

# Файл с входными данными
input_file = "faq.md"
output_file = "faq.json"

# Регулярные выражения для разделов
section_pattern = re.compile(r"^### (.+)", re.MULTILINE)
subsection_pattern = re.compile(r"^#### (.+)", re.MULTILINE)

# # Функция разбиения длинного текста на части (chunks)
def split_text_chunks(text, max_length=5000):
    chunks = []
    while len(text) > max_length:
        split_index = text.rfind(". ", 0, max_length)  # Разбиваем по ближайшему предложению
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index + 1])
        text = text[split_index + 1:].strip()
    chunks.append(text)
    return chunks

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

# Функция для генерации осмысленного вопроса с использованием Ollama (phi-4)
def format_question(title):
    english_title = translate_to_english(title)
    system_prompt = f"You generate meaningful questions based on given topics."

    #system_prompt_for_question = f"You are a helpful AI assistant.
    # Your task is to help a user understand how to use functions and classes from Apple's Deep Learning framework, MLX.
    # Carefully examine the function documentation snippet and generate 3 questions a medium to experienced MLX user could ask.
    # Questions must be answerable from the information in the snippet.
    # Do not assume anything about MLX's API that is not discussed in the snippet.
    # If the snippet is too short or contains too little information, output an empty JSON array."

    #system_prompt_for_answer = "You are a helpful AI assistant.
    # Your task is to help a user understand how to use functions and classes from Apple's Deep Learning framework, MLX.
    # Carefully examine the function documentation and generate an explanatory response based on the user's question which showcases usage and examples.
    # Do not assume anything about MLX's API that is not discussed in the reference documentation snippet."


    prompt = f"Generate a clear and concise question based on the topic: {english_title}"
    response = ollama.chat(model='phi4', messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}])
    question = response['message']['content'].strip()

    return question if question.endswith('?') else question + '?'

# Читаем файл
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# Разбиваем файл на разделы
sections = section_pattern.split(content)[1:]
faq_list = []

for i in range(0, len(sections), 2):
    title = sections[i].strip()
    text = sections[i + 1].strip()

    # Объединяем все подразделы в один ответ
    answer_parts = subsection_pattern.split(text)[1:]
    russian_title = "\n".join(part.strip() for part in answer_parts[1::2])

    question = format_question(title)
    answer = translate_to_english(russian_title)

    print("==== Iteration " + str(i) + " ====")
    print(russian_title)
    print(question)
    print(answer)

    faq_list.append({"prompt": question, "response": answer})

# Записываем в JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(faq_list, f, ensure_ascii=False, indent=2)

print(f"JSON файл сохранен: {output_file}")