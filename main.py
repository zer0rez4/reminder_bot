import logging, sys, asyncio, sqlite3, datetime, os
#import matplotlib.pyplot as plt
import numpy as np

#my own class
from db_classes import Timechanger
from graph_classes import Graph

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Dispatcher, Bot, types, F

from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton


token = ""
start_time = 0

dp = Dispatcher()
bot = Bot(token)
sheduler = AsyncIOScheduler()


main_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Статистика', callback_data='stat'), InlineKeyboardButton(text='Время напоминания', callback_data='choose_time')], [InlineKeyboardButton(text='Начать занятие', callback_data='start_lesson')]])
back_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='back')]])
stat_period_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='День', callback_data='stat_day'), InlineKeyboardButton(text='Неделя', callback_data='stat_week'), InlineKeyboardButton(text='Месяц', callback_data='stat_month')], [InlineKeyboardButton(text='Всё время', callback_data='stat_all_time')], [InlineKeyboardButton(text='Назад', callback_data='back')]])
stat_back_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='stat_back')]])
stat_all_graph_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='stat_back'), InlineKeyboardButton(text='Показать на графике', callback_data='all_time_graph')]])
stat_show_month_graph_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='stat_back'), InlineKeyboardButton(text='Показать на графике', callback_data='show_month_graph')]])
stat_show_week_graph_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='stat_back'), InlineKeyboardButton(text='Показать на графике', callback_data='show_week_graph')]])
stat_delete_photo = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Закрыть', callback_data='close_photo')]])
start_study_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Начать занятие', callback_data='start_lesson')], [InlineKeyboardButton(text='Назад', callback_data='back')]])
finish_study_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Закончить занятие', callback_data='finish_lesson')]])
change_time_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Изменить время', callback_data='change_reminde_time')], [InlineKeyboardButton(text='Назад', callback_data='back')]])
choose_time_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='8:00', callback_data='cht_8'), InlineKeyboardButton(text='10:00', callback_data='cht_10'), InlineKeyboardButton(text='12:00', callback_data='cht_12')], [InlineKeyboardButton(text='18:00', callback_data='cht_18'), InlineKeyboardButton(text='20:00', callback_data='cht_20'), InlineKeyboardButton(text='22:00', callback_data='cht_22')], [InlineKeyboardButton(text='Назад', callback_data='back')]])


@dp.message(CommandStart())
async def start(message: Message):
    ddn = datetime.datetime.now()

    conn = sqlite3.connect(r"ebn_bot/db.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='t_{message.from_user.id}'")
    if cursor.fetchone() is None:
        cursor.execute(f"CREATE TABLE t_{message.from_user.id} (day TEXT PRIMARY KEY, learn_time INTEGER)")
        cursor.execute(f"INSERT INTO t_{message.from_user.id} VALUES ('{ddn.date()}', 0)")

    #дописать сюда
    cursor.execute(f"SELECT learn_time FROM t_{message.from_user.id} WHERE day={ddn.date()}")
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO t_{message.from_user.id} VALUES ('{ddn.date()}', 0)")

    conn.commit()
    conn.close()

    await message.answer("Добро пожаловать", reply_markup=main_markup)
@dp.callback_query(F.data == 'back')
async def back(callback_data: CallbackQuery):
    await callback_data.message.edit_text('Добро пожаловать', reply_markup=main_markup)


@dp.callback_query(F.data == 'stat')
@dp.callback_query(F.data == 'stat_back')
async def person_stats(callback_data: CallbackQuery):
    await callback_data.message.edit_text("Выберите период", reply_markup=stat_period_markup)


@dp.callback_query(F.data == 'stat_day')
async def stat_day(callback_data: CallbackQuery):
    connection = sqlite3.connect(r"ebn_bot/db.db")
    cursor = connection.cursor()
    
    cursor.execute(f"SELECT learn_time FROM t_{callback_data.message.chat.id} WHERE day = '{datetime.datetime.now().date()}'")
    result = cursor.fetchone()[0]

    connection.close()

    await callback_data.message.edit_text(f'Сегодня вы занимались: {result // 60} часов, {result % 60} минут', reply_markup=stat_back_markup)

