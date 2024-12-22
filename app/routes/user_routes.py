from flask import Blueprint, render_template, session, redirect, request
from app.utils.db_utils import check_login, register_user

bp = Blueprint('user_routes', __name__)


@bp.route('/')
def index():
    ''' Главная страница, на ней отображается статус входа в аккаунт, поля для загрузки 
    лабораторных и отправки на проверку '''
    user = session.get('user') # проверка входа в аккаунт
    session['user'] = user # для корректной работы куки
    session['error_message'] = None # если во время логина была ошибка, после логина 
    # она уберётся, только если мы сами её уберём
    return render_template('index.html', user=user)


@bp.route('/login', methods=["GET", "POST"])
def login_page():
    ''' форма логина пользователя '''
    error_message = session.get('error_message')

    if request.method == 'POST':

        username = request.form.get('login')
        password = request.form.get('password')

        user = check_login(username) # возвращает (username, password) из бд

        if user is None:
            error_message = "Неправильный логин"
        elif user[1] != password:
            error_message = "Неправильный пароль"
        else:
            session['user'] = username
            session['error_message'] = None
            return redirect('/')

    return render_template('login.html', error_message = error_message)


@bp.route('/reg', methods=["GET", "POST"])
def reg_page():
    ''' форма регистрации пользователя с полями
     Логин :: str;
     Номер группы :: str;
     Пароль :: str;
     Ключ :: str;
    Ключ выдаётся преподавателем, генерируется в админской панели.
    Все данные обрабатываются в db_utls и записываются при
    успешной прверке '''
    error_message = None

    if request.method == 'POST':

        username = request.form.get('login')
        group_num = request.form.get('group_num')
        password = request.form.get('password')
        generated_key = request.form.get('key')
        
        error_message = register_user(username, group_num, password, generated_key)

        session['error_mesage'] = error_message

        if error_message == "Аккаунт зарегестрирован":
            return redirect('/login')

    return render_template('reg.html', error_message=error_message)
