from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import re
from scraper import get_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    price_with_sale = db.Column(db.String(100))
    image_url = db.Column(db.String(500))


def extract_price(price_str):
    if isinstance(price_str, str):
        price = re.sub(r'\D', '', price_str)
        return float(price) if price else 0.0
    return 0.0

def filter_products(min=None, max=None):
    products = Product.query.all()
    filtered_products = []
    for product in products:
        price = extract_price(product.price_with_sale)
        if (min is None or price >= min) and (max is None or price <= max):
            filtered_products.append(product)

    return filtered_products


@app.route("/")
def index():
    min_price = request.args.get('min_price', type=float, default=None)
    max_price = request.args.get('max_price', type=float, default=None)
    order = request.args.get('order', default=None)

    products = filter_products(min=min_price, max=max_price) if min_price is not None or max_price is not None else Product.query.all()

    if order:
        products.sort(key=lambda product: extract_price(product.price_with_sale), reverse=(order == 'desc'))

    return render_template('index.html', products=products, order=order, min_price=min_price, max_price=max_price)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        get_data("https://sushifuji.ru/ufa/menu/", db, Product)
    app.run(host='0.0.0.0', port=5000)
