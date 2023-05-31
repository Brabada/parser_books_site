import os
from pprint import pprint
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def check_for_redirect(response):
    main_page_url = "https://tululu.org/"
    if response.history and response.url == main_page_url:
        raise requests.HTTPError


def download_image(url, folder='images/'):
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


def get_book_title(soup):
    title_and_author = soup.find('h1').text
    title = title_and_author.split('::')
    return title[0].strip()


def get_book_author(soup):
    title_and_author = soup.find('h1').text
    author = title_and_author.split('::')
    return author[1].strip()


def get_book_image_url(soup, book_page_url):
    img_rel_path = soup.find('div', class_='bookimage').find('img')['src']
    img_src = urljoin(book_page_url, img_rel_path)
    return img_src


def fetch_book_page_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return
    return BeautifulSoup(response.text, 'lxml')


def get_book_comments(soup):
    raw_comments = soup.find_all('div', class_='texts')
    comments = []
    for raw_comment in raw_comments:
        comments.append(raw_comment.find('span', class_='black').text)
    return comments


def get_book_genres(soup):
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    genres = []
    for raw_genre in raw_genres:
        genres.append(raw_genre.text)
    return genres


def download_book(book_id):
    book_url = f'https://tululu.org/b{book_id}/'
    soup = fetch_book_page_soup(book_url)
    if not soup:
        return

    title = get_book_title(soup)
    filename = f'{book_id}. {title}'

    image_src = get_book_image_url(soup, book_url)
    if image_src:
        download_image(image_src)
    download_txt(book_url, filename)
    pprint(parse_book_page(soup))


def parse_book_page(soup):
    """Returns dict with author, title, genre"""

    book_info = {
        'author': get_book_author(soup),
        'title': get_book_title(soup),
        'genres': get_book_genres(soup),
        'comments': get_book_comments(soup),
    }
    return book_info


def main():
    for book_id in range(1, 10):
        download_book(book_id)


if __name__ == "__main__":
    main()
