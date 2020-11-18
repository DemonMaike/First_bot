import sqlite3
import secret

# Показывает текущие задачи, надо сделать разветвление по user_id, чтобы в зависимости от id каждый видел свои задачи,
# наверное проще решить это посредством корректировки структуры самой БД.
def read_task(idu):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()

    # Сначала нужно определить роль
    # вах какой костыль
    # получили вот такого очкарика  [0][0]
    role = [x for x in cur.execute('SELECT Role FROM Users WHERE Id_Users = {}'.format(idu))][0][0]

    # Выводим все задачи - кажется жестко(например есди задач 100)
    # 100 задач не будет, задачи будут закрываться, а здесь выводим актуальные, завершенные задачи смотряться в
    # отдельном блоке, и там будет лимит на 10-20 последних заверешнных задач, так что тут все ок.
    if role == 'Руководитель':
        result = [x for x in cur.execute('SELECT * FROM Task')]
        text = '22'
        # Чуть чуть переделал
        # Пока не меняет id пользователей
        # Что за text?
        response_data = []
        for i in result:
            temp = []
            temp.append('Номер задачи: {}\n'.format(i[0]))
            temp.append('Назавание задачи: {}\n'.format(i[1]))
            temp.append('Выполнение: {}\n'.format(i[2]))
            result = [x for x in cur.execute('SELECT User_Name FROM Users WHERE Id_Users = {}'.format(i[3]))]
            if result:
                name = result[0][0]
            else:
                name = "конь в пальто"
            temp.append('Исполнитель: {}\n'.format(name))
            temp.append('Коментарии:{}\n'.format(i[4]))

            response_data.append(' '.join(temp))
        # поставил пробел , чтобы tg думал что строка непустая
        # Не очень понял, это ты для себя сделал чтобы видеть пустые сообщения от тг если нет строчки ?
        text = ' \n'.join(response_data)

    # Нужно выодить задачи для пользователей по их id на самом деле
    elif role == 'Ведущий':
        result = [x for x in cur.execute('SELECT * FROM Task t JOIN Users u ON t. ')]
        print(result)
        string = 0
        text = ''
        for i in range(len(result)):
            result_print = 'Номер задачи: {}\nНазавание задачи: {}\nВыполнение: {}\n Исполнитель: {}\n Коментарии:{}\n'. \
                format(result[string][0], result[string][1], result[string][2], result[string][3], result[string][4])
            text = text + result_print
            string += 1

    elif role == 'Инженер':
        result = [x for x in cur.execute('SELECT * FROM Task')]
        string = 0
        text = ''
        for i in range(len(result)):
            result_print = 'Номер задачи: {}\nНазавание задачи: {}\nВыполнение: {}\n Исполнитель: {}\n Коментарии:{}\n'. \
                format(result[string][0], result[string][1], result[string][2], result[string][3], result[string][4])
            text = text + result_print
            string += 1
    else:
        text = 'Роль не определена'

    return text


# Запись задачи.
def write_task(msg):
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    db_data = [(msg,)]
    result = cur.executemany("""INSERT INTO Task(Task_Name) VALUES(?)""", db_data)
    conn.commit()


# Запись комента
def write_comment(msg):
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    db_data = [(msg,)]
    cur.executemany("""INSERT INTO Comments(Comment) VALUES(?) """, db_data)
    conn.commit()


# Возвращает Фамилию юзера по id
def id_filter(idu):
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    result = [x for x in cur.execute("SELECT User_Name FROM Users WHERE Id_Users = {} ".format(idu))]
    return result


# Записывает юзера, Фамлию, Роль, id
def write_user(user):
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    cur.executemany("""INSERT INTO Users(User_Name, Role, Id_Users) VALUES(?, ?, ?) """, user)
    conn.commit()


# Читает роль по id.
def read_role(idu):
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    result = [x for x in cur.execute("""SELECT Role FROM Users WHERE Id_Users = {} """.format(idu))]
    conn.commit()
    return result[0][0]


# Возвращает строку с фамилиями ведущих из ТГ.
def list_users_mid():
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    result = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Role = 'Ведущий' """)]
    string = 0
    text = ''
    for i in range(len(result)):
        result_print = '{}\n'.format(result[string][0])
        text = text + result_print
        string += 1
    return text


# Возвращает строку с фамилиями инженеров.
def list_users_top():
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    result = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Role = 'Инженер' """)]
    string = 0
    text = ''
    for i in range(len(result)):
        result_print = '{}\n'.format(result[string][0])
        text = text + result_print
        string += 1
    return text


# Принимает имя исполнителя, записывает в последнюю задачу.
def write_worker_task(user_name):
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    all = [x for x in cur.execute("""SELECT * FROM Task""")]
    index_end_task = len(all) - 1
    end = [x for x in cur.execute("""SELECT No_task FROM Task""")]
    end_no_task = end[index_end_task][0]
    id_bd = [x for x in conn.execute("""SELECT Id_Users FROM Users WHERE User_Name = '{}'""".format(user_name))]
    id_worker = id_bd[0][0]
    result = cur.execute("""UPDATE Task SET id_worker = '{}'  WHERE No_task = {}  """.format(id_worker, end_no_task))
    conn.commit()


