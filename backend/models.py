from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey

db=SQLAlchemy()

class Customer(db.Model):
    __table_args__ = {'extend_existing': True}
    customerid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name=db.Column(db.String(80), nullable=False)
    customer_email=db.Column(db.String(80), nullable=False, unique=True)
    customer_password=db.Column(db.String(80), nullable=False, unique=True)
    phone_no=db.Column(db.String(80), nullable=False)
    address=db.Column(db.String(80), nullable=False)
    city=db.Column(db.String(80), nullable=False)
    pincode=db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="customer")

    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.customer_name}>"

class Product(db.Model):
    __table_args__ = {'extend_existing': True}
    productid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name=db.Column(db.String(80), nullable=False)
    product_description=db.Column(db.String(500), nullable=False)
    product_rating=db.Column(db.DECIMAL)
    price=db.Column(db.DECIMAL)
    quantity=db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    categoryid=db.Column(db.Integer, db.ForeignKey('category.categoryid'), nullable=False)
    supplierid=db.Column(db.Integer, db.ForeignKey('supplier.supplierid'), nullable=False)

    Category = db.relationship('Category', backref='products')
    Supplier = db.relationship('Supplier', backref='products')
    orderdetails = db.relationship('OrderDetails', backref='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.product_name}>"
    
class Category(db.Model):
    __table_args__ = {'extend_existing': True}
    categoryid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name=db.Column(db.String(80), nullable=False)
    date_posted=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Category {self.category_name}>"
    
class Supplier(db.Model):
    __table_args__ = {'extend_existing': True}
    supplierid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_name=db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"<Supplier {self.supplier_name}>"
    
class Order(db.Model):
    orderid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    customerid = db.Column(db.Integer, db.ForeignKey('customer.customerid'), nullable=False)

    orderdetails = db.relationship('OrderDetails', backref='order', lazy=True)

    def __repr__(self):
        return f"<Order {self.orderid}>"

class OrderDetails(db.Model):
    orderdetailsid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderid = db.Column(db.Integer, db.ForeignKey('order.orderid'), nullable=False)
    productid = db.Column(db.Integer, db.ForeignKey('product.productid'), nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    customerid = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<OrderDetails {self.orderdetailsid}>"




