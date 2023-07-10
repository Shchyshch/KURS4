from classes import HH, SJ, JSONSaver


def main():
    # Получение вакансий
    keyword = input('Введите поисковый запрос: ')
    hh = HH(keyword)
    sj = SJ(keyword)

    while True:
        pl = input('Выберите платформу для поиска вакансий:\n1.hh.ru\n2.superjob.ru\n3.Обе\n')
        if pl == '1':
            hh.get_request()
            vacancies = hh.get_formatted_vacancies()
            break
        if pl == '2':
            sj.get_request()
            vacancies = sj.get_formatted_vacancies()
            break
        if pl == '3':
            hh.get_request()
            sj.get_request()
            vacancies = hh.get_formatted_vacancies() + sj.get_formatted_vacancies()
            break

    # Сохранить в файл
    js = JSONSaver(f'{keyword}.json', vacancies)

    # Выборка вакансий
    while True:
        action = input('1.Вывести всё\n2.Отсортировать по зарплате (по возрастанию)\n'
                       '3.Вывести топ-10 вакансий по нижней границе зарплаты\n'
                       'Для выхода наберите "exit"\n')
        if action == '1':
            js_all = js.select_all()
            for v in js_all:
                print(v)
        if action == '2':
            js_sorted = js.sorted_by_salary()
            for v in js_sorted:
                print(v)
        if action == '3':
            js_top_ten = js.top_ten()
            for v in js_top_ten:
                print(v)
        if action == 'exit':
            break


if __name__ == "__main__":
    main()
