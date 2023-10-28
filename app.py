import os
import sqlite3

from flask import Flask, request, render_template, session, redirect, url_for

app = Flask(__name__, static_url_path='/static')

app.secret_key = os.urandom(24)


@app.route('/')
def index():
    current_username = ''
    if 'current_user' in session:
        current_username = session['current_user']['name']
    return render_template('abc.html', search_text="", user_name=current_username)


@app.route("/searchData", methods=["POST"])
def searchData():
    # Get data from Request
    # Check if 'username' key exists in the session
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    search_text = request.form['searchInput']
    # Thay bang ham Load du lieu tu DB
    product_table = load_data_from_db(search_text)
    print(product_table)
    return render_template('abc.html', search_text=search_text, products=product_table,
                           user_name=current_username)


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


@app.route("/cart", methods=["POST"])
def view_cart():
    current_cart = []
    if 'cart' in session:
        current_cart = session.get("cart", [])
    return render_template('cart_update.html', carts=current_cart)


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


@app.route("/update_cart", methods=['POST'])
def update_cart():
    # 1. Get the shopping cart from the session
    cart = session.get('cart', [])
    # 2. Create a new cart to store updated items
    new_cart = []
    # 3. Iterate over each item in the cart
    for product in cart:
        product_id = str(product['id'])
        # 3.1 If this product has a new quantity in the form data
        if f'quantity-{product_id}' in request.form:
            quantity = int(request.form[f'quantity-{product_id}'])
        # If the quantity is o or this is a delete field, skip this product
        if quantity == 0 or f'delete-{product_id}' in request.form:
            continue

        # Otherwise, update the quantity of the product
        product['quantity'] = quantity
        # 3.2 Add the product to the new cart
        new_cart.append(product)
        # 4. Save the updated cart back to the session
        session['cart'] = new_cart
        # 5. Redirect to the shopping cart page (or wherever you want)
    return redirect(url_for('index'))


def get_obj_user(username, password):
    result = []
    sqldbname = 'db/website.db'
    # Khai bao bien de tro toi db
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # sqlcommand = "Select * from storages where "
    sqlcommand = "Select * from user where name =? and password = ?"
    cursor.execute(sqlcommand, (username, password))
    # return object
    obj_user = cursor.fetchone() or []
    if len(obj_user) > 0:  # Mỗi đối tượng là một danh sách
        result = obj_user
    conn.close()
    return result


@app.route("/login", methods=['GET', 'POST'])
def login():
    # Khi nhận dữ liệu từ hành vi post, sau khi nhận dữ 1.
    # từ session sẽ gọi định tuyến sang trang index
    if request.method == 'POST':
        username = request.form['txt_username']
        password = request.form['txt_password']
        # Store 'username' in the session
        obj_user = get_obj_user(username, password)
        if int(obj_user[0]) > 0:  # Nêu tôn Lui ID
            obj_user = {
                "id": obj_user[0],
                "name": obj_user[1],
                "email": obj_user[2]
            }
            session['current_user'] = obj_user
            return redirect(url_for('index'))
    # Trường hợp mặc định là vào trang login
    return render_template('login.html')


if __name__ == '__main__':
    app.run()