#недельный график
@dp.callback_query(F.data == 'stat_week') 
async def stat_week(callback_data: CallbackQuery):
    week_stat_list = []
    day = []
    
    connection = sqlite3.connect(r"ebn_bot/db.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM t_{callback_data.message.chat.id} ORDER BY day DESC LIMIT 7")
    result = cursor.fetchall()[::-1]

    connection.close()

    for i in result:
        day.append(i[0][5::])
        week_stat_list.append(i[1])

    await callback_data.message.edit_text(f"За последнюю неделю вы занимались: {sum(week_stat_list) // 60} часов, {sum(week_stat_list) % 60} минут\nВ среднем вы занимаетесь по {round(np.average(week_stat_list), 1)} минут в день", reply_markup=stat_show_week_graph_markup)


@dp.callback_query(F.data == 'show_week_graph')
async def show_week_graph(callback_data: CallbackQuery):
    Graph().draw_graph(user_id=callback_data.message.chat.id, days=7)
    photo = FSInputFile(f'g_{callback_data.message.chat.id}.png')
    await callback_data.message.answer_photo(photo, has_spoiler=True, reply_markup=stat_delete_photo)
    os.remove(f'g_{callback_data.message.chat.id}.png')


#месячный график
@dp.callback_query(F.data == 'stat_month')
async def stat_month(callback_data: CallbackQuery):
    day = []
    month_stat_list = []

    connection = sqlite3.connect(r"ebn_bot/db.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM t_{callback_data.message.chat.id} ORDER BY day DESC LIMIT 30")
    result = cursor.fetchall()

    connection.close()

    for i in result:
        day.append(i[0][5::])
        month_stat_list.append(i[1])

    await callback_data.message.edit_text(f"В последние 30 дней вы занимались: {sum(month_stat_list) // 60} часов, {sum(month_stat_list) % 60} минут\nВ среднем вы занимаетесь по {round(np.average(month_stat_list), 1)} минут в день", reply_markup=stat_show_month_graph_markup)


@dp.callback_query(F.data == 'show_month_graph')
async def show_month_graph(callback_data: CallbackQuery):
    Graph().draw_graph(user_id=callback_data.message.chat.id, days=30)
    photo = FSInputFile(f'g_{callback_data.message.chat.id}.png')
    await callback_data.message.answer_photo(photo, has_spoiler=True, reply_markup=stat_delete_photo)
    os.remove(f'g_{callback_data.message.chat.id}.png')

#всё время график
@dp.callback_query(F.data == 'stat_all_time')
async def stat_all_time(callback_data: CallbackQuery):
    stat_list = []
    
    connection = sqlite3.connect(r"ebn_bot/db.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM t_{callback_data.message.chat.id}")
    all_stat = cursor.fetchall()

    connection.close()

    for i in all_stat:
        stat_list.append(i[1])

    await callback_data.message.edit_text(f'Общее время занятий: {sum(stat_list) // 60} часов, {sum(stat_list) % 60} минут\nВ среднем вы занимаетесь по {round(np.average(stat_list), 1)} минут в день', reply_markup=stat_all_graph_markup)


@dp.callback_query(F.data == 'all_time_graph')
async def show_graph_all_time(callback_data: CallbackQuery):
    Graph().draw_graph_all_time(user_id=callback_data.message.chat.id)

    photo = FSInputFile(f'g_{callback_data.message.chat.id}.png')
    await callback_data.message.answer_photo(photo, has_spoiler=True, reply_markup=stat_delete_photo)
    os.remove(f'g_{callback_data.message.chat.id}.png')
