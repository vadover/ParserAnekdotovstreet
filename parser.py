import requests
import re
import csv
from bs4 import BeautifulSoup

# Переменные
URL = 'https://anekdotovstreet.com/semeynye/lubov-otnosheniya/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/100.0.4896.88 Safari/537.36',
           'accept': '*/*'}
HOST = 'https://anekdotovstreet.com'
FILE = 'anekdots.csv'


# Получаем страницу
def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


# Получаем количество страниц по категории
def get_pages_count(html):
    soup = BeautifulSoup(html, 'lxml')
    pagination = soup.find('ul', class_='pagination')
    search_pagination = pagination.find_all('li')[-1]
    try:
        link_last_pages = search_pagination.find('a').get('href')
    except AttributeError:
        return 1
    number_last_pages = re.sub('[^0-9]', '', link_last_pages)

    if search_pagination:
        return int(number_last_pages)
    else:
        return 1


# Получаем необходимый контент
def get_content(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all('div', class_='anekdot-text')

    anekdot = []
    for item in items:
        link = item.find('span', class_='anekdotlink').text.replace('#', '').strip()
        link_grade = f'anekdot{link}'
        anekdot.append({
            'text': item.find('p').get_text(strip=True),
            'grade': item.find('span', id=link_grade).get_text(strip=True),
            'link': HOST + item.find('a').get('href')
        })
    return anekdot


# Сохраняем всё в .csv файл
def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Текст', 'Оценка', 'Ссылка'])
        for item in items:
            writer.writerow([item['text'], item['grade'], item['link']])


# Основная функция
def parse():
    URL = input('Введите URL: ')
    html = get_html(URL)
    # Проверка работоспособности
    if html.status_code == 200:
        anekdot = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            if page == 1:
                html = get_html(URL)
            else:
                html = get_html(URL + str(page) + '/')
            anekdot.extend(get_content(html.text))
        save_file(anekdot, FILE)
        print(f'Получено {len(anekdot)} анекдотов.')
    else:
        print('Error')


parse()
