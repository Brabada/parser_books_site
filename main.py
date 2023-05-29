import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def check_for_redirect(response):
    main_page_url = "https://tululu.org/"
    if response.history and response.url == main_page_url:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return

    filename = sanitize_filename(filename)
    book_name = f'{filename}.txt'
    filepath = sanitize_filepath(os.path.join(folder, book_name))
    with open(filepath, 'w') as book:
        book.write(response.text)
    return filepath


def fetch_book_title(book_id):

    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    title_and_author = soup.find('h1').text
    title = title_and_author.split('::')
    return title[0].strip()


def download_book(book_id):
    title = fetch_book_title(book_id)
    book_url = f'http://tululu.org/txt.php?id={book_id}'
    filename = f'{book_id}. {title}'
    download_txt(book_url, filename)


def main():
    for book_id in range(1, 10):
        download_book(book_id)


if __name__ == "__main__":
    main()
