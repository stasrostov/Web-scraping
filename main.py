from logger import logger
import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers


@logger
def get_headers():
    headers = Headers(browser='chrome', os='win').generate()
    headers['accept-language'] = 'ru-RU,ru;q=0.9'
    return headers


@logger
def criteria_check(vacancy_description):
    verification_passed = False
    if vacancy_description.find('Django') >= 0 and vacancy_description.find('Flask') >= 0:
        verification_passed = True
    return verification_passed


@logger
def get_list_vacancies_html(link):
    html = requests.get(link, headers=get_headers()).text
    soup = BeautifulSoup(html, features='lxml')
    vacancies_div = soup.find(class_='vacancy-serp-content')
    vacancies_tag = vacancies_div.find_all(class_='serp-item')
    next_page = get_next_page(soup)
    return {'vacancies_tag': vacancies_tag, 'next_page': next_page}


@logger
def get_vacancy_attrs(vacancy_tag):
    title_tag = vacancy_tag.find(class_='serp-item__title')
    link = title_tag['href']
    title = title_tag.text.replace('\u202f', ' ')
    vacancy_html = requests.get(link, headers=get_headers()).text
    vacancy_soup = BeautifulSoup(vacancy_html, features='lxml')
    description_element = vacancy_soup.find(class_='vacancy-description')
    description = description_element.text.replace('\u202f', ' ') if description_element else ''
    company = vacancy_soup.find(class_='vacancy-company-name').text.replace('\u202f', ' ')
    salary = vacancy_soup.find(attrs={'data-qa': 'vacancy-salary'}).text.replace('\u202f', ' ')
    try:
        city = vacancy_soup.find(attrs={'data-qa': 'vacancy-view-raw-address'}).text.replace('\u202f', ' ').split(',')[0]
    except AttributeError:
        city = vacancy_soup.find(attrs={'data-qa': 'vacancy-view-location'}).text.replace('\u202f', ' ').split(',')[0]
    vacancy_attrs = {
        'title': title,
        'link': link,
        'company': company,
        'salary': salary,
        'city': city
    }
    return {'vacancy_attrs': vacancy_attrs, 'criteria_check': criteria_check(description)}


@logger
def get_next_page(soup):
    link = ''
    exists = True
    try:
        link = soup.find(attrs={'data-qa': 'pager-next'})['href']
    finally:
        exists = False
    return {'exists': exists, 'link': link}


if __name__ == '__main__':
    HOST = 'https://spb.hh.ru/search/vacancy?area=1&area=2&text=python&only_with_salary=true&search_period=1'
    vacancies = []

    while True:
        vacancies_content = get_list_vacancies_html(HOST)
        list_vacancies_html = vacancies_content['vacancies_tag']

        for vacancy in list_vacancies_html:
            vacancy_info = get_vacancy_attrs(vacancy)
            if vacancy_info['criteria_check']:
                vacancies.append(vacancy_info['vacancy_attrs'])

        if not vacancies_content['next_page']['exists']:
            break
        HOST = vacancies_content['next_page']['link']

    with open('vacancies_info.json', 'w', encoding='utf-8') as f:
        json.dump(vacancies, f, indent=2, ensure_ascii=False)
