from flask import Flask, request, jsonify, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import pymysql
from models import db, Customer, Product, Category, Supplier, Order, OrderDetails
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging


pymysql.install_as_MySQLdb()

app=Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'shoppingmart321'

app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:Shiva%40123@127.0.0.1/shoppingmart'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)

with app.app_context():
    db.create_all()

# CRUD for Customers- to update their profile

@app.route('/signup', methods=['POST'])
def signup():
    data=request.get_json()
    new_data=Customer(customer_name=data['customer_name'],
                      customer_email=data['customer_email'],
                      customer_password=data['customer_password'],
                      phone_no=data['phone_no'],
                      address=data['address'],
                      city=data['city'],
                      pincode=data['pincode'],
                      role=data.get('role', 'customer'))
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message":"customer registered successfully"})


# Login route for customer

@app.route('/login/customer', methods=['POST'])
def login_customer():
    data = request.get_json()
    customer_email = data.get('customer_email')
    customer_password = data.get('customer_password')

    if not customer_email or not customer_password:
        return jsonify({"message": "Missing email or password"}), 400

    try:
        user = Customer.query.filter_by(customer_email=customer_email).one()
    except NoResultFound:
        return jsonify({"message": "Invalid email or password"}), 401

    # Check the password (ensure you're using a secure hashing method in production)
    if user.customer_password != customer_password:
        return jsonify({"message": "Invalid email or password"}), 401

    # Set session variables if needed

    session['customer_id'] = user.customerid,
    session['customer_name'] = user.customer_name,
    session['role'] = user.role,
    print(session)

    # Return additional customer information
    return jsonify({
        "message": "Login successful",
        "customer_id": user.customerid,
        "customer_name": user.customer_name,
        "customer_email": user.customer_email,
        "phone_no": user.phone_no,
        "address": user.address,
        "city": user.city,
        "pincode": user.pincode,
    }), 200  # Return a 200 OK status

app.config['SESSION_TYPE'] = 'filesystem' 

# Login route for admin

@app.route('/login/admin', methods=['POST'])
def login_admin():
    data = request.get_json()
    admin_email = data.get('admin_email')  # Assuming admin uses a different email field
    admin_password = data.get('admin_password')

    if not admin_email or not admin_password:
        return jsonify({"message": "Missing email or password"}), 400

    # Check if the user is an admin in the Customer table
    admin = Customer.query.filter_by(customer_email=admin_email, role='admin').one()
    if not admin or admin.customer_password != admin_password:
        return jsonify({"message": "Invalid email or password"}), 401

    session['user_id'] = admin.customerid
    session['role'] = admin.role

    return jsonify({"message": "Admin login successful", "role": admin.role})



@app.route('/login/<int:id>', methods=['PUT'])
def updateCustomer(id):
    data=request.get_json()
    upd=Customer.query.get_or_404(id)
    upd.customer_name=data['customer_name']
    upd.customer_email=data['customer_email']
    upd.customer_password=data['customer_password']
    upd.phone_no=data['phone_no']
    upd.address=data['address']
    upd.city=data['city']
    upd.pincode=data['pincode']
    if 'role' in data:
        upd.role = data['role'] 
    db.session.commit()
    return jsonify({"message":"Updated successfully"})


# CRUD for products

UPLOAD_FOLDER = os.path.join('static', 'images')  # Use os.path.join for consistency
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/products', methods=['POST'])
def adddProduct():
    try:
        # Log request form data
        logging.info(f"Received form data: {request.form}")
        logging.info(f"Received file data: {request.files}")

        data = request.form
        file = request.files.get('image')

        # Fetch the category and supplier IDs
        category = Category.query.get(data['categoryid'])
        supplier = Supplier.query.get(data['supplierid'])

        if not category or not supplier:
            logging.error("Invalid category or supplier ID")
            return jsonify({"error": "Invalid category or supplier ID"}), 400

        # Process image file
        if file:
            image_filename = secure_filename(file.filename)  # Use secure_filename to avoid issues
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)  # Saves to the file system
            file.save(image_path)
            image_url = f"/images/{image_filename}"  # Correct URL format for web access
        else:
            logging.error("Image file is required")
            return jsonify({"error": "Image file is required"}), 400

        # Create the new product
        new_product = Product(
            product_name=data['product_name'],
            product_description=data['product_description'],
            product_rating=data['product_rating'],
            price=data['price'],
            quantity=data['quantity'],
            image=image_url,
            categoryid=data['categoryid'],
            supplierid=data['supplierid']
        )
        
        db.session.add(new_product)
        db.session.commit()

        logging.info(f"Product {new_product.product_name} added successfully")
        return jsonify({"message": "Product added successfully"}), 201

    except Exception as e:
        logging.error(f"Error adding product: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500




@app.route('/products', methods=['GET'])
def getProducts():
    products = Product.query.all()
    return jsonify([{
        "productid": prod.productid,
        "product_name": prod.product_name,
        "product_description": prod.product_description,
        "product_rating": prod.product_rating,
        "price": prod.price,
        "quantity": prod.quantity,
        "image": f"static/images/{os.path.basename(prod.image)}",  # Ensure proper image path
        "categoryName": prod.Category.category_name,
        "supplierName": prod.Supplier.supplier_name
    } for prod in products])


# Flask backend
@app.route('/products/<int:id>', methods=['GET'])
def getProduct(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'productid': product.productid,  # Consistent with frontend
        'product_name': product.product_name,
        'product_description': product.product_description,
        'product_rating': product.product_rating,
        'price': product.price,
        'quantity': product.quantity,
        "image": f"static/images/{os.path.basename(product.image)}",
        'categoryid': product.categoryid,
        'supplierid': product.supplierid
    })



