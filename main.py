from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from pgfunc import fetch_data, insert_sales, insert_products,sales_per_day, insert_stock
from pgfunc import update_products, sales_per_products, remaining_stock, remainin_stock
import pygal

# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder
# All CSS/JS/ Images are put inside "static" folder
app = Flask(__name__)




app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/kassmat.db'
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


# a route is an extension of url which loads you a html page
# @ - a decorator(its in-built ) make something be static
@app.route("/")
def home():
    return render_template("index.html")


    


@app.route("/products")
def products():
   prods = fetch_data("products")
   return render_template('products.html', prods=prods)



   

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
      chart.add('sales', sales)
   chart = chart.render_data_uri()


   bar_chart = pygal.Bar()
   bar_chart.title = 'sales per product'
   sale_product = sales_per_products()
   name1 = []
   sale1 = []
   for j in sale_product:
      name1.append(j[0])
      sale1.append(j[1])
   bar_chart.x_labels = name1
   bar_chart.add('Sale', sale1)
   bar_chart=bar_chart.render_data_uri()


   bar_chart1 = pygal.Bar()
   bar_chart1.title = 'remaining stock'
   remain_stock = remaining_stock()
   name1 = []
   rs = []
   for j in remain_stock:
      name1.append(j[1])
      rs.append(j[2])
   bar_chart1.x_labels = name1
   bar_chart1.add('remain_stock', rs)
   bar_chart1=bar_chart1.render_data_uri()

   return render_template('dashboard.html', chart=chart, bar_chart=bar_chart, bar_chart1=bar_chart1 )
   





@app.route('/addproducts', methods=["POST", "GET"])
def addproducts():
   if request.method=="POST":
      name = request.form["name"]
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]

      products=(name,buying_price,selling_price)
      insert_products(products)
      return redirect("/products")
   


@app.route('/editproduct', methods=["POST", "GET"])
def editproducts():
   if request.method=="POST":
      id = request.form['id']
      name = request.form["name"]
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]

      vs=(id,name,buying_price,selling_price)
      update_products(vs)
      return redirect("/products")
   
   

# @app.route('/delete_row', methods=['POST'])
# def delete_row():
#    q = request.form.get('q')  # Assuming the row ID is sent as form data

#     # Call the delete_row_from_db function from pgfunc.py
#    delete_row_from_products(q)

#    #  return "Row deleted successfully."
#    return redirect("/products")


   
@app.route('/addsales', methods=["POST", "GET"])
def addsales():
   if request.method=="POST":
      pid= request.form["pid"]
      quantity=request.form["quantity"]
      sales=(pid,quantity,'now()')
      insert_sales(sales)
      return redirect("/sales")

      


@app.route("/sales")
def sales():
   sales = fetch_data("sales")
   prods= fetch_data("products")
   return render_template('sales.html', sales=sales, prods=prods)







@app.route("/stock")
def stock():
   stock = fetch_data("stock")
   prods= fetch_data("products")
   return render_template('stock.html', stock=stock, prods=prods)


@app.route('/addstock', methods=["POST"])
def addstock():
   if request.method=="POST":
      pid= request.form["pid"]
      quantity=request.form["quantity"]
      stock=(pid,quantity,'now()')
      insert_stock(stock)
      return redirect("/stock")
   







@app.context_processor
def inject_remainin_stock():
    def remaining_stock(product_id=None):
      stock = remainin_stock(product_id)
      return stock[0] if stock is not None else int('0')
    return {'remaining_stock': remaining_stock}


if __name__ == "__main__":
 app.run(debug=True)


