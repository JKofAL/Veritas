import os
import subprocess
from flask import Flask, request, jsonify, render_template
import re
import sqlite3

app = Flask(__name__, static_folder='src')

# Папка для загрузки файлов и хранения результатов
UPLOAD_FOLDER = './uploads'
COMPILE_FOLDER = './compiled'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPILE_FOLDER, exist_ok=True)

# Тестовые данные
TEST_INPUT = "test_input.txt"   # Файл с входными данными
TEST_OUTPUT = "test_output.txt" # Файл с ожидаемым результатом

@app.route('/')
def index():
    return render_template('index.html')


# более подробно, что находится внутри бд, можно в файле scripts.py
@app.route('/admin')
def admin_panel():
    # админ панель доступна по ссылке localhost:5000/admin
    # сделана для проверки для преподавателя
    with sqlite3.connect("VeritasDB.db") as conn:
        cur = conn.cursor()
        # устанавливаем соединение с БД и создаём курсор

        # создаём массив данных, которые достанем
        dataForm = []

        # делаем запрос для БД "ВЫБРАТЬ всё ИЗ ТАБЛИЦЫ students"
        task = """

            SELECT * FROM students

        """

        # задаём запрос для курсора и вытаскиваем всю инфу методом fetchall
        cur.execute(task)
        students_results = cur.fetchall()
        for elem in students_results:
            # форматирую так, как мне будет удобнее брать информацию
            dataForm.append({"name": elem[1], "vusGroup": elem[2], "lbs": elem[3].replace("1", "зачёт", 7).replace("0", "незач", 7).split(" ")})
            # dataForm.append([elem[1], elem[2], elem[3].replace("1", "зачтено", 7).replace("0", "незачтено", 7).split(" ")])
        # print(dataForm)
    try:
        return render_template('admin.html', dataForm=dataForm)
    except NameError:
        return render_template('admin.html', dataForm=[]) # на случай если бд полетит и коннекта не будет


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('results.html', status="Ошибка", message="Файл не загружен", output="")
    
    # -----------------------------------------------------------------------
    # if subprocess.run("g++ --version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
    #     raise EnvironmentError("Компилятор g++ не установлен или недоступен в PATH.")

    # насчёт 2-ух строк выше у меня вопросы, зачем это делать, если на сервере, на котором держится проект, будет
    # предустановлен g++, и такая ошибка просто не может быть, а если и может, то проект ляжет
    # тем более у нас есть попытка обработать файл ниже (try except)
    # -----------------------------------------------------------------------

    file = request.files['file']
    if file.filename == '':
        return render_template('results.html', status="Ошибка", message="Файл не выбран", output="")

    if not file.filename.endswith(".cpp"):
        return render_template('results.html', status="Ошибка", message="Файл должен быть .cpp", output="")

    # Сохраняем файл
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Компиляция файла
    executable_path = os.path.join(COMPILE_FOLDER, "program.out")
    compile_command = f"g++ {file_path} -o {executable_path}"

    try:
        subprocess.run(compile_command, shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8', errors='replace')
        return render_template('results.html', status="Ошибка", message="Ошибка компиляции", output=error_message)

    # Выполнение программы с входными данными
    with open(TEST_INPUT, "r") as input_file:
        try:
            result = subprocess.run(executable_path, stdin=input_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        except subprocess.TimeoutExpired:
            return render_template('results.html', status="Ошибка", message="Программа выполнялась слишком долго", output="")

    # Чтение и сравнение результата
    try:
        actual_output = result.stdout.decode('utf-8', errors='replace').strip() # число, которое выдала программа
        # -----------------------------------------------------------------------
        # -----------------------------------------------------------------------
        # Извлечение числа из вывода
        match = re.search(r'\d+$', actual_output)
        if match:
            extracted_output = match.group()  # Здесь будет "22" или другое число
        else:
            extracted_output = "Ответ не найден"
        # -----------------------------------------------------------------------
        # -----------------------------------------------------------------------
        # не понял что за переменная (куда мне её выводить, у меня есть actual_output и expected_output)
        # вывод программы и ожидаемый вывод
        # пока что нигде не юзается (понял, что сохраняется число в виде ответа программы,
        # я так понимаю это для того, чтобы игнорировать текст в output)
        # -----------------------------------------------------------------------
        # -----------------------------------------------------------------------
    except UnicodeDecodeError as e:
        return render_template('results.html', status="Ошибка", message=f"Ошибка декодирования вывода: {str(e)}", output="")

    # Читаем ожидаемый результат из test_output.txt
    with open(TEST_OUTPUT, "r") as expected_output_file:
        expected_output = expected_output_file.read().strip() # ожидаемое число

    # Сравниваем фактический и ожидаемый результаты
    if actual_output == expected_output:
        return render_template('results.html', status="УСПЕХ", message="Вывод совпадает с ожидаемым", output=actual_output)
    else:
        return render_template('results.html', status="НЕУДАЧА", message="Вывод не совпадает с ожидаемым", output=actual_output, expected_output=expected_output)


if __name__ == '__main__':
    app.run(debug=True)

