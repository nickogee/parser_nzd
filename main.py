
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import csv

TEMP_FILE_NAME = 'temp/html_nzd.txt'
RESULT_FILE_NAME = 'temp/res.txt'

def print_hi(name):

    def add_to_file(ls_text, prefix):

        mode = 'a' if os.path.exists(RESULT_FILE_NAME) else 'w'

        with open(RESULT_FILE_NAME, mode) as f_html:
            f_html.write(prefix + ls_text + '\n')

        return

    def find_items(root_ul, prefix):
        for item_li in root_ul.findAll('li', {'class': 'menu-item'}):
            add_to_file(item_li.next.text, prefix)

            sub_menu_ul = item_li.find("ul", {"class": "sub-menu"})
            if sub_menu_ul:
                find_items(sub_menu_ul, prefix + '\t')


    try:
        with open(TEMP_FILE_NAME, 'r') as f_html:
            soup = BeautifulSoup(f_html.read(), features="html.parser")
    except FileNotFoundError:
        f = requests.get('https://nemez1da.ru/naczistskie-podrazdeleniya/')

        with open(TEMP_FILE_NAME, 'w') as f_html:
            f_html.write(f.text)

        soup = BeautifulSoup(f.text, features="html.parser")

    root_ul = soup.find("ul", {"id": "simple-grid-menu-primary-navigation"})
    find_items(root_ul, '')


if __name__ == '__main__':
    print_hi('PyCharm')


