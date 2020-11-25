import telebot
import DB
import secret

# token tg
bot = telebot.TeleBot(secret.TOKEN)
Keyboard_boss = telebot.types.ReplyKeyboardMarkup(True, False)
Keyboard_mid = telebot.types.ReplyKeyboardMarkup(True, False)
Keyboard_top = telebot.types.ReplyKeyboardMarkup(True, False)
Keyboard_choose = telebot.types.ReplyKeyboardMarkup(True, True)
Keyboard_start = telebot.types.ReplyKeyboardMarkup(True, True)
Keyboard_users = telebot.types.ReplyKeyboardMarkup(True, True)
Keyborad_retarget = telebot.types.ReplyKeyboardMarkup(True, True)
button_next = telebot.types.ReplyKeyboardMarkup(True, True)
Keyboard_boss.row('Cоздать задачу', 'Текущие задачи', 'Завершенные задачи', 'Удалить задачу')
Keyboard_mid.row('Просмотр задач', 'Переназначение задач', 'Завершение задания')
Keyboard_top.row('Просмотр задач', 'Завершение задания')
Keyboard_choose.row('Руководитель', 'Ведущий', 'Инженер')
Keyboard_start.row('Начать')
button_next.row('Продолжить')
Keyborad_retarget.row('Переназначить')


# This handler for command start, before writed command scanning the id user's, if id have in database, bot send hi-message,
# else asks write the user role and write user info in database.

@bot.message_handler(commands=['start'])
def start(message):
    if DB.id_filter(message.from_user.id) == []:
        msg = bot.send_message(message.chat.id,
                               'Добро пожаловать,' + message.from_user.first_name + ', выберите вашу должность:',
                               reply_markup=Keyboard_choose)
        bot.register_next_step_handler(msg, write_user)
    else:
        msg = bot.send_message(message.chat.id,
                               'Добро пожаловать,' + message.from_user.first_name + ', нажмите на кнопку,чтобы начать:',
                               reply_markup=Keyboard_start)
        bot.register_next_step_handler(msg, user_filter)


def write_user(message):
    user = [(message.from_user.last_name, message.text, message.from_user.id)]
    DB.write_user(user)
    msg = bot.send_message(message.chat.id, 'Вы успешно добавлены! Нажмите кнопку, чтобы начать:',
                           reply_markup=Keyboard_start)
    bot.register_next_step_handler(msg, user_filter)


@bot.message_handler(content_types=['text'])
# После определения роли, отправляем на ветку, читая роль.
def user_filter(message):
    """Определяет роль пользователя и отправляет на ветку пользователя"""
    mci = message.chat.id
    # print(message)

    if DB.read_role(message.from_user.id) == 'Руководитель':
        msg = bot.send_message(mci, 'Выберете вариант:', reply_markup=Keyboard_boss)
        bot.register_next_step_handler(msg, button_read)
    elif DB.read_role(message.from_user.id) == 'Ведущий':
        msg = bot.send_message(mci, 'Выберете вариант:', reply_markup=Keyboard_mid)
        bot.register_next_step_handler(msg, button_read)
    elif DB.read_role(message.from_user.id) == 'Инженер':
        msg = bot.send_message(mci, 'Выберете вариант:', reply_markup=Keyboard_top)
        bot.register_next_step_handler(msg, button_read)


# Функция чтения кнопок, отправляет на функцию выполнения действия в зависимости от выбранной кнопки.
# Если кнопка еще не разработана, возвращет на себя.
# Не выполнена отработка ошибочных действий, папример передан список задач для удаления, введен номер не из списка.
def button_read(message):
    idu = message.from_user.id
    mci = message.chat.id
    mt = message.text
    if mt == 'Текущие задачи':
        msg = bot.send_message(mci, 'Вот список текущих задач:')
        bot.send_message(mci, f"{DB.read_task(idu)}")
        bot.register_next_step_handler(msg, button_read)
    elif mt == 'Cоздать задачу':
        msg = bot.send_message(mci, 'Напишите вашу задачу:')
        bot.register_next_step_handler(msg, write_task)
    elif mt == 'Завершенные задачи':
        msg = bot.send_message(mci, f'Список завершенных задач:\n {DB.read_complete_task(idu)}')
        bot.register_next_step_handler(msg, button_read)
    elif mt == 'Просмотр задач':
        mci = message.chat.id
        msg = bot.send_message(mci,'Вот список текущих задач:')
        bot.send_message(mci, f'{DB.read_task(idu)}')
        bot.register_next_step_handler(msg, button_read)
    elif mt == 'Переназначение задач':
        msg = bot.send_message(mci, 'Чтобы переназначить задачу, нажмите на кнопку:', reply_markup=Keyborad_retarget)
        bot.register_next_step_handler(msg, reget_task)
    elif mt == 'Завершение задания':
        msg = bot.send_message(mci, 'Выберете, какую задачу вы хотите завершить:\n {}'.format(DB.read_no_task(idu)))
        bot.register_next_step_handler(msg, end_task)
    elif mt == 'Удалить задачу':
        msg = bot.send_message(mci, 'Напишите номер задачи, которую вы хотите удалить:'
                                    '\n {}'.format(DB.read_full_no_task()))
        bot.register_next_step_handler(msg, del_task)
    elif mt == 'Cформировать Excel отчет':
        bot.send_message(mci, 'EXCEL отчёт:')
        DB.excel_commit(idu)


    else:
        msg = bot.send_message(mci, 'Вы выбрали не верный вариант, пожалуйста, нажмите на одну из кнопок.')
        bot.register_next_step_handler(msg, button_read)

