from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from models import db, Customer   #import db and Customer here
from models import db, Customer, Product,Order


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bms.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User model for admin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
# ------------------ CUSTOMER ROUTES ------------------

@app.route('/customers')
@login_required
def customers():
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

@app.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        new_customer = Customer(name=name, email=email, phone=phone, address=address)
        db.session.add(new_customer)
        db.session.commit()
        flash('Customer added successfully!')
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        customer.address = request.form.get('address')
        db.session.commit()
        flash('Customer updated!')
        return redirect(url_for('customers'))
    return render_template('edit_customer.html', customer=customer)

@app.route('/delete_customer/<int:id>')
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted!')
    return redirect(url_for('customers'))

# ------------------ PRODUCT ROUTES ------------------

@app.route('/products')
@login_required
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        new_product = Product(name=name, category=category, price=price, stock=stock)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.category = request.form.get('category')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        db.session.commit()
        flash('Product updated!')
        return redirect(url_for('products'))
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!')
    return redirect(url_for('products'))


@app.route("/orders")
@login_required
def orders():
    all_orders = Order.query.all()
    return render_template("orders.html", orders=all_orders)

@app.route("/add_order", methods=["GET", "POST"])
@login_required
def add_order():
    customers = Customer.query.all()
    products = Product.query.all()
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        product_id = request.form.get("product_id")
        quantity = request.form.get("quantity")

        new_order = Order(customer_id=customer_id, product_id=product_id, quantity=quantity)
        db.session.add(new_order)
        db.session.commit()
        flash("Order added successfully!")
        return redirect(url_for("orders"))

    return render_template("add_order.html", customers=customers, products=products)

# ------------------ SALES ROUTES ------------------

@app.route('/sales')
@login_required
def sales():
    from models import Sale, Customer, Product
    all_sales = Sale.query.all()
    return render_template('sales.html', sales=all_sales)

@app.route('/add_sale', methods=['GET', 'POST'])
@login_required
def add_sale():
    from models import Sale, Customer, Product
    customers = Customer.query.all()
    products = Product.query.all()
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity'))

        product = Product.query.get(product_id)
        total_price = product.price * quantity

        sale = Sale(customer_id=customer_id, product_id=product_id, quantity=quantity, total_price=total_price)
        product.stock -= quantity
        db.session.add(sale)
        db.session.commit()
        flash('Sale recorded successfully!')
        return redirect(url_for('sales'))
    return render_template('add_sale.html', customers=customers, products=products)

@app.route("/reports")
@login_required
def reports():
    from models import Order, Product, Customer
    total_customers = Customer.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()

    # Calculate total revenue
    orders = Order.query.all()
    total_revenue = sum(order.product.price * order.quantity for order in orders)

    # Data for chart: product names vs quantities sold
    product_sales = {}
    for order in orders:
        product_sales[order.product.name] = product_sales.get(order.product.name, 0) + order.quantity

    labels = list(product_sales.keys())
    values = list(product_sales.values())

    return render_template(
        "reports.html",
        total_customers=total_customers,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        labels=labels,
        values=values,
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
