import os
from urllib.parse import urljoin, urlsplit
import argparse
import logging
from time import sleep

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def check_for_redirect(response):
    """Checking for redirect codes 3xx. If found any raises exception"""
    main_page_url = "https://tululu.org/"
    if response.history :
        raise requests.HTTPError


def download_image(url, folder='images/'):
    """Download image by url, saves its to folder and returns path to image"""
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)

    filename = urlsplit(url).path
    filename = filename.split(sep='/')[-1]

    image_path = os.path.join(folder, filename)
    with open(image_path, 'wb') as image:
        image.write(response.content)
    return image_path


def download_txt(url, filename, folder='books/'):
    """
    Функция для скачивания текстовых файлов.
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
    check_for_redirect(response)

    filename = sanitize_filename(filename)
    book_name = f'{filename}.txt'
    filepath = sanitize_filepath(os.path.join(folder, book_name))
    with open(filepath, 'w') as book:
        book.write(response.text)
    return filepath


def get_book_title(soup):
    """Returns book title from bs4 soup"""
    title_and_author = soup.find('h1').text
    title = title_and_author.split('::')
    return title[0].strip()


def get_book_author(soup):
    """Returns book_author from bs4 soup"""
    title_and_author = soup.find('h1').text
    author = title_and_author.split('::')
    return author[1].strip()


def get_book_image_url(soup, book_page_url):
    """Returns URL for book cover by book page URL from bs4 soup"""
    img_rel_path = soup.find('div', class_='bookimage').find('img')['src']
    img_src = urljoin(book_page_url, img_rel_path)
    return img_src


def fetch_book_page_soup(url):
    """Fetched bs4 soup from url"""
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')


def get_book_comments(soup):
    """Return book comments[] from bs4 soup"""
    raw_comments = soup.find_all('div', class_='texts')
    comments = [
        comment.find('span', class_='black').text for comment in raw_comments]
    logging.info(comments)
    return comments


def get_book_genres(soup):
    """Returns book genres[] from bs4 soup"""
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [raw_genre.text for raw_genre in raw_genres]
    logging.info(genres)
    return genres


def download_book(book_id):
    """Downloads book txt and cover by book_id from tululu.org"""
    book_url = f'https://tululu.org/b{book_id}/'
    soup = fetch_book_page_soup(book_url)

    book_page = parse_book_page(soup)
    filename = f'{book_id}. {book_page["title"]}'

    image_src = get_book_image_url(soup, book_url)
    download_image(image_src)
    download_txt(book_url, filename)


def parse_book_page(soup):
    """Returns dict with author, title, genres[], comments[]"""

    book_page = {
        'author': get_book_author(soup),
        'title': get_book_title(soup),
        'genres': get_book_genres(soup),
        'comments': get_book_comments(soup),
    }
    return book_page


def init_arg_parser():
    parser = argparse.ArgumentParser(
        description='Script is download books from tululu.org by their id.')
    parser.add_argument(
        '-s',
        '--start_id',
        help='book_id for range start',
        default=1,
        type=int)
    parser.add_argument(
        '-e',
        '--end_id',
        help='book_id for range end',
        default=1,
        type=int)
    return parser


def main():
    logging.basicConfig(level=logging.INFO)
    parser = init_arg_parser()
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id+1):
        try:
            download_book(book_id)
            logging.info(f'Book {book_id} downloaded.')
        except requests.HTTPError:
            logging.warning(f'Book (id {book_id}) not found on server.')
        except requests.ConnectionError:
            logging.warning(f'Book {book_id} can\'t be downloaded via '
                            f'connection error.')
            sleep(5)


if __name__ == "__main__":
    main()
