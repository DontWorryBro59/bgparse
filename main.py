import json
import os
import time

from datetime import datetime as dt


from database.database_init import DatabaseRepository, db_url
from database.models import ProductModels
from parser.parse import start_parse

time_to_sleep = os.getenv('TIME_TO_SLEEP') or 200
time_to_sleep = int(time_to_sleep)



def add_items_with_file_to_db() -> None:
    """Добавление товаров с ценами в базу данных"""
    print('*' * 100)
    print('Adding items with prices to the database has started /'
          ' Добавление товаров с ценами в базу данных началось')
    start_time = dt.now()
    # Создаем базу данных и таблицы
    repo = DatabaseRepository(url=db_url)
    session = repo.get_session()
    # Получаем данные из файла и сохраняем их в базу данных
    with open('parser/file/catalog.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    try:
        for category in data:
            for sub_category in category['sub_dirs']:
                for items in sub_category['items']:
                    for item in items['items']:
                        new_item = ProductModels(
                            product_name=category['rus_name'],
                            category_name=sub_category['rus_name'],
                            item_name=item['item_name'],
                            price=item['price'],
                            density=item['params']['density'],
                            size=item['params']['size'],
                            quantity=item['params']['quantity']
                        )
                        session.add(new_item)
    except Exception as ex:
        print(f'An error occurred while adding items to the database: {ex}')
    finally:
        # Перезаписываем базу данных если все прошло успешно
        print('Deleting all tables / Удаление всех таблиц')
        repo.drop_tables()
        print('Creating tables / Создание таблиц')
        repo.create_tables()
        session.commit()
    end_time = dt.now()
    print(f'The operation was completed successfully, time: {end_time - start_time} / '
          f'Операция выполнена успешно, время: {end_time - start_time}')


if __name__ == '__main__':
    while True:
        # Парсим данные и сохраняем их в файл
        start_parse()
        # Получаем данные из файла и сохраняем их в базу данных
        add_items_with_file_to_db()
        # Засыпаем
        print(f'Waiting for {time_to_sleep} seconds / Ждем {time_to_sleep} секунд')
        time.sleep(time_to_sleep)