@app.route('/products/<int:id>', methods=['PUT'])
def updateProduct(id):
    data = request.get_json()
    print("Received data:", data)  # Debug log
    product = Product.query.get_or_404(id)
    
    # Validate incoming data
    if not all(key in data for key in ('product_name', 'product_description', 'product_rating', 'price', 'quantity', 'categoryid', 'supplierid')):
        return jsonify({"error": "Missing fields in request data"}), 400

    category = Category.query.get(data['categoryid'])
    supplier = Supplier.query.get(data['supplierid'])
    if not category or not supplier:
        return jsonify({"error": "Invalid category or supplier ID"}), 400
    
    # Update the product
    product.product_name = data['product_name']
    product.product_description = data['product_description']
    product.product_rating = data['product_rating']
    product.price = data['price']
    product.quantity = data['quantity']
    product.image = data.get('image', product.image)  # Update image if provided
    product.categoryid = data['categoryid']
    product.supplierid = data['supplierid']
    
    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200



@app.route('/images/<path:filename>')
def send_image(filename):
    return send_from_directory('UPLOAD_FOLDER', filename)

@app.route('/products/<int:id>', methods=['DELETE'])
def deleteProduct(id):
    prod=Product.query.get_or_404(id)
    db.session.delete(prod)
    db.session.commit()
    return jsonify({"message":"product deleted successfully"})


# CRUD for Category

@app.route('/categories', methods=['POST'])
def addCategory():
    data=request.get_json()
    new_category=Category(category_name=data['category_name'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message":"category added successfully"})

@app.route('/categories', methods=['GET'])
def getCategories():
    categories=Category.query.all()
    return jsonify([{"categoryid":cat.categoryid, "category_name":cat.category_name, "date_posted":cat.date_posted}for cat in categories])

@app.route('/categories/<int:id>', methods=['GET'])
def getCategory(id):
    cat=Category.query.get_or_404(id)
    return jsonify({"categoryid":cat.categoryid, "category_name":cat.category_name, "date_posted":cat.date_posted})

@app.route('/categories/<int:id>', methods=['PUT'])
def updateCategory(id):
    data=request.get_json()
    cat=Category.query.get_or_404(id)
    cat.category_name=data['category_name']
    db.session.commit()
    return jsonify({"message":"category updated successfully"})

@app.route('/categories/<int:id>', methods=['DELETE'])
def deleteCategory(id):
    cat=Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"message":"category deleted successfully"})

# CRUD for supplier

@app.route('/suppliers', methods=['POST'])
def addSupplier():
    data=request.get_json()
    newdata=Supplier(supplier_name=data['supplier_name'])
    db.session.add(newdata)
    db.session.commit()
    return jsonify({"message":"supplier added successfully"})

@app.route('/suppliers', methods=['GET'])
def getSuppliers():
    datas=Supplier.query.all()
    return jsonify([{"supplierid":data.supplierid, "supplier_name":data.supplier_name}for data in datas])

@app.route('/suppliers/<int:id>', methods=['GET'])
def getSupplier(id):
    data=Supplier.query.get_or_404(id)
    return jsonify({"supplierid":data.supplierid, "supplier_name":data.supplier_name})

@app.route('/suppliers/<int:id>', methods=['PUT'])
def updateSupplier(id):
    data=request.get_json()
    supl=Supplier.query.get_or_404(id)
    supl.supplier_name=data['supplier_name']
    db.session.commit()
    return jsonify({"message":"supplier updated successfully"})

@app.route('/suppliers/<int:id>', methods=['DELETE'])
def deleteSupplier(id):
    supl=Supplier.query.get_or_404(id)
    db.session.delete(supl)
    db.session.commit()
    return jsonify({"message":"supplier deleted successfully"})



