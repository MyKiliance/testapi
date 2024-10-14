from flask import Flask, request, jsonify
import random
import uuid

app = Flask(__name__)

# ตัวอย่างข้อมูลสินค้าคงคลัง
inventory = {i: {"product_id": i, "quantity": random.randint(0, 100)} for i in range(1, 101)}

# ตัวอย่างข้อมูลสินค้า
products = {i: {"product_id": i, "name": f"Product {i}", "price": round(random.uniform(10, 100), 2)} for i in range(1, 101)}

# สถานะคำสั่งซื้อ
order_statuses = {}

@app.route('/order', methods=['POST'])
def create_order():
    data = request.json
    order_id = data.get('order_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if product_id not in inventory or inventory[product_id]['quantity'] < quantity:
        return jsonify({"error": "Insufficient stock"}), 400
    
    inventory[product_id]['quantity'] -= quantity
    order_statuses[order_id] = 'pending'
    
    return jsonify({"message": f"Order {order_id} created successfully", "status": "pending"}), 200

@app.route('/inventory/<int:product_id>', methods=['GET'])
def check_inventory(product_id):
    if product_id in inventory:
        return jsonify(inventory[product_id]), 200
    return jsonify({"error": "Product not found"}), 404

@app.route('/order/<string:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    new_status = data.get('status')
    
    if order_id not in order_statuses:
        return jsonify({"error": "Order not found"}), 404
    
    order_statuses[order_id] = new_status
    return jsonify({"message": f"Order {order_id} status updated to {new_status}"}), 200

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product_info(product_id):
    if product_id in products:
        return jsonify(products[product_id]), 200
    return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
