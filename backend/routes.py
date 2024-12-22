from flask_sqlalchemy import SQLAlchemy
from shoppingmart import app
from flask import Flask, request, jsonify
from models import Product, Category

db=SQLAlchemy()

# CRUD for products

@app.route('/products', methods=['POST'])
def addProduct():
    data=request.get_json()
    new_Product=Product(product_name=data['product_name'], product_description=data['product_description'], product_rating=data['product_rating'], price=data['price'], quantity=data['quantity'], image=data['image'])
    db.session.add(new_Product)
    db.session.commit()
    return jsonify({"message":"product added successfully"})

@app.route('/products', methods=['GET'])
def getProducts():
    products=Product.query.all()
    return jsonify([{"id":prod.productid, "product_name":prod.product_name, "product_description":prod.product_description, "product_rating":prod.product_rating, "price":prod.price, "quantity":prod.quantity, "image":prod.image }for prod in products])

@app.route('/products', methods=['PUT'])
def updateProduct(id):
    data=request.get_json()
    product=Product.query.get_or_404(id)
    product.product_name=data['product_name']
    product.product_description=data['product_description']
    product.product_rating=data['product_rating']
    product.price=data['price']
    product.quantity=data['quantity']
    product.image=data['image']
    db.session.commit()
    return jsonify({"message":"product updated successfully"})

@app.route('/products', methods=['DELETE'])
def deleteProduct(id):
    prod=Product.query.get_or_404(id)
    db.session.delete(prod)
    db.session.commit()
    return jsonify({"message":"product deleted successfully"})



