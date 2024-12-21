# пока что тут жёсктий срач, я исправлю
# пока что тут жёсктий срач, я исправлю
# пока что тут жёсктий срач, я исправлю
# пока что тут жёсктий срач, я исправлю
# пока что тут жёсктий срач, я исправлю

import os
import subprocess
from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import re
import sqlite3
import time

app = Flask(__name__, static_folder='src')
app.secret_key = "cookies_secret_key"

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
    user = session.get('user')
    session['user'] = user
    session['error_message'] = None
    return render_template('index.html', user=user)


@app.route('/login', methods=["GET", "POST"])
def login_page():
    error_message = session.get('error_message')

    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')

        with sqlite3.connect('VeritasDB.db') as conn:
            cur = conn.cursor()

            req_db = "SELECT login, password FROM verifyed_users WHERE login = ?"
 
            cur.execute(req_db, (username,))
            user = cur.fetchone()

        if user is None:
            error_message = "Неправильный логин"
        elif user[1] != password:
            error_message = "Неправильный пароль"
        else:
            session['user'] = username
            session['error_message'] = None
            return redirect('/')

    return render_template('login.html', error_message = error_message)


@app.route('/reg', methods=["GET", "POST"])
def reg_page():
    error_message = None

    if request.method == 'POST':

        username = request.form.get('login')
        password = request.form.get('password')
        generated_key = request.form.get('key')

        with sqlite3.connect('VeritasDB.db') as conn:
            cur = conn.cursor()

            req_db = "SELECT login FROM verifyed_users WHERE login = ?"
 
            cur.execute(req_db, (username,))
            user = cur.fetchone()

            if user is None:
                req_db = "SELECT * FROM generated_keys"
                cur.execute(req_db)
                keys = cur.fetchall()
                if generated_key in [k[1] for k in keys]:
                    req_db = "INSERT INTO verifyed_users (login, password) VALUES (?, ?)"
                    cur.execute(req_db, (username, password))
                    conn.commit()
                    req_db = " DELETE FROM generated_keys WHERE key = ? "
                    cur.execute(req_db, (generated_key, ))
                    conn.commit()
                    session['error_message'] = "Аккаунт зарегестрирован"
                    return redirect('/login')
                else:
                    error_message = "Неправильный ключ"
            else:
                error_message = "Имя занято"


    return render_template('reg.html', error_message=error_message)


@app.route('/admin', methods=["GET", "POST"])
def admin_log():
    if request.method == "POST":

        if request.form.get('login') == 'admin' and request.form.get('password') == 'admin':
            session['logged_in_admin'] = True
            return redirect("/admin-panel")
        else:
             return render_template("admin-log.html")     
    return render_template("admin-log.html")


# более подробно, что находится внутри бд, можно в файле scripts.py
@app.route('/admin-panel', methods=["GET", "POST"])
def admin_panel():
    # админ панель доступна по ссылке localhost:5000/admin
    # сделана для проверки для преподавателя
    if session.get('logged_in_admin'):
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
            task = " SELECT * FROM generated_keys "
            cur.execute(task)
            keys = cur.fetchall()
        try:
            keys = [i[1] for i in keys]
            dataForm=dataForm
        except NameError:
            keys=[]
            dataForm=[] # на случай если бд полетит и коннекта не будет
        finally:
            if request.method == "POST":
                number_of_keys = int(request.form.get("key_count"))
                task = " INSERT INTO generated_keys (key) VALUES (?) "
                with sqlite3.connect("VeritasDB.db") as conn:
                    cur = conn.cursor()
                    for new_key in generate_uniq_keys(number_of_keys):
                        cur.execute(task, (new_key,))
                    conn.commit()
                return redirect(url_for("admin_panel"))
            return render_template("admin-panel.html", dataForm=dataForm, generated_keys=keys)
    else:
        return redirect('/admin')


def generate_uniq_keys(n_k: int): # numbers_of_keys
    import random, string
    # ДЛИННА КЛЮЧА ДЛЯ РЕГИСТРАЦИИ
    LENGTH_OF_KEY = 10
    keys = list()
    for i in range(n_k):
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=LENGTH_OF_KEY))
        keys.append(key)
    return keys


@app.route('/delete-key', methods=["POST"])
def delete_key():
    key = request.form.get("key-to-delete")
    with sqlite3.connect('VeritasDB.db') as conn:
        cur = conn.cursor()
        req_db = " DELETE FROM generated_keys WHERE key = ? "

        cur.execute(req_db, (key, ))

        conn.commit()
    return redirect(url_for("admin_panel"))


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

