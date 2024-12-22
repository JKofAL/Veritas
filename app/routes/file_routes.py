from flask import Blueprint, request, render_template, current_app
import os
from app.utils.compile_utils import compile_and_run
import subprocess, re

bp = Blueprint('file_routes', __name__)


@bp.route('/upload', methods=['POST'])
def upload_file():
    '''тут вообще минимум front, почти всё бэк, так что пока над оформлением не парюсь
    вообще можно связать файлы compile_utils и этот, чтобы оптимизировать место,
    накидал идеи в compile_utils.py'''

    file = request.files['file']
    if not file.filename.endswith(".cpp"):
        return render_template('results.html', status="Ошибка", message="Файл должен быть .cpp", output="")

    # Сохраняем файл
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # Компиляция файла
    executable_path = os.path.join(current_app.config["COMPILE_FOLDER"], "program.out")
    compile_command = f"g++ {file_path} -o {executable_path}"

    try:
        subprocess.run(compile_command, shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8', errors='replace')
        return render_template('results.html', status="Ошибка", message="Ошибка компиляции", output=error_message)

    # Выполнение программы с входными данными
    with open(current_app.config['TEST_INPUT'], "r") as input_file:
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
    with open(current_app.config['TEST_OUTPUT'], "r") as expected_output_file:
        expected_output = expected_output_file.read().strip() # ожидаемое число

    # Сравниваем фактический и ожидаемый результаты
    if actual_output == expected_output:
        return render_template('results.html', status="УСПЕХ", message="Вывод совпадает с ожидаемым", output=actual_output)
    else:
        return render_template('results.html', status="НЕУДАЧА", message="Вывод не совпадает с ожидаемым", output=actual_output, expected_output=expected_output)

