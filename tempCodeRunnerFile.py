from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3  # Missing import

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for sessions

# Admin credentials for login
admin_credentials = {
    "admin": "adminpassword"  # Admin username and password
}

# Dummy list of food items
foods = [
    {"name": "Chicken Gravy", "price": 80.00, "image": "chicken Gravy.jpg", "description": "Lorem ipsum dolor sit amet."},
    {"name": "Briyani", "price": 150.00, "image": "Briyani.jpg", "description": "Lorem ipsum dolor sit amet."},
    {"name": "Burger", "price": 70.00, "image": "b1.jpg", "description": "Lorem ipsum dolor sit amet."},
    {"name": "Pizza", "price": 100.00, "image": "pizza.jpg", "description": "Lorem ipsum dolor sit amet."},
    {"name": "Dosa", "price": 50.00, "image": "dosa.webp", "description": "Lorem ipsum dolor sit amet."},
    {"name": "Roti with Panner Masala", "price": 90.00, "image": "roti.jpg", "description": "Lorem ipsum dolor sit amet."}
]

# Dummy data for login (for demo purposes)
users = {
    "admin": "password123",
    "user1": "mypassword"
}
users_db = {}

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials
        if admin_credentials.get(username) == password:
            session['admin'] = username  # Store admin in session
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials. Please try again."
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('food_orders.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', orders=orders)

@app.route('/admin/update_status/<pnr_number>', methods=['POST'])
def update_order_status(pnr_number):
    new_status = request.form.get('status')
    
    conn = sqlite3.connect('food_orders.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders
        SET status = ?
        WHERE pnr_number = ?
    """, (new_status, pnr_number))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_order/<pnr_number>', methods=['POST'])
def delete_order(pnr_number):
    conn = sqlite3.connect('food_orders.db')
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM orders WHERE pnr_number = ?
    """, (pnr_number,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)  # Remove admin from session
    return redirect(url_for('admin_login'))

# Initialize Database
def init_db():
    conn = sqlite3.connect('food_orders.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr_number TEXT NOT NULL,
            station TEXT NOT NULL,
            food_category TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Ordered successful'
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

@app.route('/')
def index():
    return render_template('index.html', foods=foods)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    quantity = request.form.get('quantity', 1)
    food_id = request.form.get('food_id')
    item = next((food for food in foods if food['name'] == food_id), None)
    if item:
        cart_item = {"name": item['name'], "quantity": quantity, "price": item['price'], "image": item['image']}
        session.setdefault('cart', []).append(cart_item)
    return redirect(url_for('index'))

@app.route('/order', methods=['GET', 'POST'])
def order_food():
    if request.method == 'POST':
        pnr_number = request.form.get('pnrNumber')
        station = request.form.get('stationSelect')
        food_category = request.form.get('foodCategory')
        payment_method = request.form.get('paymentMethod')

        if not (pnr_number and station and food_category and payment_method):
            return "All fields are required.", 400

        try:
            conn = sqlite3.connect('food_orders.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (pnr_number, station, food_category, payment_method)
                VALUES (?, ?, ?, ?)
            """, (pnr_number, station, food_category, payment_method))
            conn.commit()
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()

        return redirect(url_for('index'))

    return render_template('orders.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if users.get(username) == password:     
        return redirect(url_for('dashboard', username=username))
    else:
        return "Invalid username or password. Please try again."

@app.route('/dashboard/<username>')
def dashboard(username):
    return f"Welcome, {username}! You are logged in."

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']   
    password = request.form['password']
    confirm_password = request.form['confirmpassword']

    if password != confirm_password:
        return "Passwords do not match. Please try again."

    if username in users_db:
        return "Username already exists. Please choose a different one."

    users_db[username] = {'email': email, 'password': password}

    return redirect(url_for('login_page'))

@app.route('/cart')
def cart_page():
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart)

@app.route('/add-to-cart', methods=['POST'])
def add_item_to_cart():
    item = request.json
    cart = session.get('cart', [])
    cart.append(item)
    session['cart'] = cart
    return jsonify({'message': 'Item added to cart'}), 201

@app.route('/remove-item', methods=['POST'])
def remove_item():
    item_id = request.json.get('id')
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != item_id]
    session['cart'] = cart
    return jsonify({'message': 'Item removed from cart'}), 200

if __name__ == '__main__':
    app.run(debug=True)
