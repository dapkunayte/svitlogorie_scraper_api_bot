"""
Бот
"""
from telebot.async_telebot import AsyncTeleBot
from telebot.async_telebot import types
import re
bot = AsyncTeleBot('5603610049:AAEkpFrDrZVRei_ietByPl8VLCzvJ7nGVsk')
import requests
import json

categories = ["Творожные сырки", "Творожные палочки", "Масса творожная", "Творог", "Растительное молоко",
              "Молоко и трубочки для молока", "Кефир", "Сливки", "Сметана и соусы", "Сливочное масло",
              "Сыры", "Сгущенное молоко", "Трубочки, орешки и суфле", "Мороженое порционное", "Мороженое семейное",
              "Хлебцы экструзионные", "Сушки"]


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    for category in categories:
        markup.add(types.InlineKeyboardButton(category,callback_data=category))
    await bot.send_message(message.chat.id,"Все категории:",reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in categories)
async def get_category_product(call):
    response = requests.get(f"http://127.0.0.1:8000/products_categories_full/{call.data.replace(' ','_')}")
    products = response.json()
    markup1 = types.InlineKeyboardMarkup()
    markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup2.add(types.KeyboardButton('/start'))
    for product in products:
        markup1.add(types.InlineKeyboardButton(product["name"], callback_data=f'{products.index(product)} {call.data.replace(" ","_")}'))
    await bot.send_message(call.message.chat.id, f"Все продукты из категории {call.data}:",reply_markup=markup1)
    await bot.send_message(call.message.chat.id,"Чтобы вернуться к категориями, нажмите кнопку /start",reply_markup=markup2)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.callback_query_handler(func=lambda call: True)
async def get_product_data(call):
    # Получение всей информации
    product_id = call.data.split(' ')[0]
    category = call.data.split(' ')[1]

    response_all_data = requests.get(f"http://127.0.0.1:8000/products_categories_full/{category}/{int(product_id)}")
    category = response_all_data.json()["category"]
    name = response_all_data.json()["name"]
    weight = response_all_data.json()["product_description"]["weight"]
    protein = response_all_data.json()["product_description"]["protein"]
    fats = response_all_data.json()["product_description"]["fats"]
    carbs = response_all_data.json()["product_description"]["carbs"]
    calories = re.search(fr'(?<=\()\d+(?:,\d+)?(?= )',response_all_data.json()["product_description"]["calories"])[0]

    fat_content = response_all_data.json()["product_description"]["fat_content"]
    storage_conditions = response_all_data.json()["product_description"]["storage_conditions"]
    expiry = response_all_data.json()["product_description"]["expiry"]
    pack = response_all_data.json()["product_description"]["pack"]

    composition = response_all_data.json()["composition"]

    link = response_all_data.json()["link"]
    img = response_all_data.json()["img"]

    # получение детальной информации
    response_detail_data = requests.get(f"http://127.0.0.1:8000/products_cpfc/{category}/{int(product_id)}")
    protein_detail = response_detail_data.json()["protein"]
    fats_detail = response_detail_data.json()["fats"]
    carbs_detail = response_detail_data.json()["carbs"]
    calories_detail = response_detail_data.json()["calories"]
    #костыль
    result = f'\t- Категория: {category}\n' \
             f'\t- Вес: {weight}\n' \
             f'\t- КБЖУ:\n' \
             f'\t\t\t\t• <b>Калории</b>: {calories} ккал <u>(на 100 грамм)</u>, {calories_detail} <u>(во всём продукте)</u>\n' \
             f'\t\t\t\t• <b>Белки</b>: {protein} <u>(на 100 грамм)</u>, {protein_detail} <u>(во всём продукте)</u>\n' \
             f'\t\t\t\t• <b>Жиры</b>: {fats} <u>(на 100 грамм)</u>, {fats_detail} <u>(во всём продукте)</u>\n' \
             f'\t\t\t\t• <b>Углеводы</b>: {carbs} <u>(на 100 грамм)</u>, {carbs_detail} <u>(во всём продукте)</u>\n' \
             f'\t- Жирность: {fat_content}\n' \
             f'\t- Условия хранения: {storage_conditions}\n' \
             f'\t- Срок годности: {expiry}\n' \
             f'\t- Упаковка: {pack}\n' \
             f'\t- Состав: <i>{composition}</i>\n' \
             f'\t- Ссылка на товар: {link}\n' \
             f'\t- Изображение: {img}\n'

    markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup2.add(types.KeyboardButton('/start'))
    await bot.send_message(call.message.chat.id, f"Информация о продукте <i>'{name}'</i>:\n{result}", parse_mode='html')
    await bot.send_message(call.message.chat.id,"Чтобы вернуться к категориями, нажмите кнопку /start",reply_markup=markup2)


import asyncio
asyncio.run(bot.polling())