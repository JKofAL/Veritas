from flask import Blueprint, render_template, session, redirect, request, url_for, current_app
from app.utils.db_utils import get_keys_n_users_info, add_keys, delete_uniq_key, check_login_admin

# обращаемся к приложению и создаём blueprint
bp = Blueprint('admin_routes', __name__)


@bp.route('/admin', methods=["GET", "POST"]) # исполняется при переходе на /admin
def admin_log():
    if session.get('logged_in_admin'): # проверяем куки на вход админа
        return redirect(url_for('admin_routes.admin_panel')) # перенаправляем в админскую панель
    else:
        if request.method == "POST":
            dataForm = check_login_admin(request.form.get('login'), request.form.get('password'))
            # ('login', 'group_num1,group_num2', 'password')
            if dataForm:
                session['logged_in_admin'] = True # сохраняем вход
                session['group_nums'] = dataForm[1].split(',') # ['group_num1', 'group_num2']
                return redirect("/admin-panel") # перенаправляем в админскую панель
            else:
                return render_template("admin-log.html")     
        return render_template("admin-log.html")


@bp.route('/admin-panel', methods=["GET", "POST"])
def admin_panel():
    # админ панель доступна по ссылке /admin или /admin-panel, если юзер подтвердил вход
    # сделана для проверки студентов для преподавателя
    if session.get('logged_in_admin'): # если в куки есть подтверждённый вход в админку
        
        # находим в бд уникальные ключи, максимальный рейтинг среди студентов и вся информация о студентах
        keys, max_rating, dataForm = get_keys_n_users_info(session['group_nums'])

        # из списка ((id, key), (id, key)) делаем (key, key)
        keys = [i[1] for i in keys]
        if request.method == "POST":
            # получаем количество необходимых ключей
            number_of_keys = int(request.form.get("key_count"))
            add_keys(number_of_keys) # генерируем ключи и добавляем их в бд
            return redirect(url_for("admin_routes.admin_panel")) # перезагружаем таблицу в методе GET
        return render_template("admin-panel.html", dataForm=dataForm, generated_keys=keys, max_rating=max_rating)
    else:
        return redirect('/admin') # перенаправляем на авторизацию админа если в куки нет информации о входе


@bp.route('/delete-key', methods=["POST"])
def delete_key():
    
    key_to_del = request.form.get("key-to-delete")

    delete_uniq_key(key_to_del)

    return redirect(url_for('admin_routes.admin_panel'))