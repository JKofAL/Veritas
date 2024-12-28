from flask import Blueprint, request, render_template, current_app, redirect, session
import os
from app.utils.compile_utils import run_tests # как вариант перенести сюда back
from app.utils.db_utils import write_test_results
import subprocess, re

bp = Blueprint('file_routes', __name__)

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
        test_results = run_tests(file_path, current_app)
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