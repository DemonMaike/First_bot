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
        # Теперь таблица таск склеивается с коментами по номеру комента
        result = [x for x in cur.execute('SELECT * FROM Task t JOIN Comments c ON t.No_Comments = c.No_Comments')]
        print(result)
        text = ''
        # Чуть чуть переделал
        # Пока не меняет id пользователей
        # Что за text?
        response_data = []
        for i in result:
            temp = []
            temp.append('Номер задачи: {}\n'.format(i[0]))
            temp.append('Назавание задачи: {}\n'.format(i[1]))
            temp.append('Выполнение: {}\n'.format(i[2]))
            idd = [x for x in cur.execute("""SELECT id_worker FROM Task WHERE No_task = {}""".format(i[0]))][0][0]
            name = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Id_Users = {}""".format(idd))][0][0]
            temp.append('Исполнитель: {}\n'.format(name))
            temp.append('Коментарии: {}\n\n'.format(i[6]))

            response_data.append(' '.join(temp))
        # поставил пробел , чтобы tg думал что строка непустая
        # Не очень понял, это ты для себя сделал чтобы видеть пустые сообщения от тг если нет строчки ?
        text = ' \n'.join(response_data)
    # Нужно выодить задачи для пользователей по их id на самом деле
    elif role == 'Ведущий':
        result = [x for x in cur.execute('SELECT * FROM Task t JOIN Comments c '
                                         'WHERE t.No_Comments = c.No_Comments AND id_worker = {} '.format(idu))]
        text = ''
        response_data = []
        for i in result:
            temp = []
            temp.append('Номер задачи: {}\n'.format(i[0]))
            temp.append('Назавание задачи: {}\n'.format(i[1]))
            temp.append('Выполнение: {}\n'.format(i[2]))
            idd = [x for x in cur.execute("""SELECT id_worker FROM Task WHERE No_task = {}""".format(i[0]))][0][0]
            name = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Id_Users = {}""".format(idd))][0][0]
            temp.append('Исполнитель: {}\n'.format(name))
            temp.append('Коментарии: {}\n\n'.format(i[6]))

            response_data.append(' '.join(temp))
            text = ' \n'.join(response_data)
    elif role == 'Инженер':
        result = [x for x in cur.execute('SELECT * FROM Task t JOIN Comments c ON t.No_Comments = c.No_Comments '
                                         'WHERE id_worker = {} '.format(idu))]
        text = ''
        response_data = []
        for i in result:
            temp = []
            temp.append('Номер задачи: {}\n'.format(i[0]))
            temp.append('Назавание задачи: {}\n'.format(i[1]))
            temp.append('Выполнение: {}\n'.format(i[2]))
            idd = [x for x in cur.execute("""SELECT id_worker FROM Task WHERE No_task = {}""".format(i[0]))][0][0]
            name = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Id_Users = {}""".format(idd))][0][0]
            temp.append('Исполнитель: {}\n'.format(name))
            temp.append('Коментарии: {}\n\n'.format(i[6]))

            response_data.append(' '.join(temp))
            text = ' \n'.join(response_data)
    else:
        text = 'Роль не определена'

    return text


# Запись задачи, при создании задачи ставим Comlpete = 'Не выполнено'
def write_task(msg):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    db_data = [(msg,)]
    result = cur.executemany("""INSERT INTO Task(Task_Name) VALUES(?)""", db_data)
    last_task_no = [x for x in cur.execute("""SELECT No_task FROM Task WHERE Task_Name = '{}' """.format(msg))]
    print(last_task_no)
    cur.execute("""UPDATE Task SET Complete = 'Не выполнено' WHERE No_task = {}""".format(last_task_no[0][0]))
    conn.commit()


# Запись комента
def write_comment(msg):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    db_data = [(msg,)]
    cur.executemany("""INSERT INTO Comments(Comment) VALUES(?) """, db_data)
    set_no_comments = [x for x in cur.execute("""SELECT No_Comments FROM Comments""")]
    end_index = len(set_no_comments) - 1
    no_end_comments = set_no_comments[end_index][0]
    all = [x for x in cur.execute("""SELECT * FROM Task""")]
    index_end_task = len(all) - 1
    end = [x for x in cur.execute("""SELECT No_task FROM Task""")]
    end_no_task = end[index_end_task][0]
    cur.execute("""UPDATE Task SET No_Comments = {} WHERE No_Task = {}""".format(no_end_comments, end_no_task))
    conn.commit()


# Возвращает Фамилию юзера по id
def id_filter(idu):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    result = [x for x in cur.execute("SELECT User_Name FROM Users WHERE Id_Users = {} ".format(idu))]
    return result


# Записывает юзера, Фамлию, Роль, id
def write_user(user):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    cur.executemany("""INSERT INTO Users(User_Name, Role, Id_Users) VALUES(?, ?, ?) """, user)
    conn.commit()


# Читает роль по id.
def read_role(idu):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    result = [x for x in cur.execute("""SELECT Role FROM Users WHERE Id_Users = {} """.format(idu))]
    conn.commit()
    return result[0][0]


# Возвращает строку с фамилиями ведущих из БД.
def list_users_mid():
    conn = sqlite3.connect(secret.DB)
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
    conn = sqlite3.connect(secret.DB)
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
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    all = [x for x in cur.execute("""SELECT * FROM Task""")]
    index_end_task = len(all) - 1
    end = [x for x in cur.execute("""SELECT No_task FROM Task""")]
    end_no_task = end[index_end_task][0]
    id_bd = [x for x in conn.execute("""SELECT Id_Users FROM Users WHERE User_Name = '{}'""".format(user_name))]
    id_worker = id_bd[0][0]
    result = cur.execute("""UPDATE Task SET id_worker = '{}'  WHERE No_task = {}  """.format(id_worker, end_no_task))
    conn.commit()

# Первый номер задачи имеет лишний пробел, надо разобраться и поправить
def read_no_task(idu):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    no_task_user = [x for x in cur.execute("""SELECT No_Task FROM Task WHERE id_worker = {}""".format(idu))]
    data = []
    for i in no_task_user:
        temp = []
        temp.append('{}'.format(i[0]))
        data.append("".join(temp))
    text = '\n'.join(data)
    return text

def read_full_no_task():
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    no_task_user = [x for x in cur.execute("""SELECT No_Task FROM Task""")]
    data = []
    for i in no_task_user:
        temp = []
        temp.append('{}'.format(i[0]))
        data.append("".join(temp))
    text = '\n'.join(data)
    return text


def comple_task(msg):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()
    print(msg)
    cur.execute("""UPDATE Task SET Complete = 'Выполнено' WHERE No_task = {}""".format(msg))
    conn.commit()

def read_complete_task(idu):
    conn = sqlite3.connect(secret.DB)
    cur = conn.cursor()

    role = [x for x in cur.execute('SELECT Role FROM Users WHERE Id_Users = {}'.format(idu))][0][0]

    if role == 'Руководитель':
        result = [x for x in cur.execute("SELECT * FROM Task t JOIN Comments c ON t.No_Comments = c.No_Comments"
                                         " WHERE Complete = 'Выполнено'")]
        print(result)
        response_data = []
        for i in result:
            temp = []
            temp.append('Номер задачи: {}\n'.format(i[0]))
            temp.append('Назавание задачи: {}\n'.format(i[1]))
            temp.append('Выполнение: {}\n'.format(i[2]))
            idd = [x for x in cur.execute("""SELECT id_worker FROM Task WHERE No_task = {}""".format(i[0]))][0][0]
            name = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Id_Users = {}""".format(idd))][0][0]
            temp.append('Исполнитель: {}\n'.format(name))
            temp.append('Коментарии: {}\n\n'.format(i[6]))

            response_data.append(' '.join(temp))
        text = ' \n'.join(response_data)
    elif role == 'Ведущий':
        result = [x for x in cur.execute('SELECT * FROM Task t JOIN Comments c ON t.No_Comments = c.No_Comments '
                                         'WHERE id_worker = {} AND Complete = "Выполнено" '.format(idu))]
        text = ''
        response_data = []
        for i in result:
            temp = []
            temp.append('Номер задачи: {}\n'.format(i[0]))
            temp.append('Назавание задачи: {}\n'.format(i[1]))
            temp.append('Выполнение: {}\n'.format(i[2]))
            idd = [x for x in cur.execute("""SELECT id_worker FROM Task WHERE No_task = {}""".format(i[0]))][0][0]
            name = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Id_Users = {}""".format(idd))][0][0]
            temp.append('Исполнитель: {}\n'.format(name))
            temp.append('Коментарии: {}\n\n'.format(i[6]))
            response_data.append(' '.join(temp))
            text = ' \n'.join(response_data)
    elif role == 'Инженер':
        result = [x for x in cur.execute('SELECT * FROM Task t JOIN Comments c ON t.No_Comments = c.No_Comments '
                                         'WHERE id_worker = {} AND Complete = "Выполнено" '.format(idu))]
        text = ''
        response_data = []
        for i in result:
            temp = []
            temp.append('Номер задачи: {}\n'.format(i[0]))
            temp.append('Назавание задачи: {}\n'.format(i[1]))
            temp.append('Выполнение: {}\n'.format(i[2]))
            idd = [x for x in cur.execute("""SELECT id_worker FROM Task WHERE No_task = {}""".format(i[0]))][0][0]
            name = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Id_Users = {}""".format(idd))][0][0]
            temp.append('Исполнитель: {}\n'.format(name))
            temp.append('Коментарии: {}\n\n'.format(i[6]))

            response_data.append(' '.join(temp))
            text = ' \n'.join(response_data)
    else:
        text = 'Роль не определена'

    return text

def top_list():
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    result = [x for x in cur.execute("""SELECT User_Name FROM Users WHERE Role = 'Инженер'""")]
    response_data =[]
    for i in result:
        response_data.append('{}'.format(i[0]))
    text = '\n'.join(response_data)
    return text

def reget_task(msg):
    info = msg.split(', ')
    print(info)
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    id_reget_user = [x for x in cur.execute("""SELECT Id_Users FROM Users WHERE User_Name = '{}' """.format(info[1]))]
    print(id_reget_user)
    cur.execute("""UPDATE Task SET id_worker = {} WHERE No_task = {}  """.format(id_reget_user[0][0], info[0]))
    conn.commit()

def del_task(no_task):
    conn = sqlite3.connect('FGMG.db')
    cur = conn.cursor()
    cur.execute("""DELETE FROM Task WHERE No_task = {} """.format(int(no_task)))
    conn.commit()