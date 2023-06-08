"""
Асинхронный парсер
"""
from bs4 import BeautifulSoup
import requests
import aiohttp
import asyncio
import lxml
import re
import json

url = 'https://svitlogorie.ru/'

response = requests.get(url=url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'lxml')

categories = [link['href'] for link in
              soup.find('div', class_='catalog-menu__wrapper').find_all('a', class_='catalog-menu__card')][:-1]

products_links = []
names = []
weights = []
fats = []
temps = []
expires = []
packs = []
proteins = []
fatss = []
carbs = []
cals = []
desc = []
compositions = []
links = []
product_categories = []
imgs = []

async def get_products_link(session, link):
    async with session.get(url=link) as response1:
        response11 = await response1.text()
        soup1 = BeautifulSoup(response11, 'lxml')
        products_links.extend(f'{link}#{i}' for i,product in
                              enumerate(soup1.find_all('a', class_='product js-popup-card')))


async def get_product_info(session, link):
    async with session.get(url=link) as response2:
        response22 = await response2.text()
        soup2 = BeautifulSoup(response22, 'lxml')
        res = soup2.findAll('div', 'card-item')
        for tag in res:
            product_categories.append(soup2.find('div', 'h3').text)
            names.append(re.search(f'[^\\tn\n]+', tag.find('h3', class_='card-item__title-mobile').text)[0])
            decs1 = [span.find_all('span')[1].text for span in tag.find('ul', class_='card-item__list').find_all('li')]
            weights.append(decs1[0])
            print(decs1[0])
            fats.append(decs1[1])
            temps.append(decs1[2])
            expires.append(decs1[3])
            packs.append(decs1[4])
            imgs.append(tag.find('div','card-item__img').find('img')['src'])
            try:
                p1 = tag.find('h4', string='Состав')
                compositions.append(re.search(rf'(?:\S+ ?)+', p1.find_next().text)[0])
            except:
                compositions.append("Не указан")
            if len(decs1) == 9:
                proteins.append(decs1[5])
                fatss.append(decs1[6])
                carbs.append(decs1[7])
                cals.append(decs1[8])
            elif len(decs1) == 8:
                proteins.append(decs1[5])
                fatss.append(decs1[6])
                carbs.append(0)
                cals.append(decs1[7])
            elif len(decs1) == 7:
                proteins.append(0)
                fatss.append(0)
                carbs.append(decs1[5].replace("u","г").replace(".",","))
                cals.append(decs1[6])
            else:
                proteins.append(0)
                fatss.append(0)
                carbs.append(0)
                cals.append(0)
        links.extend([f'{link}#{product["data-slide"]}' for product in soup2.find_all('a', class_='product js-popup-card')])



async def main():
    async with aiohttp.ClientSession() as session1:
        tasks = []
        for category in categories:
            task = asyncio.create_task(get_product_info(session1, category))
            tasks.append(task)
        await asyncio.gather(*tasks)


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())

result_json = []

for name, weight, fat, temp, expiry, pack, protein, fats1, carb, cal, link, product_category, composition,img in zip(names, weights,
                                                                                                    fats, temps,
                                                                                                    expires, packs,
                                                                                                    proteins, fatss,
                                                                                                    carbs, cals, links,
                                                                                                    product_categories, compositions,imgs):
    result_json.append(
        {
            'category': product_category,
            'name': name,
            'product_description': {
                'weight': weight,
                'fat_content': fat,
                'storage_conditions': temp,
                'expiry': expiry,
                'pack': pack,
                'protein': protein,
                'fats': fats1,
                'carbs': carb,
                'calories': cal
            },
            'composition': composition,
            'link': link,
            'img': img
        }
    )


with open('res_async.json', 'w', encoding='utf-8') as file:
    json.dump(result_json, file, indent=4, ensure_ascii=False)
