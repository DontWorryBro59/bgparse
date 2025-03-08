import json
import os
import re
from datetime import datetime as dt

import requests
from bs4 import BeautifulSoup

# Constants
URL_CATALOG = 'https://www.bereg.net/catalog'
FILE_PATH = 'file/catalog.json'

USER_AGENT = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537'}

COOKIES = {'nbid': '10',  # Город Пермь
           'WPHSSID': 'e30bac1f86f6e5427411846bd7c81fed'
           }
DATABASE_URI = 'sqlite:///db/db.sqlite3'


def create_file(user_dict: list[dict]) -> None:
    """
    This function creates directories and json files
    Эта функция создает директории и json файлы
    """
    print('*' * 100)
    print(f'Create files directory has started / Создаем директории')
    # Получаем директорию файла
    directory = os.path.dirname(FILE_PATH)
    # Если директории нет, создаем ее
    if not os.path.exists(directory):
        os.makedirs(directory)

    print(f'Create json file has started / Создаем json файл')
    # Создаем файл если его нет, записываем данные для первичного парсинга
    with open(FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(user_dict, file, indent=4, ensure_ascii=False)
    print(f'Json file has been created! / Json файл создан / path = {FILE_PATH}')


# Функция для получения списка категорий
def get_catalog() -> list:
    """
    This function returns a 'wet' list of categories
    Эта функция возвращает 'грязный' список категорий
    """
    print('*' * 100)
    print(f'Get nav links from page {URL_CATALOG} has started / Получаем "грязный" список категорий')
    catalog = requests.get(URL_CATALOG, cookies=COOKIES, headers=USER_AGENT)
    soup = BeautifulSoup(catalog.text, 'html.parser')
    category_menu_wet = soup.find('div', class_="category_menu")
    all_categories = category_menu_wet.find_all('a', class_="nav-link")
    print('Wet list of categories has been created! / "Грязный" список категорий получен')
    return all_categories


def get_clear_data(all_categories: list) -> list[dict]:
    """
    This function returns a 'clear' list of categories in the format of a dictionary in a list
    Эта функция возвращает 'чистый' список категорий в формате словаря в списке
    """
    print('*' * 100)
    print('Clear list of categories has started! / Получаем "чистый" список категорий')
    category_list = []
    for el in all_categories:
        rus_name = el.text
        current_element = str(el)
        # Убираем ненужно ссылку которая ведет на форму поиска
        if 'qsearch' in current_element:
            continue
        # Регулярным выражением получаем данные между ковычками (в данном случае это ссылка)
        url = "https://www.bereg.net" + (re.findall(r'"(.*?)"', current_element))[1]
        to_add = {'rus_name': rus_name, 'url': url}
        category_list.append(to_add)
    print('Clear list of categories has been created! / "Чистый" список категорий получен')
    return category_list


def get_sub_directories(clr_catalog: list[dict]) -> list:
    """
    This function improve subdirectories to the category dictionary
    Эта функция расширяет доступ к подкаталогам словаря категорий
    """
    print('*' * 100)
    print('Improve subdirectories to the category dictionary has started! / Добавляем подкаталоги к категориям')
    for index, el in enumerate(clr_catalog):
        print(
            f'Adding subdirectories to category [{el["rus_name"]}] [{index + 1}/{len(clr_catalog)}]')
        sub_dirs = []
        url = el['url']
        response = requests.get(url, cookies=COOKIES, headers=USER_AGENT)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup = soup.find('li', class_='nav-item current')
        soup = soup.find('ul', class_='nav flex-md-column wSelHelper text-left')
        wet_sub_dirs = soup.find_all('a', class_='nav-link')
        for dir_el in wet_sub_dirs:
            rus_name = dir_el.text
            dir_el = str(dir_el)
            url = "https://www.bereg.net" + (re.findall(r'"(.*?)"', dir_el))[1]
            to_add = {'rus_name': rus_name, 'url': url}
            sub_dirs.append(to_add)
        el['sub_dirs'] = sub_dirs
    print(f'Processing completed! / Обработка завершена!')
    return clr_catalog


def found_items_instock(ctg_with_subdirs: list[dict]):
    """
    This function finds subdirectories to the category
    Эта функция находит субкаталоги для каждой категории
    """
    print('*' * 100)
    print(
        'Finding url for all subcategories has started! / Добавляем ссылки на товары в наличии по каждому подкаталогу')
    count = 0
    for index, el in enumerate(ctg_with_subdirs):
        print(f'Finding url for subcategory to category [{el['rus_name']}] [{index + 1}/{len(ctg_with_subdirs)}]')
        for sub_dir_el in el['sub_dirs']:
            request = requests.get(sub_dir_el['url'], cookies=COOKIES, headers=USER_AGENT)
            soup = BeautifulSoup(request.text, 'html.parser')
            soup = soup.find('div', class_='row no-gutters text-center')
            all_items_in_subdir = soup.find_all('div', class_='wMarkSet')
            url_for_items = []
            for soup_el in all_items_in_subdir:
                # Проверяем наличие товара на складе
                check_item = soup_el.find('div', class_='wMaCount wMaCountYes')
                if not check_item:
                    continue
                # Получим блок товара с нужными данными
                all_a = soup_el.find('a')
                # Получаем ссылку на товар
                url = all_a['href']
                full_url = 'https://www.bereg.net' + url
                # Получаем название товара
                title = all_a.find('div', class_='wMTitle').text.split()[:-2]
                title = ' '.join(title)
                # print(title)
                result = {'item_name': title, 'url': full_url}
                url_for_items.append(result)
                count += 1
            sub_dir_el['items'] = url_for_items
    print(f'Processing completed! / Обработка завершена!')
    print(f'Found {count} items in subcategories! / Найдено {count} товаров в субкатегориях!')
    return ctg_with_subdirs


def delete_out_of_stock_items(user_dict: list[dict]) -> list[dict]:
    """
    This function deletes items that are out of stock
    Эта функция удаляет товары, которых нет на складе
    """
    print('*' * 100)
    print('Processing items in stock has started! / Удаляем товары которых нет на складе')
    count = 0
    for index, el in enumerate(user_dict):
        print(
            f'Delete subcategories in [{user_dict[index]['rus_name']}]')
        new_sub_dir = []
        for sub_dir_el in el['sub_dirs']:
            if sub_dir_el['items']:
                new_sub_dir.append(sub_dir_el)
            else:
                count += 1
        el['sub_dirs'] = new_sub_dir
    print(f'Processing completed! / Обработка завершена!')
    print(f'Deleted {count} subcategories! / Удалено {count} субкатегорий!')
    return user_dict


def get_items(url: str) -> (list[dict], int):
    """
    This function searches for items in stock and adds them to the subcategory dictionary
    Эта функция ищет товары в наличии и добавляет их в словарь подкатегории
    """
    items = []
    count = 0
    request = requests.get(url, cookies=COOKIES, headers=USER_AGENT)
    soup = BeautifulSoup(request.text, 'html.parser')
    soup = soup.find('div', class_='col-12 table_order wRealOffers')
    soup = soup.find_all('div', attrs={
        'class': ['row', 'no-gutters', 'text-right', 'wPRow', 'wPRC_2', 'wP_c-2', 'wP_sc-49', 'wPRSC_49',
                  'wProdAvail']})
    for el in soup:
        if el['class'][-1] == 'wProdAvail':
            # Получаем название, цену и параметры товара
            name = el.attrs['data-mname']
            price = el.attrs['data-price']
            params = el.find('small').text.strip().split(', ')
            # Переводим параметры ['Плотность: 120', 'Размер: 64x90', 'Кол-во: Лист'] в словарь
            params_to_dict = {'density': params[0].split()[1], 'size': params[1].split()[1],
                              'quantity': params[2].split()[1]}
            items.append({'item_name': name, 'price': price, 'params': params_to_dict})
            count += 1
        elif el['class'][-1] == 'wProdAvailNot':
            # Как только натыкаемся на товар который не в наличии, выходим из цикла (все остальные товары не в наличии)
            break
    return items, count


def add_items_with_price(it_with_price: list[dict]) -> list[dict]:
    """
    This function adds items to the subdirectory dictionary
    Эта функция добавляет товары в словарь подкаталога
    """
    print('*' * 100)
    print('Adding items to subdirectory dictionary has started! / Добавляем товары в словарь подкаталога')
    quantity_items = 0
    for el in it_with_price:
        print(f'Adding items to subdirectory [{el['rus_name']}]', end=' ')
        quantity_items_to_subdir = 0
        for sub_dir in el['sub_dirs']:
            for item in sub_dir['items']:
                result = get_items(item['url'])
                item['items'] = result[0]
                quantity_items_to_subdir += result[1]
        print(f'[{quantity_items_to_subdir}]')
        quantity_items += quantity_items_to_subdir
    print(f'Processing completed! / Обработка завершена!')
    print(f'Found {quantity_items} items in subcategories! / Найдено {quantity_items} товаров в субкатегориях!')
    print(f'Processing completed! / Обработка завершена!')
    return it_with_price


def start_parse() -> None:
    time_start = dt.now()

    # Получаем 'грязный' список категорий
    wet_catalog = get_catalog()

    # Получаем 'чистый' список категорий
    clear_catalog = get_clear_data(wet_catalog)

    # Добавляем подкаталоги к категориям
    catalog_with_subdirs = get_sub_directories(clear_catalog)

    # Добавляем ссылки на товары в наличии по каждому подкаталогу
    fii = found_items_instock(catalog_with_subdirs)

    # Удаляем товары которых нет на складе
    fii_deleted = delete_out_of_stock_items(fii)

    # Получаем список товаров с ценами (товары в наличии)
    items_with_price = add_items_with_price(fii_deleted)

    # Сохраняем данные в файл
    create_file(items_with_price)

    time_end = dt.now()

    print('*' * 100)
    print(f'Parsing completed! / Парсинг завершен!')
    print(f'Time spent on parsing: {time_end - time_start} / Время выполнения парсинга: {time_end - time_start}')


if __name__ == '__main__':
    start_parse()
