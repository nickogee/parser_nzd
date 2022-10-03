
import pandas as pd
from bs4 import BeautifulSoup, element
import requests
import os


def cook_soup(url, temp_file=None):
    if temp_file:
        try:
            with open(temp_file, 'r') as f_html:
                html = f_html.read()
        except FileNotFoundError:
            f = requests.get(url)

            with open(temp_file, 'w') as f_html:
                f_html.write(f.text)
                html = f.text

    else:
        f = requests.get(url)
        html = f.text

    soup = BeautifulSoup(html, features="html.parser")
    return soup

def search_menu():

    URL = 'https://nemez1da.ru/'
    TEMP_FILE_NAME = 'temp/html_nzd_menu.html'
    RESULT_FILE_NAME = 'temp/res_menu.txt'

    def add_to_file(ls_text, prefix):

        mode = 'a' if os.path.exists(RESULT_FILE_NAME) else 'w'

        with open(RESULT_FILE_NAME, mode) as f_html:
            f_html.write(prefix + ls_text + '\n')

        return

    def find_items(root_ul, lvl, res_ls):

        for item_li in root_ul.findAll('li', {'class': 'menu-item'}, recursive=False):
            add_to_file(item_li.next.text, '\t'*lvl)
            href = item_li.contents[0].attrs['href']
            res_ls.append([lvl, item_li.next.text, href])

            sub_menu_ul = item_li.find("ul", {"class": "sub-menu"})
            if sub_menu_ul:
                find_items(sub_menu_ul, lvl + 1, res_ls)

        return

    def find_description(res_ls):

        for url_ls in res_ls:
            cur_soup = cook_soup(url_ls[2])
            desc_div = cur_soup.find("div", {"class": "taxonomy-description"})

            if desc_div:
                p_len = desc_div.contents[0].contents.__len__()
                desc_ru = desc_div.contents[0].contents[0]
                desc_ua = desc_div.contents[0].contents[p_len-1]

                if (desc_ua == desc_ru) and desc_ru.find('/') > 0:
                    ls_desc = desc_ru.split('/')
                    desc_ua, desc_ru = ''.join(ls_desc[:len(ls_desc)//2]), ''.join(ls_desc[len(ls_desc)//2:])

            else:
                desc_ru = None
                desc_ua = None

            url_ls.append(desc_ru.strip() if isinstance(desc_ru, str) else desc_ru)
            url_ls.append(desc_ua.strip() if isinstance(desc_ua, str) else desc_ua)

        return

    soup = cook_soup(temp_file=TEMP_FILE_NAME, url=URL)
    root_ul = soup.find("ul", {"id": "simple-grid-menu-primary-navigation"})

    res = []
    find_items(root_ul, 0, res)
    find_description(res)

    df = pd.DataFrame(res)
    df.columns = ['lvl', 'name', 'url', 'ru_full_name', 'ua_full_name']
    # df.to_excel("temp/output.xlsx", sheet_name='Sheet_name_1')
    df.to_csv("temp/output_menu.csv", index_label='index')
    return


def search_catalog():
    URL = 'https://nemez1da.ru/spravochnik/naczionalisticheskie-organizaczii-ukrainy/'
    TEMP_FILE_NAME = 'temp/html_nzd_catalog.html'
    RESULT_FILE_NAME = 'temp/res_catalog.txt'

    def add_discription_img(href, res_ls):
        soup_dcr = cook_soup(href)
        dcr_div = soup_dcr.find("div", {"class": "entry-content"})
        dcr_text = ''''''
        img_ls = []

        if hasattr(dcr_div, 'children'):

            for child in dcr_div.children:

                if type(child) == element.Tag:
                    if child.name == 'p':
                        dcr_text += (child.text + '\n')

                    elif child.name == 'figure':

                        for cotn in child.contents:
                            if cotn.name == 'img':
                                img_ls.append(cotn.attrs.get('data-src'))
                                break

        # res_ls.append(dcr_text)
        res_ls.append(img_ls)

        return

    def find_items(root_ul, res_ls):

        for item_li in root_ul.findAll('li', recursive=False):

            if hasattr(item_li.contents[0], 'attrs'):
                href = item_li.contents[0].attrs['href']

                res_ls.append([item_li.next.text, href])
                add_discription_img(href, res_ls)

            sub_menu_ul = item_li.find("ul")
            if sub_menu_ul:
                res_ls.append([])
                find_items(sub_menu_ul, res_ls[-1])

        return

    def search_head(res, root_div):

        h2 = ''
        for child in root_div.children:

            if type(child) == element.Tag:
                if child.name == 'h2':
                    res.append([child.text, []])

                if child.name == 'ul':
                    cur_h2_ls = res[-1][1]
                    find_items(child, cur_h2_ls)

        return

    res = []
    soup = cook_soup(url=URL)
    root_div = soup.find("div", {"class": "entry-content"})

    search_head(res=res, root_div=root_div)
    df = pd.DataFrame(res)

    df.to_csv("temp/output_catalog.csv", index_label='index')

    return






if __name__ == '__main__':
    # search_menu()
    search_catalog()