# Create Order
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    logging.info(f"Received order data: {data}")

    try:
        # Fetch the customer ID directly from the order data
        customer_id = data.get('customer_id')  # Get it directly from the request
        if not customer_id:
            return jsonify({'message': 'Customer ID not found in request'}), 403

        # Create a new order
        new_order = Order(customerid=customer_id)
        db.session.add(new_order)
        db.session.flush()  # This allows you to access new_order.orderid

        # Add order details
        if 'orderDetails' not in data or not data['orderDetails']:
            return jsonify({'message': 'Order details not found in request'}), 400

        for item in data['orderDetails']:
            if 'productid' not in item or 'quantity' not in item:
                return jsonify({'message': 'Invalid data for order details'}), 400

            logging.info(f"Adding item to order: {item}")
            order_detail = OrderDetails(
                orderid=new_order.orderid,
                productid=item['productid'],
                price=item['price'],
                quantity=item['quantity'],
                customerid=customer_id  # Include customer ID here
            )
            db.session.add(order_detail)

        db.session.commit()
        return jsonify({'message': 'Order placed successfully!', 'orderid': new_order.orderid}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error while placing order: {str(e)}")
        return jsonify({'message': 'Failed to place order', 'error': str(e)}), 500


# Get All Orders
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([{
        "orderid": ord.orderid,
        "order_date": ord.order_date,
        "customerid": ord.customerid
    } for ord in orders])

# Get Specific Order
@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    ord = Order.query.get_or_404(id)
    return jsonify({
        "orderid": ord.orderid,
        "order_date": ord.order_date,
        "customerid": ord.customerid
    })

# Delete Order
@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    ord = Order.query.get_or_404(id)
    db.session.delete(ord)
    db.session.commit()
    return jsonify({"message": "Order deleted successfully"})

# Add Order Detail
@app.route('/orderdetails', methods=['POST'])
def add_order_detail():
    data = request.get_json()
    
    if 'orderid' not in data or 'productid' not in data or 'price' not in data or 'quantity' not in data:
        return jsonify({"message": "Invalid data for order detail"}), 400

    new_order_detail = OrderDetails(
        orderid=data['orderid'],
        productid=data['productid'],
        price=data['price'],
        quantity=data['quantity']
    )
    db.session.add(new_order_detail)
    db.session.commit()
    return jsonify({"message": "Order detail added successfully"}), 201

# Get All Order Details
@app.route('/orderdetails', methods=['GET'])
def get_order_details():
    order_details = OrderDetails.query.all()
    return jsonify([{
        "orderdetailsid": detail.orderdetailsid,
        "orderid": detail.orderid,
        "productid": detail.productid,
        "customerid": detail.customerid,
        "price": detail.price,
        "quantity": detail.quantity
    } for detail in order_details])

# Get Specific Order Detail
@app.route('/orderdetails/<int:id>', methods=['GET'])
def get_order_detail(id):
    detail = OrderDetails.query.get_or_404(id)
    return jsonify({
        "orderdetailsid": detail.orderdetailsid,
        "orderid": detail.orderid,
        "productid": detail.productid,
        "price": detail.price,
        "quantity": detail.quantity
    })

# Update Order Detail
@app.route('/orderdetails/<int:id>', methods=['PUT'])
def update_order_detail(id):
    data = request.get_json()
    detail = OrderDetails.query.get_or_404(id)
    
    if 'quantity' in data:
        detail.quantity = data['quantity']
        db.session.commit()
        return jsonify({"message": "Order detail updated successfully"})
    
    return jsonify({"message": "Invalid data"}), 400

# Delete Order Detail
@app.route('/orderdetails/<int:id>', methods=['DELETE'])
def delete_order_detail(id):
    detail = OrderDetails.query.get_or_404(id)
    db.session.delete(detail)
    db.session.commit()
    return jsonify({"message": "Order detail deleted successfully"})

# Customer info (as per your original code)
@app.route('/api/customer/<int:customer_id>', methods=['GET'])
def get_customer_info(customer_id):
    customer = Customer.query.get(customer_id)
    
    if customer:
        return jsonify({
            'customer_name': customer.customer_name,
            'customer_email': customer.customer_email,
            'phone_no': customer.phone_no,
            'address': customer.address,
            'city': customer.city,
            'pincode': customer.pincode
        })
    return jsonify({'message': 'Customer not found'}), 404



@app.route('/my-orders', methods=['POST'])
def get_my_orders():
    try:
        # Extract customer_id from the request body
        data = request.get_json()
        customer_id = data.get('customer_id')

        if not customer_id:
            return jsonify({'message': 'Customer ID not provided'}), 403

        # Fetch orders for the customer
        orders = Order.query.filter_by(customerid=customer_id).all()

        if not orders:
            return jsonify({'message': 'No orders found for this customer'}), 404

        # Prepare order details to return to the frontend
        order_list = []
        for order in orders:
            order_details = OrderDetails.query.filter_by(orderid=order.orderid).all()
            products = [{'productid': detail.productid, 'quantity': detail.quantity, 'price': detail.price} for detail in order_details]
            order_list.append({'order_id': order.orderid, 'products': products})

        return jsonify(order_list), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500


@app.route('/products/category/<search_term>', methods=['GET'])
def get_products_by_category(search_term):
    try:
        # Your logic to fetch products
        products = fetch_products_by_category(search_term)  # Replace with actual fetching logic
        return jsonify({"products": products})
    except Exception as e:
        return jsonify({"message": str(e)}), 500  # Return JSON response on error






if __name__=="__main__":
    app.run(debug=True)
