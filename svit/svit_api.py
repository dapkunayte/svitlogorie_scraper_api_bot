"""
Синхронный парсер
"""
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import parse_obj_as
import json
from typing import List
import re

app = FastAPI()

products = []

with open('res_async.json', 'r', encoding='utf-8') as f:
    products = json.loads(f.read())
f.close()


class Description(BaseModel):
    weight: str
    fat_content: str = None
    storage_conditions: str
    expiry: str
    pack: str
    protein: str = None
    fats: str = None
    carbs: str = None
    calories: str = None


class Product(BaseModel):
    category: str
    name: str
    product_description: Description
    composition: str
    link: str
    img: str


class DetailProduct(BaseModel):
    name: str
    weight: str
    protein: str = None
    fats: str = None
    carbs: str = None
    calories: str = None


pydantic_products = parse_obj_as(List[Product], products)
# product = pydantic_products[1]
# print(float(re.search(fr'(?<=\()\d+(?= )', product.product_description.calories)[0]))
category_list = [product for product in pydantic_products if product.category == 'Творожные сырки']


# print(category_list)


@app.get("/products/{product_id}")
def get_product_info(product_id: int) -> Product:
    return pydantic_products[product_id]


@app.get("/products_cpfc/{product_id}")
def get_product_cpfc(product_id: int) -> DetailProduct:
    product = pydantic_products[product_id]
    try:
        if "кг" in product.product_description.weight:
            product_weight = float(product.product_description.weight.split(" ")[0])*1000 / 100
        elif "x" in product.product_description.weight:
            product_weight = float(product.product_description.weight.split("x")[1].split(" ")[0])*float(product.product_description.weight.split("x")[0]) / 100
        else:
            product_weight = float(product.product_description.weight.split(" ")[0]) / 100
    except:
        product_weight = 0
    try:
        product_protein = float(product.product_description.protein.split(" ")[0].replace(",", ".")) * product_weight
    except:
        product_protein = 0
    try:
        product_carbs = float(product.product_description.carbs.split(" ")[0].replace(",", ".")) * product_weight
    except:
        product_carbs = 0
    try:
        product_fats = float(product.product_description.fats.split(" ")[0].replace(",", ".")) * product_weight
    except:
        product_fats = 0
    try:
        product_cals = float(re.search(fr'(?<=\()\d+(?:,0)?(?= )', product.product_description.calories)[0].replace(",",
                                                                                                                    ".")) * product_weight
    except:
        product_cals = 0
    if "200/400" in product.product_description.weight:
        product_protein = [round(float(product.product_description.protein.split(" ")[0].replace(",", "."))*2,2), round(float(product.product_description.protein.split(" ")[0].replace(",", "."))*4,2)]
        product_carbs = [round(float(product.product_description.carbs.split(" ")[0].replace(",", "."))*2,2), round(float(product.product_description.carbs.split(" ")[0].replace(",", "."))*4,2)]
        product_fats = [round(float(product.product_description.fats.split(" ")[0].replace(",", "."))*2,2),round(float(product.product_description.fats.split(" ")[0].replace(",", "."))*4,2)]
        product_cals = [round(float(re.search(fr'(?<=\()\d+(?:,0)?(?= )', product.product_description.calories)[0].replace(",","."))*2,2),round(float(re.search(fr'(?<=\()\d+(?:,0)?(?= )', product.product_description.calories)[0].replace(",","."))*4,2)]
        detail_product = DetailProduct(name=product.name, weight=f'{product.product_description.weight}',
                                   protein=f'{" ".join(product_protein)} г',
                                   carbs=f'{" ".join(product_carbs)} г',
                                   fats=f'{" ".join(product_fats)} г',
                                   calories=f'{" ".join(product_cals)} ккал')
    else:
        detail_product = DetailProduct(name=product.name, weight=f'{round(product_weight * 100, 2)} г',
                                       protein=f'{round(product_protein,2)} г',
                                       carbs=f'{round(product_carbs,2)} г',
                                       fats=f'{round(product_fats,2)} г',
                                       calories=f'{round(product_cals,2)} ккал')
    return detail_product


