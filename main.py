from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import aspose.pdf as ap
from aiogram.types import InputFile

bot = Bot('6466520874:AAHs2JLdpoNA5BSdQUzwxLjq4JG5-ro0PAM')

dp = Dispatcher(bot)
db_name = 'users.db'

keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Створити розсилку'))

def connect_to_db():
    return sqlite3.connect(db_name)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    id_user = message.from_user.id
    await message.answer('Натисни на кнопку щоб створити розсилку!', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Створити розсилку')
async def create_broadcast(message: types.Message):
    db_connection = sqlite3.connect(db_name)
    try:
        cursor = db_connection.cursor()
        cursor.execute('SELECT NA FROM user WHERE NA IS NOT NULL')
        app_num_from_db = cursor.fetchall()
    finally:
        db_connection.close()
    if app_num_from_db:
        app_num = [number[0] for number in app_num_from_db]
        await message.answer('Оберіть квартиру:', reply_markup=get_apartments_keyboard(app_num))
    else:
        await message.answer('Немає доступних квартир.')
    

def get_apartments_keyboard(apartment_numbers):
    global number
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for number in apartment_numbers:
        button = KeyboardButton(str(number))
        keyboard.add(button)
    return keyboard

@dp.message_handler(lambda message: message.text.isdigit())
async def process_apartment_choice(message: types.Message):
    global chosen_apartment
    chosen_apartment = int(message.text)
    await message.answer(f"Ви обрали квартиру {chosen_apartment}. Надішліть мені текст розсилки.")

def create_pdf(chosen_apartment):
    document = ap.Document()

    page = document.pages.add()
    text_fragment = ap.text.TextFragment(f'Квитанція {chosen_apartment}')
    page.paragraphs.add(text_fragment)

    document.save(f'broadcast-{chosen_apartment}.pdf')

@dp.message_handler(lambda message: chosen_apartment is not None)
async def process_broadcast_text(message: types.Message):
    global text_for_broadcast
    text_for_broadcast = message.text

    db_connection = sqlite3.connect('users.db')
    try:
        cursor = db_connection.cursor()
        cursor.execute('SELECT id FROM user WHERE NA = ?', (chosen_apartment,))
        result = cursor.fetchall()

        for row in result:
            user_id = row[0]
            create_pdf(chosen_apartment)
            await bot.send_message(user_id, f"Розсилка для квартири {chosen_apartment}:\n\n{text_for_broadcast}")
            await bot.send_document(user_id, document=InputFile(f'./broadcast-{chosen_apartment}.pdf'))

    finally:
        db_connection.close()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
