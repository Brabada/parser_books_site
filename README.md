# Book parser from tululu.org

CLI-utility that downloads books, books covers and metadata (author, description, commentaries) from website free-book
site [tululu.org](https://tululu.org/).


### How to launch

For launching is need [**Python 3.10**](https://www.python.org/downloads/release/python-3109/).

Installing neccessary packages:
```shell
$ cd c/path/to/repository
$ pip install -r requirements.txt
```

Launching utility:
```shell
$ cd c/path/to/repository
$ python main.py --start_id 1 --end_id 10
```

### Arguments

Utility takes books ids as two arguments: `--start_id` and `--end_id`, which are setting up begin and end ranges for
downloading books by their id. 

End of range is **included**. 

If there is no book by book_id, utility continuing to work.

Example: https://tululu.org/b9/, there's book_id is **9**.
- `--start_id` - range's start, takes integer value (**int**);
- `--end_id` - range's end (included), takes integer value (**int**).

### Project goals
This project is created for practicing parsing data from websites using _BeautifulSoup4_.