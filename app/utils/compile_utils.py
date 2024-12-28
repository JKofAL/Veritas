import subprocess, os, re

######################!!!ВАЖНО!!!#####################
# функция run_tests вызывается из app.routes.file_routes
# и эта же функция возвращает результат теста обратно
# форма вывода результата по тесту представлена в функции result_stroke
# используйте эту строку везде для возврата значений мне на front, потому что иначе я их не прочитаю
# при необходимости вы можете добавить новые строки в форму вывода, для этого
# измените параметры в функции result_stroke
#######################################################

# def compile_and_run(file_path, executable_path, input_path):
#     try:
#         compile_command = f"g++ {file_path} -o {executable_path}"
#         subprocess.run(compile_command, shell=True, check=True, stderr=subprocess.PIPE)

#         with open(input_path, "r") as input_file:
#             result = subprocess.run(executable_path, stdin=input_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
#             return result.stdout.decode('utf-8', errors='replace').strip()
#     except subprocess.CalledProcessError as e:
#         return f"Compilation error: {e.stderr.decode('utf-8', errors='replace')}"

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
def run_tests(file_path, current_app):
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
