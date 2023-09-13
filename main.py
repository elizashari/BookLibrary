import requests
import os
from requests.exceptions import HTTPError, Timeout
from urllib.parse import unquote, urljoin, urlsplit,urlparse
from bs4 import BeautifulSoup
import argparse
import logging

def check_for_redirect(response):
    main_page_url = 'https://tululu.org/'
    if response.url == main_page_url:
        raise HTTPError



def download_txt(book_id, filename, folder='books/'):
    text_url = 'https://tululu.org/txt.php?'
    fullpath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    payload = {'id': book_id}
    response = requests.get(text_url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    with open(fullpath, 'wb') as file:
        file.write(response.content)

    return fullpath


def download_image(url, filename, folder='images/'):
    image_fullpath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    with open(image_fullpath, 'wb') as file:
        file.write(response.content)
    return image_fullpath


def parse_book_page(book_html):
    soup = BeautifulSoup(book_html, 'lxml')
    book = soup.find('div', id='content').find('h1').text
    book_name, book_author = book.split('::')
    book_name = book_name.strip()
    book_author = book_author.strip()
    book_image_url = soup.find('div', class_="bookimage") \
                                .find('a').find('img')['src']
    comments = soup.find_all('div', class_='texts')
    comments_txt = [comment.find('span').text for comment in comments]
    genres = soup.find('span', class_='d_book').find_all('a')
    genres_txt = [genre.text for genre in genres]
    return {'book_name': book_name,
        'book_author': book_author,
        'book_image_url' : book_image_url,
        'comments': comments_txt,
        'geners' : genres_txt}


def main():
    main_page_url = 'https://tululu.org/'


    parser = argparse.ArgumentParser(description=f'Parse books and images from on-line library: {main_page_url}')
    parser.add_argument('--start_id',
                        default=1,
                        type=int)
    parser.add_argument('--stop_id',
                        default=10,
                        type=int)
    args = parser.parse_args()
    start_id = args.start_id
    stop_id = args.stop_id
    for book_id in range(start_id, stop_id+1):
        try:
            book_page_url = urljoin(main_page_url, f'b{book_id}')
            response = requests.get(book_page_url)
            response.raise_for_status()
            check_for_redirect(response)
            book_html = response.text
            book = parse_book_page(book_html)
            book_name = book['book_name']
            book_author = book['book_author']
            book_filename = f"{book_id}. {book_name}.txt"
            book_image_url = book['book_image_url']
            book_image_url = urljoin(book_page_url, book_image_url)

            saved_txt_filepath = download_txt(book_id,
                                            book_filename,
                                            folder='books/')
            image_name = unquote(urlparse(book_image_url).path.split("/")[-1])
            saved_image_filepath = download_image(book_image_url,
                                                      image_name,
                                                      folder='image/')
            comments = book['comments']
            geners = book['geners']

            print(f'\nНазвание: {book_name}')
            print(f'Автор: {book_author}')
            print(f'Жанр: {geners}')
            print(f'Комментарии: {comments}')
            
            
        except HTTPError:
            logging.info(f'HTTP protocol error {book_page_url} is unavailable')


if __name__ == '__main__':
    main()

