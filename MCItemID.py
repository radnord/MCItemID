import os
import json
import zipfile
import re
from pathlib import Path

def extract_item_data_from_jar(minecraft_version_path):
    """Извлекает ID предметов и их английские названия из JAR-файла Minecraft."""
    
    # Находим JAR-файл в папке версии
    jar_files = [f for f in os.listdir(minecraft_version_path) if f.endswith(".jar")]
    if not jar_files:
        raise FileNotFoundError(f"JAR-файл не найден в папке {minecraft_version_path}")
    
    jar_path = os.path.join(minecraft_version_path, jar_files[0])
    print(f"Обрабатываю JAR-файл: {jar_path}")
    
    # Словари для хранения данных о предметах
    item_ids = set()
    item_en_names = {}
    
    # Открываем JAR как ZIP-архив
    with zipfile.ZipFile(jar_path, 'r') as jar:
        # Ищем файлы с моделями предметов
        item_model_files = [name for name in jar.namelist() if name.startswith('assets/minecraft/models/item/')]
        
        # Получаем английские названия из файла локализации, если есть
        en_lang_path = 'assets/minecraft/lang/en_us.json'
        en_lang_data = {}
        
        if en_lang_path in jar.namelist():
            try:
                with jar.open(en_lang_path) as f:
                    en_lang_data = json.load(f)
            except:
                print("Не удалось загрузить файл локализации en_us.json")
        
        # Извлекаем ID предметов из файлов моделей
        for model_file in item_model_files:
            # Извлекаем имя предмета из пути файла
            item_name = model_file.replace('assets/minecraft/models/item/', '').replace('.json', '')
            item_id = f"minecraft:{item_name}"
            item_ids.add(item_id)
            
            # Добавляем человеко-читаемое название по умолчанию
            readable_name = item_name.replace('_', ' ').title()
            item_en_names[item_id] = readable_name
            
            # Пытаемся найти официальное название в файле локализации
            lang_key = f"item.minecraft.{item_name}"
            if lang_key in en_lang_data:
                item_en_names[item_id] = en_lang_data[lang_key]
        
        # Ищем другие ID предметов в рецептах и блоках
        for prefix in ['data/minecraft/recipes/', 'assets/minecraft/models/block/']:
            files = [name for name in jar.namelist() if name.startswith(prefix)]
            for file_path in files:
                try:
                    # Извлекаем имя из пути
                    if prefix == 'data/minecraft/recipes/':
                        item_name = file_path.replace(prefix, '').replace('.json', '')
                        item_id = f"minecraft:{item_name}"
                    else:
                        item_name = file_path.replace('assets/minecraft/models/block/', '').replace('.json', '')
                        item_id = f"minecraft:{item_name}"
                    
                    item_ids.add(item_id)
                    
                    # Если названия еще нет, добавляем стандартное
                    if item_id not in item_en_names:
                        readable_name = item_name.replace('_', ' ').title()
                        item_en_names[item_id] = readable_name
                        
                        # Пытаемся найти в файле локализации
                        block_key = f"block.minecraft.{item_name}"
                        if block_key in en_lang_data:
                            item_en_names[item_id] = en_lang_data[block_key]
                except Exception as e:
                    continue
    
    # Объединяем все данные в один список словарей
    item_data = []
    for item_id in sorted(item_ids):
        # Используем ID предмета как запасной вариант если нет названия
        default_name = item_id.split(':')[1].replace('_', ' ').title()
        
        item_data.append({
            'id': item_id,
            'en_name': item_en_names.get(item_id, default_name)
        })
    
    return item_data

def save_item_data_to_txt(item_data, output_file):
    """Сохраняет данные о предметах в текстовый файл в виде таблицы."""
    
    # Определяем максимальную длину для каждой колонки
    max_id_len = max([len(item['id']) for item in item_data] or [10]) + 2
    max_en_len = max([len(item['en_name']) for item in item_data] or [20]) + 2
    
    # Форматируем заголовок и разделитель
    header = f"{'ID':{max_id_len}} | {'Английское название':{max_en_len}}"
    separator = "-" * max_id_len + "-+-" + "-" * max_en_len
    
    # Записываем данные в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header + "\n")
        f.write(separator + "\n")
        
        for item in item_data:
            line = f"{item['id']:{max_id_len}} | {item['en_name']:{max_en_len}}"
            f.write(line + "\n")

def main():
    # Получаем путь к папке версии от пользователя
    minecraft_version_path = input("Введите путь к папке версии Minecraft (например, C:\\Users\\username\\AppData\\Roaming\\.minecraft\\versions\\1.21.5): ")
    
    if not os.path.exists(minecraft_version_path):
        print(f"Ошибка: Папка {minecraft_version_path} не существует.")
        return
    
    # Определяем путь для выходного файла
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minecraft_items.txt")
    
    try:
        print(f"Извлекаю данные о предметах из {minecraft_version_path}...")
        item_data = extract_item_data_from_jar(minecraft_version_path)
        
        print(f"Найдено {len(item_data)} предметов.")
        
        print(f"Сохраняю данные в файл {output_file}...")
        save_item_data_to_txt(item_data, output_file)
        
        print("\nГотово! Таблица с данными о предметах создана.")
        print(f"Расположение файла: {output_file}")
    except Exception as e:
        print(f"Ошибка при обработке: {e}")

if __name__ == "__main__":
    main()
