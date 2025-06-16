# from flask import Flask, request, render_template
# from flask_mysqldb import MySQL

# app = Flask(__name__)

# # MySQL Configuration
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'demo'

# mysql = MySQL(app)

# @app.route('/')
# def form():
#     return render_template('form.html')

# @app.route('/submit', methods=['POST'])
# def submit():
#     name = request.form['name']
#     id = request.form['id']
#     cur = mysql.connection.cursor()
#     cur.execute("INSERT INTO users (name, id) VALUES (%s, %s)", (name, id))
#     mysql.connection.commit()
#     cur.close()
#     return 'Data Inserted Successfully!'

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'restaurant_db'

mysql = MySQL(app)

@app.route('/')
def index():
    menu = [
        {"name": "Pizza", "price": 250},
        {"name": "Burger", "price": 120},
        {"name": "Pasta", "price": 180},
        {"name": "Fries", "price": 90}
    ]
    return render_template('index.html', menu=menu)

@app.route('/bill', methods=['POST'])
def bill():
    name = request.form['customer_name']
    selected_items = request.form.getlist('items')
    quantities = request.form.getlist('quantity')

    menu = {"Pizza": 250, "Burger": 120, "Pasta": 180, "Fries": 90}
    total = 0
    details = []

    cur = mysql.connection.cursor()
    for item, qty in zip(selected_items, quantities):
        if item in menu and qty:
            qty = int(qty)
            amount = menu[item] * qty
            total += amount
            details.append((item, qty, amount))
            cur.execute("INSERT INTO bills (customer_name, item, quantity, amount) VALUES (%s, %s, %s, %s)",
                        (name, item, qty, amount))
    mysql.connection.commit()
    cur.close()

    return render_template('bill.html', details=details, total=total, name=name)

@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()

    # Count customers for today
    today = datetime.date.today()
    cur.execute("SELECT COUNT(DISTINCT customer_name) FROM bills WHERE DATE(ordered_at) = %s", (today,))
    customer_count = cur.fetchone()[0]

    # Show pending and served orders
    cur.execute("SELECT id, customer_name, item, quantity, amount, status, payment_status FROM bills ORDER BY ordered_at DESC")
    orders = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', orders=orders, customer_count=customer_count)

@app.route('/update_status/<int:bill_id>/<string:field>/<string:value>')
def update_status(bill_id, field, value):
    cur = mysql.connection.cursor()
    if field in ['status', 'payment_status']:
        cur.execute(f"UPDATE bills SET {field} = %s WHERE id = %s", (value, bill_id))
        mysql.connection.commit()
    cur.close()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