# Функция создания задачи, есть только у РУКОВОДИТЕЛЯ, записывает название задачи и отправляет на комент.
def write_task(message):
    mci = message.chat.id
    text = message.text
    DB.write_task(text)
    msg = bot.send_message(mci, 'Введите комментарий:')
    bot.register_next_step_handler(msg, write_comment_сup)

# Возможность для руководителя удалять задачи
def del_task(message):
    mci = message.chat.id
    mt = message.text
    DB.del_task(mt)
    msg = bot.send_message(mci, 'Задача удалена! Нажмите "Продолжить":', reply_markup=button_next)
    bot.register_next_step_handler(msg, user_filter)

# Запись комента для руководителя, выводит список ведущих,
# которым можно назначить задачу, перенаправляет на запись пользователя
def write_comment_сup(message):
    mci = message.chat.id
    text = message.text
    DB.write_comment(text)
    msg = bot.send_message(mci, 'Комментарий добавлен! Напишите исполнителя из списка:\n\n' + DB.list_users_mid())
    bot.register_next_step_handler(msg, write_user_for_task)


# Записывает назначеного пользователя на задачу, выдает кнопку, возвращающую на начало ветки.
def write_user_for_task(message):
    mci = message.chat.id
    text = message.text
    DB.write_worker_task(text)
    msg = bot.send_message(mci, 'Исполнитель выбран! Чтобы продолжить, нажмите на кнопку:', reply_markup=button_next)
    bot.register_next_step_handler(msg, user_filter)


# Функция выводит список текущих задач, учитывает роль пользователя, выводит комент.
def now_task(message):
    id_user = message.from_user.id
    mci = message.chat.id
    msg = bot.send_message(mci, 'Вот список текущих задач:')
    bot.send_message(mci, f"{DB.read_task(id_user)}")
    bot.register_next_step_handler(msg, user_filter)


# Перенаправление задачи для ВЕДУЩИХ
def reget_task(message):
    mci = message.chat.id
    idu = message.from_user.id
    msg = bot.send_message(mci, f'Напишите номер задачи, которую вы хотите переназначить из списка текущих в формате '
                                f'"№ Задачи, Фамилия адресанта":\n"№ Задачи"\n {DB.read_no_task(idu)}'
                                f'\n "Фамилия адресанта"\n {DB.list_users_top()} ')
    bot.register_next_step_handler(msg, comlete_reget_task)

# Выполняет переназначение задачи.
def comlete_reget_task(message):
    mci = message.chat.id
    mt = message.text
    DB.reget_task(mt)
    msg = bot.send_message(mci, "Задача успешно переназначена! Нажмите 'Продолжить:'", reply_markup=button_next)
    bot.register_next_step_handler(msg, user_filter)

#При выполнении операции завершения задачи ставит статус задачи "завершено" и предлагает вернуться в начало.
def end_task(message):
    mt = message.text
    mci = message.chat.id
    idu = message.from_user.id
    DB.comple_task(mt)
    msg = bot.send_message(mci, "Задача завершена! Нажмите 'Продолжить':", reply_markup=button_next)
    bot.register_next_step_handler(msg, user_filter)



# При ошибке подключения должен переподключаться! Уточнить верность.
if __name__ == '__main__':
    while True:
        try:
            bot.polling(True)
        except ConnectionError:
            print('Подключение отвалилось! Переподключаем!')
            bot.polling(True)

