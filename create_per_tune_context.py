import json
import re

# Загружаем файл
file_path = "performance-tuning.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Разбиваем документ на строки
lines = content.split("\n")

# Обрабатываем документ и структурируем данные
structured_data = {}
current_section = None
current_subsection = None

for line in lines:
    # Обнаружение заголовков второго уровня (##)
    match_section = re.match(r"^##\s+(.+)", line)
    if match_section:
        current_section = match_section.group(1).strip()
        structured_data[current_section] = {}
        current_subsection = None
        continue

    # Обнаружение заголовков третьего уровня (###)
    match_subsection = re.match(r"^###\s+(.+)", line)
    if match_subsection and current_section:
        current_subsection = match_subsection.group(1).strip()
        structured_data[current_section][current_subsection] = []
        continue

    # Обнаружение заголовков четвертого уровня (####)
    match_subsubsection = re.match(r"^####\s+(.+)", line)
    if match_subsubsection and current_section and current_subsection:
        structured_data[current_section][current_subsection].append(match_subsubsection.group(1).strip())
        continue

# Сохранение в JSON
json_output_path = "performance-structured.json"
with open(json_output_path, "w", encoding="utf-8") as json_file:
    json.dump(structured_data, json_file, ensure_ascii=False, indent=4)

json_output_path
