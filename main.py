import sys
import schedule
import time

import requests
import logging
import pandas as pd

from bs4 import BeautifulSoup
from book_parser import BookParser

url_main = 'https://books.toscrape.com/catalogue/'
url_catalogue = url_main + 'page-{page_number}.html'

logging.basicConfig(
    filename='log.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='UTF-8',
    level=logging.INFO
)

file_save = 'books_data.csv'


# Получить списка url для книг на выбранной странице
def parse_book_list(page_number):
    url = url_catalogue.format(page_number=page_number)
    response = requests.get(url)
    page = BeautifulSoup(response.text, 'html.parser')

    books_obj = page.find_all('article')
    return list(map(lambda book: book.div.a['href'], books_obj))


# Получить информацию по книге со страницы
def parse_book_info(book_url):
    url = url_main + book_url
    response = requests.get(url)
    page = BeautifulSoup(response.text, 'html.parser')

    book_info = BookParser(page)
    return book_info


# Сохраняем все данные в файл
def data_loader():
    header = ["upc", "title", "price", "rating", "count_review", "product_type", "description"]
    data = []

    logging.info("Начало загрузки данных")
    for page_number in range(1, 50):
        books_url = parse_book_list(page_number)
        for url in books_url:
            book = parse_book_info(url)
            data.append(book.getObj())
        logging.info(f"Обработана страница: {page_number}")
    logging.info(f"Завершение загрузки данных. Загружено книг: {len(data)}")

    return pd.DataFrame(data, columns=header)


# Ищем дубли и удаляем их, пересохраняем в файл
def data_checker(df):
    count_before = df.shape[0]

    df.dropna()
    # Ищем дубликаты по полю UPC (Сначала сортируем, потом удаляем)
    df.drop_duplicates(subset=['upc'], inplace=True)
    count_after = df.shape[0]
    df.to_csv(file_save, encoding='utf-8', index=False, sep=';')
    logging.info(f"Процедура удаления дублей. Кол-во строк ДО: {count_before}; Кол-во строк ПОСЛЕ: {count_after}")


# Сохранение DataFrame в файл
def data_saver(df):
    df.to_csv(file_save, encoding='utf-8', index=False, sep=';')


# Основная функция, которую "шедуллер" будет дергать
def job():
    df = data_loader()
    data_checker(df)
    data_saver(df)


#schedule.every().day.at("19:25", "Europe/Moscow").do(job)
#while True:
#    schedule.run_pending()
#    time.sleep(1)
job()