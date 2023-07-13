import json
import requests
from abc import ABC, abstractmethod


class API(ABC):
    """Абстрактный класс для работы с API сайтов с вакансиями"""
    def __init__(self, keyword: str):
        self.keyword = keyword
        self.vacancies = []

    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_formatted_vacancies(self):
        pass


class HH(API):
    """Класс для работы с API сайта hh.ru"""

    def get_request(self):
        """Собирает вакансии по ключевому слову"""
        for page in range(10):
            url = "https://api.hh.ru/vacancies"
            params = {
                "per_page": 100,
                "page": page,
                "text": self.keyword,
                "archive": False
            }
            response = requests.get(url, params=params).json()
            self.vacancies.extend(response['items'])

    def get_formatted_vacancies(self) -> list:
        """Возвращает вакансии с зарплатой в рублях"""
        formatted_vacancies = []
        for vacancy in self.vacancies:
            if vacancy['salary'] is not None:
                if vacancy['salary']['currency'] == 'RUR':
                    formatted_vacancies.append({
                        'name': vacancy['name'],
                        'area': vacancy['area']['name'],
                        'salary_from': vacancy['salary']['from'],
                        'salary_to': vacancy['salary']['to'],
                        'url': vacancy['alternate_url'],
                        'employer': vacancy['employer']['name'],
                        'requirement': vacancy['snippet']['requirement'],
                    })
        return formatted_vacancies


class SJ(API):
    """Класс для работы с API сайта superjob.ru"""

    def get_request(self):
        """Собирает вакансии по ключевому слову"""
        for page in range(10):
            url = "https://api.superjob.ru/2.0/vacancies/"
            params = {
                "count": 100,
                "page": page,
                "keyword": self.keyword,
                "archive": False
            }
            headers = {
                "X-Api-App-Id": "v3.r.137668782.5c28131bb75f9ea521816a4b375655b3ab9bdc5b.87983d6de48080b2e5eb099f1e01ed8a338958a8"
            }
            response = requests.get(url, headers=headers, params=params).json()
            self.vacancies.extend(response['objects'])

    def get_formatted_vacancies(self) -> list:
        """Возвращает вакансии с зарплатой в рублях"""
        formatted_vacancies = []
        for vacancy in self.vacancies:
            if vacancy['currency'] == 'rub':
                formatted_vacancies.append({
                    'name': vacancy['profession'],
                    'area': vacancy['town']['title'],
                    'salary_from': vacancy['payment_from'],
                    'salary_to': vacancy['payment_to'],
                    'url': vacancy['link'],
                    'employer': vacancy['firm_name'],
                    'requirement': vacancy['candidat'],
                })
        return formatted_vacancies


class Vacancy:
    """Класс для работы с вакансиями"""
    def __init__(self, vacancy: dict):
        self.name = vacancy['name']
        self.area = vacancy['area']
        if vacancy['salary_from'] is None:
            vacancy['salary_from'] = 0
        self.salary_from = vacancy['salary_from']
        if vacancy['salary_to'] is None:
            vacancy['salary_to'] = 0
        self.salary_to = vacancy['salary_to']
        self.url = vacancy['url']
        self.employer = vacancy['employer']
        self.requirement = vacancy['requirement']

    def __gt__(self, other):
        """Метод сравнения вакансий по минимальной зарплате"""
        return self.salary_from > other.salary_from

    def __str__(self):
        return f"""
        {self.name}, {self.area}
        Зарплата от {self.salary_from} до {self.salary_to} руб.
        {self.url}
        """


class JSONSaver:
    """Класс для сохранения информации о вакансиях в JSON-файл"""
    def __init__(self, filename: str, vacancies: list):
        self.filename = filename
        self.create_file(vacancies)

    def create_file(self, vacancies: list):
        """Сохраняет информацию в json-файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(vacancies, f, indent=2, ensure_ascii=False)

    def select_all(self) -> list:
        """Выводит информацию о всех найденных вакансиях"""
        with open(self.filename, 'r') as f:
            data = json.load(f)
        vacancy_data = [Vacancy(x) for x in data]
        return vacancy_data

    def sorted_by_salary(self) -> list:
        """Сортирует вакансии по возрастанию нижней границы указанной зарплаты"""
        vacancy_data = self.select_all()
        sorted_data = sorted(vacancy_data)
        return sorted_data

    def top_ten(self) -> list:
        """Выводит топ-10 вакансий с самой высокой указанной минимальной зарплатой"""
        vacancy_data = self.select_all()
        sorted_data = sorted(vacancy_data, reverse=True)
        return sorted_data[:10]
