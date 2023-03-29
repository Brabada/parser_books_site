import os

import requests


def fetch_book(book_id):
    books_dir = 'books'
    os.makedirs(books_dir, exist_ok=True)

    url = f'https://tululu.org/txt.php?id={book_id}'
    response = requests.get(url)
    response.raise_for_status()
    book_name = f'{book_id}.txt'
    with open(f'{books_dir}/{book_name}', 'w') as book:
        book.write(response.text)


def main():
    for book_id in range(1, 10):
        fetch_book(book_id)


if __name__ == "__main__":
    main()