@dp.callback_query(F.data == 'close_photo')
async def close_photo(callback_data: types.CallbackQuery):
    await callback_data.message.delete()


#всё что связано с напоминанием (кроме отправленя сообщения)
@dp.callback_query(F.data == 'choose_time')
async def choose_time(callback_data: CallbackQuery):
    conn = sqlite3.connect(r'ebn_bot/db.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT time FROM remind_table WHERE id = '{callback_data.message.chat.id}'")
    try:
        result = cursor.fetchall()[0][0]
        await callback_data.message.edit_text(f"Время вашего напоминания: {result}:00", reply_markup=change_time_markup)
    except:
        cursor.execute(f"SELECT * FROM remind_table WHERE id = '{callback_data.message.chat.id}'")
        if cursor.fetchone() is None:
            cursor.execute(f"INSERT INTO remind_table VALUES ('{callback_data.message.chat.id}', '20')")
        conn.commit()

        await callback_data.message.edit_text("Вы ещё не устновили напоминание", reply_markup=change_time_markup)
    finally:
        conn.close()

@dp.callback_query(F.data == 'change_reminde_time')
async def change_time(callback_data: CallbackQuery):
    await callback_data.message.edit_text(f"Выберите время напоминания", reply_markup=choose_time_markup)

#изменение врмени напоминания
@dp.callback_query(F.data.startswith('cht_'))
async def new_reminde_time(callback_data: CallbackQuery):
    Timechanger().change_reminde_time_a(remind_time=callback_data.data[4::], user_id=callback_data.message.chat.id)
    await callback_data.message.edit_text(f'Время вашего напоминания - {callback_data.data[4::]}:00',reply_markup=back_markup)

#начало/конец занятия
@dp.callback_query(F.data == 'start_lesson')
async def start_lesson(callback_data: CallbackQuery):
    global start_time
    start_time = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
    await callback_data.message.edit_text("Вы начали занятие", reply_markup=finish_study_markup)
    await callback_data.message.answer("Воспользуйтесь этими кнопками", reply_markup=main_markup)

@dp.callback_query(F.data == 'finish_lesson')
async def finish_lesson(callback_data: CallbackQuery):
    global start_time
    lesson_duration = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute - start_time

    connection = sqlite3.connect(r"ebn_bot/db.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT learn_time FROM t_{callback_data.message.chat.id} WHERE day = '{datetime.datetime.now().date()}'")
    today_time = cursor.fetchone()[0]
    
    today_time += lesson_duration
    cursor.execute(f"UPDATE t_{callback_data.message.chat.id} SET learn_time = {today_time} WHERE day = '{datetime.datetime.now().date()}'")

    connection.commit()
    connection.close()

    await callback_data.message.edit_text(f'Вы занимались: {lesson_duration} минут\nОбщее время занятий за сегодня: {today_time} минут')
    await asyncio.sleep(5)
    await callback_data.message.delete()



def create_new_day():
    ddn = datetime.datetime.now()

    connection = sqlite3.connect(r"ebn_bot/db.db")
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 't_%'")
    tables = cursor.fetchall()
    
    #создание записи в каждую таблицу
    for i in tables:
        cursor.execute(f"INSERT INTO {i[0]} VALUES ('{ddn.date()}', 0)")

    connection.commit()
    connection.close()


#функция не работает блять !!! (или работает, я уже нихуя не понимаю)
async def create_remind_message(remind_time):
    conn = sqlite3.connect(r"enb_bot/db.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT id FROM remind_table WHERE time = '{remind_time}'")
    result = cursor.fetchall()
    
    conn.close()

    for i in result:
        await bot.send_message(chat_id=i, text='Ваше время пришло', reply_markup=start_study_markup)


async def main():
    sheduler.add_job(func=create_new_day, trigger='cron', hour='0')
    for i in ['8', '10', '12', '18', '20', '22']:
        sheduler.add_job(func=lambda: create_remind_message(i),trigger='cron', hour=i)
    sheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

