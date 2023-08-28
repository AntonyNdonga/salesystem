from flask import Flask, render_template, request, redirect, url_for, flash, session
from pgfunc import (
    fetch_data,
    insert_sales,
    insert_products,
    sales_per_day,
    insert_stock,
    get_pid,
)
from pgfunc import (
    update_products,
    sales_per_products,
    remaining_stock,
    remainin_stock,
    delete_products,
    login,
)
import pygal
import psycopg2
import barcode
from barcode import Code128
from barcode.writer import ImageWriter
from datetime import datetime, timedelta
from functools import wraps
import psycopg2
import re
from werkzeug.security import generate_password_hash, check_password_hash


conn = psycopg2.connect("dbname=kassmat user=postgres password=123Sugarcane")
cur = conn.cursor()
# 'postgresql+psycopg2://postgres:123Sugarcane@localhost:5432/kassmat'
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)


# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder
# All CSS/JS/ Images are put inside "static" folder
app = Flask(__name__)
app.secret_key = "tony2023"

# a route is an extension of url which loads you a html page
# @ - a decorator(its in-built ) make something be static


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("login"))

    return wrap


# @app.before_request
# def restrict_pages():
#     protected_routes = ['/products', '/sales', '/dashboard','/stock']
#     if request.path in protected_routes and not session.get('logged_in') and not session.get('registered'):
#         return redirect(url_for('login'))


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/index")
def landing_page():
    return render_template("index.html")


@app.route("/products")
def products():
    prods = fetch_data("products")
    return render_template("products.html", prods=prods)


# def login_required(view_func):
#     @wraps(view_func)
#     def decorated_view(*args, **kwargs):
#         if not session.get('logged_in') and not session.get('registered'):
#             return redirect('/login')
#         return view_func(*args, **kwargs)
#     return decorated_view


@app.route("/dashboard")
def dashboard():
    daily_sales = sales_per_day()
    dates = []
    sales = []

    for i in daily_sales:
        dates.append(i[0])
        sales.append(i[1])
        chart = pygal.Line()
        chart.title = "sales per day"
        chart.x_labels = dates
        chart.add("sales", sales)
    chart = chart.render_data_uri()

    bar_chart = pygal.Bar()
    bar_chart.title = "sales per product"
    sale_product = sales_per_products()
    name1 = []
    sale1 = []
    for j in sale_product:
        name1.append(j[0])
        sale1.append(j[1])
    bar_chart.x_labels = name1
    bar_chart.add("Sale", sale1)
    bar_chart = bar_chart.render_data_uri()

    bar_chart1 = pygal.Bar()
    bar_chart1.title = "remaining stock"
    remain_stock = remaining_stock()
    name1 = []
    rs = []
    for j in remain_stock:
        name1.append(j[1])
        rs.append(j[2])
    bar_chart1.x_labels = name1
    bar_chart1.add("remain_stock", rs)
    bar_chart1 = bar_chart1.render_data_uri()

    return render_template(
        "dashboard.html", chart=chart, bar_chart=bar_chart, bar_chart1=bar_chart1
    )


@app.route("/addproducts", methods=["POST", "GET"])
def addproducts():
    if request.method == "POST":
        name = request.form["name"]
        buying_price = request.form["buying_price"]
        selling_price = request.form["selling_price"]

        products = (name, buying_price, selling_price)
        insert_products(products)
        return redirect("/products")


@app.route("/editproduct", methods=["POST", "GET"])
def editproducts():
    if request.method == "POST":
        id = request.form["id"]
        name = request.form["name"]
        buying_price = request.form["buying_price"]
        selling_price = request.form["selling_price"]

        vs = (id, name, buying_price, selling_price)
        update_products(vs)
        return redirect("/products")


@app.route("/deleteproduct", methods=["POST", "GET"])
def deleteproducts():
    if request.method == "POST":
        id = request.form["id"]
        name = request.form["name"]
        buying_price = request.form["buying_price"]
        selling_price = request.form["selling_price"]

        vs = (id, name, buying_price, selling_price)
        delete_products(vs)
        return redirect("/products")


@app.route("/addsales", methods=["POST", "GET"])
def addsales():
    if request.method == "POST":
        pid = request.form["pid"]
        quantity = request.form["quantity"]
        sales = (pid, quantity, "now()")
        insert_sales(sales)
        return redirect("/sales")


@app.route("/sales")
def sales():
    sales = fetch_data("sales")
    prods = fetch_data("products")
    return render_template("sales.html", sales=sales, prods=prods)


@app.route("/stock")
def stock():
    stock = fetch_data("stock")
    prods = fetch_data("products")
    return render_template("stock.html", stock=stock, prods=prods)


@app.route("/addstock", methods=["POST"])
def addstock():
    if request.method == "POST":
        pid = request.form["pid"]
        quantity = request.form["quantity"]
        stock = (pid, quantity, "now()")
        insert_stock(stock)
        return redirect("/stock")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash(
        "You have been logged out. To regain access, please log in.", category="error"
    )
    return render_template("logout.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    # checking email and password are in form
    if (
        request.method == "POST"
        and "email" in request.form
        and "password" in request.form
    ):
        email = request.form["email"]
        password = request.form["password"]
        # cheking account existing in in SQL
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        print(user)
        # PRINT WORKING CAN SEE USERS DETAILS IN TERMINAL
        if user:
            password_rs = user[2]
            if check_password_hash(password_rs, password):
                session["loggedin"] = True
                session["email"] = user[1]
                session["full_name"] = user[0]
                return redirect("/index")
            else:
                flash("Incorrect email/password")
        else:
            flash("user doesnot exist")
    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if (
        request.method == "POST"
        and "full_name" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        full_name = request.form["full_name"]
        password = request.form["password"]
        email = request.form["email"]

        _hashed_password = generate_password_hash(password)

        # Check if the email already exists in the database
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        emails = cur.fetchone()

        # Email Validation
        if emails:
            flash("Email is already in use")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address")
        elif not re.match(r"[A-Za-z]+", full_name):
            flash("Full_name must contain characters and numbers")
        elif not password or not email:
            flash("Please fill out the form")
        else:
            cur.execute(
                "INSERT INTO users (full_name, email, password, created_at) VALUES ( %s, %s, %s, NOW())",
                (full_name, email, _hashed_password),
            )
            conn.commit()
            flash("You have registered successfully!")
            return render_template("login.html")
    elif request.method == "POST":
        flash("Please fill out the form")

    return render_template("register.html")


@app.context_processor
def inject_remainin_stock():
    def remaining_stock(product_id=None):
        stock = remainin_stock(product_id)
        return stock[0] if stock is not None else int("0")

    return {"remaining_stock": remaining_stock}


@app.context_processor
def generate_barcode():
    id_list = get_pid()
    barcode_paths = []
    for pid_tuple in id_list:
        pid = pid_tuple[0]
        code = Code128(str(pid), writer=ImageWriter())
        barcode_path = f"static/barcodes/{pid}.png"
        code.save(barcode_path)
        barcode_paths.append(barcode_path)
    return {"generate_barcode": generate_barcode}


if __name__ == "__main__":
    app.run(debug=True)
