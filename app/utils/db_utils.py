import sqlite3
from app.utils.key_utils import generate_uniq_keys

def get_users():
    with sqlite3.connect('VeritasDB.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT login, group_num, rating FROM verifyed_users")

    return cur.fetchall()


def get_keys_n_users_info(groups):
    with sqlite3.connect("VeritasDB.db") as conn:
        cur = conn.cursor()

        dataForm = []
        students_results = []
        for group in groups:
            task = """
                SELECT login, group_num, rating FROM verifyed_users WHERE group_num = ?
                """
            cur.execute(task, (group, ))
            students_results_group = cur.fetchall()
            if students_results_group:
                for row in students_results_group:
                    students_results.append(row)
        for elem in students_results:
            dataForm.append({"username": elem[0], "group_num": elem[1], "rating": elem[2]})
        task = " SELECT * FROM generated_keys "
        cur.execute(task)
        keys = cur.fetchall()
        if students_results:
            dataForm = sorted(dataForm, key=lambda x: float(x["rating"]), reverse=True)
            max_rating = max([float(rate["rating"]) for rate in dataForm])
            dataForm = list(map(lambda x: {**x, "procent": round((float(x["rating"]) / max_rating)*100, 2)}, dataForm))
        else:
            max_rating=0
            dataForm=[]
            

    return keys, max_rating, dataForm


def get_users_info_for_profile(username):
    with sqlite3.connect("VeritasDB.db") as conn:
        cur = conn.cursor()

        dataForm = []

        req_db = "SELECT group_num FROM verifyed_users WHERE login = ?"

        cur.execute(req_db, (username, ))

        group_num = cur.fetchone()[0]

        task = """
            SELECT login, rating FROM verifyed_users WHERE group_num = (?)
            """
        cur.execute(task, (group_num, ))
        students_results = cur.fetchall()
        print(students_results)
        for elem in students_results:
            dataForm.append({"username": elem[0], "rating": elem[1]})
        if students_results:
            print(dataForm)
            dataForm = sorted(dataForm, key=lambda x: float(x["rating"]), reverse=True)
            print(dataForm)
            max_rating = max([float(rate["rating"]) for rate in dataForm])
            dataForm = list(map(lambda x: {**x, "procent": round((float(x["rating"]) / max_rating)*100, 2)}, dataForm))
            print(dataForm)
        else:
            dataForm=[]
            

    return dataForm, group_num


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

            req_db = "SELECT login, group_num FROM verifyed_users WHERE login = ?"
 
            cur.execute(req_db, (username, ))
            user = cur.fetchone()
            if user is None:
                req_db = "SELECT * FROM generated_keys"
                cur.execute(req_db)
                keys = cur.fetchall()
                if generated_key in [k[1] for k in keys]:
                    req_db = "INSERT INTO verifyed_users (login, group_num, password) VALUES (?, ?, ?)"
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


def write_test_results(login, results):
    with sqlite3.connect('VeritasDB.db') as conn:
            cur = conn.cursor()

            req_db = "SELECT * FROM verifyed_users WHERE login= ?"

            cur.execute(req_db, (login,))

            old_results = cur.fetchone()
            res = []
            for i in range(len(results)):
                new_res = results[i]["rating"]
                old_res = old_results[4+i]
                res.append(new_res if new_res>int(old_res) else old_res)
            
            res.append(sum(res))
            req_db = "UPDATE verifyed_users SET lab1=?, lab2=?, lab3=?, lab4=?, rating=? WHERE login = ?"

            cur.execute(req_db, (*res, login))
            conn.commit()


def check_login_admin(login, password):
    with sqlite3.connect('VeritasDB.db') as conn:
        cur = conn.cursor()
        req_db = "SELECT login, group_nums, password FROM verifyed_admins WHERE login = ? AND password = ?"
        cur.execute(req_db, (login, password, ))
        user = cur.fetchone()

    return user



