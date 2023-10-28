import sqlite3
from flask import Flask, request, render_template, session

app: Flask = Flask(__name__, static_url_path='/static')

app.secret_key = 'tram_ngao'

@app.route('/')
def index():
    return render_template('abc.html', search_text="")


@app.route("/searchData", methods=["POST"])
def searchData():
    search_text = request.form['searchInput']
    html_table = load_data_from_db(search_text)
    print(html_table)
    return render_template('abc.html', search_text=search_text, table=html_table)


def load_data_from_db(search_text):
    sqldbname = 'db/website.db'
    if search_text != "":
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        sqlcommand = ("Select * from storages where model like '%") + search_text + "%'"
        cursor.execute(sqlcommand)
        data = cursor.fetchall()
        conn.close()
        return data


@app.route("/cart")
def view_cart():
    current_cart = []
    if 'cart' in session:
        current_cart = session.get("cart", [])
    return render_template('cart.html', carts=current_cart)

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    sqldbname = 'db/website.db'
    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])

    connection = sqlite3.connect(sqldbname)
    cursor = connection.cursor()
    cursor.execute("SELECT model, price FROM storages WHERE id = ?", (product_id,))

    product = cursor.fetchone()
    connection.close()

    product_dict = {
        "id": product_id,
        "name": product[0],
        "price": product[1],
        "quantity": quantity
    }

    cart = session.get("cart", [])

    found = False
    for item in cart:
        if item["id"] == product_id:
            item["quantity"] += quantity
            found = True
            break
    if not found:
        cart.append(product_dict)

    session["cart"] = cart

    rows = len(cart)
    outputmessage = ("Product added to cart successfully! "
                     "</br>Current: " + str(rows) + " products")
    return outputmessage


if __name__ == '__main__':
    app.run()
