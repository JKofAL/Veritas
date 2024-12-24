from flask import Blueprint, request, render_template, current_app, redirect, url_for, session, jsonify
import os
from app.utils.compile_utils import compile_and_run # как вариант перенести сюда back
from app.utils.db_utils import write_test_results
import subprocess, re

bp = Blueprint('file_routes', __name__)

# ФУНКЦИИ ПРОВЕРКИ ФАЙЛОВ
# ФУНКЦИИ ПРОВЕРКИ ФАЙЛОВ
# ФУНКЦИИ ПРОВЕРКИ ФАЙЛОВ
# ФУНКЦИИ ПРОВЕРКИ ФАЙЛОВ


# Функция для получения среза данных
def get_test_input_slice(file_path, test_number):
    """
    Считывает входные данные из файла и возвращает срез.

    :param file_path: Путь к файлу с входными данными.
    :param test_number: Номер текущего теста.
    :return: Срез входных данных (строка).
    """
    try:
        with open(file_path, "r") as file:
            # Считываем все строки и убираем лишние пробелы
            test_data = file.read().strip()

            # Определяем размер среза: по умолчанию 4 строки, но для третьего запуска — 9 строк
            if test_number == 2:  # Третий запуск
                slice_size = 12
            elif test_number == 3:
                slice_size = 7
            else:
                slice_size = 4

            # Вычисляем начальный и конечный индексы среза
            start_index = sum(4 if i not in [2, 3] else (12 if i == 2 else 7) for i in range(test_number))
            end_index = start_index + slice_size
            # Берём только нужный срез
            sliced_data = "\n".join(test_data[start_index:end_index])
            return sliced_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {file_path} не найден")


def result_stroke(
        status=None, 
        test_number=0,
        error=None, 
        details=None, 
        extracted_output=None, 
        expected_output=None, 
        rating=0):
    return {
        "status": status,
        "test_number": test_number,
        "error": error,
        "details": details,
        "extracted_output": extracted_output,
        "expected_output": expected_output,
        "rating": rating,
    }

# Функция для выполнения всех тестов
def run_tests(file_path):
    # Проверяем наличие g++
    # if subprocess.run("g++ --version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
    #     raise EnvironmentError("Компилятор g++ не установлен или недоступен в PATH.")

    # Компиляция файла
    executable_path = os.path.join(current_app.config['COMPILE_FOLDER'], "program.out")
    compile_command = f"g++ {file_path} -o {executable_path}"
    try:
        subprocess.run(compile_command, shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        return result_stroke(status= "Ошибка", error= "Ошибка компиляции", details= e.stderr.decode('utf-8', errors='replace'))

    # Выполняем тесты
    results = []
    for test_number in range(4):  # Четыре запуска: c = 0, 1, 2, 3
        try:
            # Читаем данные для текущего теста
            test_input_path = os.path.join(current_app.config['TEST_INPUT'])
            test_input = get_test_input_slice(test_input_path, test_number)

            # Выполнение программы с входными данными
            result = subprocess.run(
                executable_path,
                input=test_input.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            # Обработка вывода программы
            try:
                actual_output = result.stdout.decode('utf-8', errors='replace').strip()

                # Регулярное выражение: извлекаем число в конце строки (если есть)
                match = re.search(r'\d+$', actual_output)  # Ищем любое число в конце строки
                if match:
                    extracted_output = match.group()
                else:
                    extracted_output = "Ответ не найден"
            except UnicodeDecodeError as e:
                return result_stroke(status="ФАЙЛ", error= f"Ошибка декодирования вывода: {str(e)}")

            # Сравниваем с ожидаемым результатом
            with open("test_output.txt", "r") as expected_file:
                expected_outputs = expected_file.read().strip().splitlines()
            
            if test_number < len(expected_outputs):
                expected_output = expected_outputs[test_number]
                if extracted_output == expected_output:
                    results.append(result_stroke(
                        test_number= test_number + 1,
                        status= "УСПЕХ",
                        extracted_output= extracted_output,
                        expected_output= expected_output,
                        rating= 1
                    ))
                else:
                    results.append(result_stroke(
                        test_number= test_number + 1,
                        status= "НЕУДАЧА",
                        extracted_output= extracted_output,
                        expected_output= expected_output,
                    ))
                         
        except FileNotFoundError as e:
            results.append({"test_number": test_number + 1, "status": "Ошибка", "error": str(e)})
        except subprocess.TimeoutExpired:
            results.append({"test_number": test_number + 1, "status": "Ошибка", "error": "Тест превысил время выполнения"})
        except Exception as e:
            results.append({"test_number": test_number + 1, "status": "Ошибка", "error": str(e)})

    return results



############################
############################
############################
############################
############################

@bp.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    # Переменная для хранения результатов проверок
    validation_results = []

    # Проверка наличия файла
    if not file:
        validation_results.append("Файл не был загружен.")
    else:
        # Проверка расширения файла (только .cpp)
        if not file.filename.endswith('.cpp'):
            validation_results.append("Файл должен быть с расширением .cpp.")

        # Проверка размера файла (например, максимум 5 МБ)
        if file.content_length > 5 * 1024 * 1024:  # 5 MB
            validation_results.append("Размер файла не должен превышать 5 МБ.")

    # Если есть ошибки проверки, возвращаем ошибки
    if validation_results:
        return render_template('results.html', validation_results=validation_results)

    # Если проверки пройдены, сохраняем файл
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Запуск тестов
    try:
        test_results = run_tests(file_path)
        # подсчёт рейтинга
        rate = 0
        print('1')
        for test in test_results:
            rate += test["rating"]
        print('2')
        write_test_results(session.get('user'), test_results)
        print(3)
        return render_template('results.html', test_results=test_results, score=rate)
    except Exception as e:
        for stroke in test_results:
            print(stroke)
        # return jsonify(result_stroke(status= "Ошибка", error= str(e)))
        return redirect('/')