import requests
import time
import random
from bs4 import BeautifulSoup

def save_product_to_db(db, Product, name, price_with_sale, image_url):
    product = db.session.query(Product).filter_by(name=name).first()
    if not product:
        product = Product(name=name, price_with_sale=price_with_sale, image_url=image_url)
        db.session.add(product)
    else:
        product.price_with_sale = price_with_sale
    db.session.commit()


def get_data(url, db, Product):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    scr = requests.get(url, headers=headers)
    soup = BeautifulSoup(scr.content, "lxml")
    articles = soup.find_all("div", class_="col-md-4 col-lg-3 col-6 one_product_col filter-work")

    for article in articles:
        name = article.find("div", class_="text_1").span.text.strip()
        image_url = article.find("picture").find("img")["data-src"]
        price_with_sale = article.find("div", class_="with_sale").text.strip()

        save_product_to_db(db, Product, name, price_with_sale, image_url)

    time.sleep(random.randint(1, 5))

if __name__ == "__main__":
    get_data("https://sushifuji.ru/ufa/menu/")