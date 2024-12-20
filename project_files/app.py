import os
import sqlite3
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_db_path():
    db_dir = os.path.dirname('rolls.db')
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    return 'rolls.db'


def create_table():
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS rolls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ingredients TEXT,
            weight TEXT,
            image_url TEXT,
            category TEXT,
            price TEXT
        )
        ''')
        conn.commit()


def parse_rolls():
    urls = [
        ("https://momohit.ru/firmennie-rolli", "Фирменные"),
        ("https://momohit.ru/tempura-rolli", "Темпура"),
        ("https://momohit.ru/zapechennie-rolli", "Запеченные")
    ]

    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for url, category in urls:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                roll_items = soup.find_all('div', class_='product-item')

                for roll_item in roll_items:
                    name_tag = roll_item.find('h3', class_='title')
                    name = name_tag.text.strip() if name_tag else 'Без названия'

                    ingredients_tag = roll_item.find('p', class_='desc')
                    ingredients = ingredients_tag.text.strip() if ingredients_tag else 'Не указан'

                    weight_tag = roll_item.find('span', class_='s_h3')
                    weight = weight_tag.text.strip() if weight_tag else 'Не указан'

                    image_tag = roll_item.find('img', class_='lazyImg')
                    image_url = image_tag['data-original'] if image_tag else 'Не указано'

                    cost_line = roll_item.find('div', class_='cost-line')
                    price_tag = cost_line.find('p', class_='cost') if cost_line else None
                    price = price_tag.text.strip() if price_tag else 'Не указана'

                    cursor.execute('''
                    SELECT COUNT(*) FROM rolls WHERE name = ? AND price = ?
                    ''', (name, price))
                    count = cursor.fetchone()[0]

                    if count == 0:
                        cursor.execute('''
                        INSERT INTO rolls (name, ingredients, weight, image_url, category, price)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (name, ingredients, weight, image_url, category, price))
            else:
                print(f"Ошибка загрузки URL {url} (Статус: {response.status_code})")

        conn.commit()


def get_rolls(sort=None):
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT name, ingredients, weight, image_url, price FROM rolls"
        params = []

        if sort:
            if sort == "weight_asc":
                query += " ORDER BY CAST(weight AS INTEGER) ASC"
            elif sort == "weight_desc":
                query += " ORDER BY CAST(weight AS INTEGER) DESC"
            elif sort == "ingredient_los":
                query += " WHERE ingredients LIKE ?"
                params.append("%лосось%")
            elif sort == "ingredient_tun":
                query += " WHERE ingredients LIKE ?"
                params.append("%тунец%")
            elif sort == "ingredient_krev":
                query += " WHERE ingredients LIKE ?"
                params.append("%креветки%")

        cursor.execute(query, params)
        rolls = [{'name': row[0], 'ingredients': row[1], 'weight': row[2], 'image_url': row[3], 'price': row[4]} for row in cursor.fetchall()]

    return rolls


@app.route("/", methods=["GET", "POST"])
def index():
    sort = request.args.get("sort")
    rolls = get_rolls(sort)
    no_rolls_message = None
    if sort and not rolls:
        no_rolls_message = "Нет роллов с выбранным продуктом."

    return render_template("index.html", rolls=rolls, sort=sort, no_rolls_message=no_rolls_message)


if __name__ == "__main__":
    create_table()
    parse_rolls()
    app.run(host="0.0.0.0", port=5000)
