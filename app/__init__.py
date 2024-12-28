# ----- ###### ----- #

from flask import Flask # framework
import secrets # генерация надёжных ключей

# ----- ###### ----- #


def create_app():
    # создаём приложение Flask
    app = Flask(__name__, static_folder='src') # определяем папку статических файлов как src (default="static")
    app.secret_key = secrets.token_hex(32) # генерируем ключ для куки в виде 64 символов

    # папки для файлов
    app.config['UPLOAD_FOLDER'] = './uploads' # загруженные файлы
    app.config['COMPILE_FOLDER'] = './compiled' # компиляция файлов

    # для проверки
    app.config['TEST_INPUT'] = "test_input.txt"   # Файл с входными данными
    app.config['TEST_OUTPUT'] = "test_output.txt" # Файл с ожидаемым результатом

    # импортируем маршруты
    from .routes import user_routes, admin_routes, file_routes
    app.register_blueprint(user_routes.bp) # маршруты юзеров
    app.register_blueprint(admin_routes.bp) # маршруты админа
    app.register_blueprint(file_routes.bp) # маршруты загрузки\проверки файлов

    return app