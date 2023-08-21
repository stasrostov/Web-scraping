from datetime import datetime


def logger(old_function):

    def new_function(*args, **kwargs):
        log = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        log += f' запущена функция {old_function.__name__} с аргументами {args} {kwargs}'
        result = old_function(*args, **kwargs)
        log += f' результат выполнения: {result} \n'
        with open('main.log', 'a', encoding='utf-8') as file:
            file.write(log)
        return result

    return new_function
