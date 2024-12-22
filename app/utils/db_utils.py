import sqlite3
from app.utils.key_utils import generate_uniq_keys

def get_users():
    with sqlite3.connect('VeritasDB.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT login, group_num, rating FROM verifyed_users")

    return cur.fetchall()


def get_keys_n_users_info():
    with sqlite3.connect("VeritasDB.db") as conn:
        cur = conn.cursor()

        dataForm = []

        task = """
            SELECT login, group_num, rating FROM verifyed_users
            """
        cur.execute(task)
        students_results = cur.fetchall()
        for elem in students_results:
            dataForm.append({"username": elem[0], "group_num": elem[1], "rating": elem[2]})
        task = " SELECT * FROM generated_keys "
        cur.execute(task)
        keys = cur.fetchall()
        dataForm = sorted(dataForm, key=lambda x: float(x["rating"]), reverse=True)
        max_rating = max([float(rate["rating"]) for rate in dataForm])
        dataForm = list(map(lambda x: {**x, "procent": round((float(x["rating"]) / max_rating)*100, 2)}, dataForm))

    return keys, max_rating, dataForm


def add_keys(number_of_keys):
    with sqlite3.connect("VeritasDB.db") as conn:
        cur = conn.cursor()
        task = " INSERT INTO generated_keys (key) VALUES (?) "
        for new_key in generate_uniq_keys(number_of_keys):
            cur.execute(task, (new_key,))
        conn.commit()


def delete_uniq_key(key):
    with sqlite3.connect('VeritasDB.db') as conn:
        cur = conn.cursor()
        task = " DELETE FROM generated_keys WHERE [key] = ? "
        cur.execute(task, (key, ))
        conn.commit()


def check_login(username):
    with sqlite3.connect('VeritasDB.db') as conn:
        cur = conn.cursor()
        req_db = "SELECT login, password FROM verifyed_users WHERE login = ?"
        cur.execute(req_db, (username,))
        user = cur.fetchone()

    return user


def register_user(username, group_num, password, generated_key):
    with sqlite3.connect('VeritasDB.db') as conn:
            cur = conn.cursor()

            req_db = "SELECT login, group_num FROM verifyed_users WHERE login = ? AND group_num = ?;"
 
            cur.execute(req_db, (username, group_num))
            user = cur.fetchone()
            if user is None:
                req_db = "SELECT * FROM generated_keys"
                cur.execute(req_db)
                keys = cur.fetchall()
                if generated_key in [k[1] for k in keys]:
                    req_db = "INSERT INTO verifyed_users (login, group_num, password, rating) VALUES (?, ?, ?, 0)"
                    cur.execute(req_db, (username, group_num, password,))
                    conn.commit()
                    req_db = " DELETE FROM generated_keys WHERE key = ? "
                    cur.execute(req_db, (generated_key, ))
                    conn.commit()
                    error_message = "Аккаунт зарегестрирован"
                else:
                    error_message = "Неправильный ключ"
            else:
                error_message = "Имя занято"

    return error_message

