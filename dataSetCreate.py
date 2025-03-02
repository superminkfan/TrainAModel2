import json
import re
import ollama


# Файл с входными данными
input_file = "faq.md"
output_file = "faq.json"

# Регулярные выражения для разделов
section_pattern = re.compile(r"^### (.+)", re.MULTILINE)
subsection_pattern = re.compile(r"^#### (.+)", re.MULTILINE)


# Функция для преобразования заголовка в осмысленный вопрос
# Используем русскоязычную модель
from transformers import pipeline

# Функция для генерации осмысленного вопроса с использованием Ollama (phi-4)
def format_question(title):
    prompt = f"Сформулируй краткий вопрос на основе темы: {title}"
    response = ollama.chat(model='phi4', messages=[
        {"role": "system", "content": "Ты помощник, который генерирует вопросы по заданной теме."},
        {"role": "user", "content": prompt}])
    question = response['message']['content'].strip()

    # Убираем лишние пробелы и символы
    question = re.sub(r'[^а-яА-ЯёЁ0-9 ,?]', '', question)

    return question if question.endswith('?') else question + '?'

# question_generator = pipeline("text-generation", model="ai-forever/rugpt3small_based_on_gpt2")
#
# def format_question(title):
#     prompt = f"Какой вопрос можно задать по теме: {title}?"
#     generated = question_generator(prompt, max_length=50, num_return_sequences=1)
#     question = generated[0]['generated_text'].strip()
#
#     # Убираем мусорные символы и пробелы
#     question = re.sub(r'[^а-яА-ЯёЁ0-9 ,?]', '', question)
#
#     return question if question.endswith('?') else question + '?'
# question_generator = pipeline("text2text-generation", model="facebook/bart-large-cnn")
#
# def format_question(title):
#     prompt = f"Создай вопрос, основываясь на заголовке: {title}"
#     generated = question_generator(prompt, max_length=50, truncation=True)
#     return generated[0]['generated_text']

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
    answer = "\n".join(part.strip() for part in answer_parts[1::2])

    faq_list.append({"question": format_question(title), "answer": answer})

# Записываем в JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(faq_list, f, ensure_ascii=False, indent=2)

print(f"JSON файл сохранен: {output_file}")