@app.get("/products_categories/{category}")
def get_products_by_category(category: str) -> List[Product]:
    return [product for product in pydantic_products if category.replace("_", " ").lower() in product.category.lower()]


@app.get("/products_categories_full/{category}")
def get_products_by_category(category: str) -> List[Product]:
    return [product for product in pydantic_products if category.replace("_", " ").lower() == product.category.lower()]


@app.get("/products_categories_full/{category}/{product_id}")
def get_products_by_category(product_id: int, category: str) -> Product:
    category_of_products = [product for product in pydantic_products if
                            category.replace("_", " ").lower() == product.category.lower()]
    print(category_of_products[product_id])
    return category_of_products[product_id]


@app.get("/products_cpfc/{category}/{product_id}")
def get_product_cpfc(product_id: int, category: str) -> DetailProduct:
    category_of_products = [product for product in pydantic_products if
                            category.replace("_", " ").lower() == product.category.lower()]
    product = category_of_products[product_id]
    try:
        if "1 кг" in product.product_description.weight or "1 л" in product.product_description.weight :
            product_weight = float(product.product_description.weight.split(" ")[0]) * 1000 / 100
        elif "x" in product.product_description.weight:
            product_weight = float(product.product_description.weight.split("x")[1].split(" ")[0]) * float(
                product.product_description.weight.split("x")[0]) / 100
        else:
            product_weight = float(product.product_description.weight.split(" ")[0]) / 100
    except:
        product_weight = 0
    try:
        product_protein = float(product.product_description.protein.split(" ")[0].replace(",", ".")) * product_weight
    except:
        product_protein = 0
    try:
        product_carbs = float(product.product_description.carbs.split(" ")[0].replace(",", ".")) * product_weight
    except:
        product_carbs = 0
    try:
        product_fats = float(product.product_description.fats.split(" ")[0].replace(",", ".")) * product_weight
    except:
        product_fats = 0
    try:
        product_cals = float(re.search(fr'(?<=\()\d+(?:,0)?(?= )', product.product_description.calories)[0].replace(",",".")) * product_weight
    except:
        product_cals = 0
    if "200/400" in product.product_description.weight:
        product_protein = [round(float(product.product_description.protein.split(" ")[0].replace(",", "."))*2,2), round(float(product.product_description.protein.split(" ")[0].replace(",", "."))*4,2)]
        product_carbs = [round(float(product.product_description.carbs.split(" ")[0].replace(",", "."))*2,2), round(float(product.product_description.carbs.split(" ")[0].replace(",", "."))*4,2)]
        product_fats = [round(float(product.product_description.fats.split(" ")[0].replace(",", "."))*2,2),round(float(product.product_description.fats.split(" ")[0].replace(",", "."))*4,2)]
        product_cals = [round(float(re.search(fr'(?<=\()\d+(?:,0)?(?= )', product.product_description.calories)[0].replace(",","."))*2,2),round(float(re.search(fr'(?<=\()\d+(?:,0)?(?= )', product.product_description.calories)[0].replace(",","."))*4,2)]
        print(product_protein)
        detail_product = DetailProduct(name=product.name, weight=f'{product.product_description.weight}',
                                   protein='/'.join(list(map(str,product_protein)))+'г',
                                   carbs='/'.join(list(map(str,product_carbs)))+'г',
                                   fats='/'.join(list(map(str,product_fats)))+'г',
                                   calories='/'.join(list(map(str,product_cals)))+'ккал')
    else:
        detail_product = DetailProduct(name=product.name, weight=f'{round(product_weight * 100, 2)} г',
                                       protein=f'{round(product_protein,2)} г',
                                       carbs=f'{round(product_carbs,2)} г',
                                       fats=f'{round(product_fats,2)} г',
                                       calories=f'{round(product_cals,2)} ккал')
    return detail_product
