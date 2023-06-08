from bs4 import BeautifulSoup
import requests
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

for category in categories:
    response1 = requests.get(category)
    response1.encoding = 'utf-8'
    soup1 = BeautifulSoup(response1.text, 'lxml')
    res = soup1.findAll('div', 'card-item')
    for tag in res:
        product_categories.append(soup1.find('div', 'h3').text)
        names.append(re.search(f'[^\\tn\n]+', tag.find('h3', class_='card-item__title-mobile').text)[0])
        decs1 = [span.find_all('span')[1].text for span in tag.find('ul', class_='card-item__list').find_all('li')]
        weights.append(decs1[0])
        fats.append(decs1[1])
        temps.append(decs1[2])
        expires.append(decs1[3])
        packs.append(decs1[4])
        try:
            p1 = tag.find('h4', string='Состав')
            compositions.append(re.search(rf'(?:\S+ ?)+',p1.find_next().text)[0])
        except:
            compositions.append("N\A")
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
            carbs.append(decs1[5])
            cals.append(decs1[6])
        else:
            proteins.append(0)
            fatss.append(0)
            carbs.append(0)
            cals.append(0)
            # print(re.search(f'[^\\tn\n]+', tag.find('h3', class_='card-item__title-mobile').text)[0])
    links.extend(
        [f'{category}#{product["data-slide"]}' for product in soup1.find_all('a', class_='product js-popup-card')])

# print(len(names),len(weights),len(fats),len(temps),len(expires),len(packs),len(proteins),len(fatss),len(carbs),len(cals),len(links),len(product_categories))
result_json = []

for name, weight, fat, temp, expiry, pack, protein, fats1, carb, cal, link, product_category, composition in zip(names, weights,
                                                                                                    fats, temps,
                                                                                                    expires, packs,
                                                                                                    proteins, fatss,
                                                                                                    carbs, cals, links,
                                                                                                    product_categories, compositions):
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
            'link': link
        }
    )

with open('res.json', 'w', encoding='utf-8') as file:
    json.dump(result_json, file, indent=4, ensure_ascii=False)
