from flask import Flask, request, jsonify
import random
import uuid
import os

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

@app.route('/payment', methods=['POST'])
def process_payment():
    data = request.json
    order_id = data.get('order_id')
    amount = data.get('amount')
    
    if order_id not in order_statuses:
        return jsonify({"error": "Order not found"}), 404
    
    order_statuses[order_id] = 'paid'
    return jsonify({"message": f"Payment for order {order_id} processed successfully"}), 200

# เพิ่มการอัปโหลดไฟล์ขนาดใหญ่ (1GB ขึ้นไป)
@app.route('/upload', methods=['POST'])
def upload_large_file():
    file = request.data
    file_size = len(file)
    
    if file_size >= 1 * 1024 * 1024 * 1024:  # ไฟล์ต้องมีขนาด >= 1GB
        return jsonify({"message": "Large file uploaded successfully", "file_size": file_size}), 200
    return jsonify({"error": "File too small"}), 400

# เพิ่มการประมวลผล JSON ขนาดใหญ่
@app.route('/process-large-json', methods=['POST'])
def process_large_json():
    data = request.json
    if 'data' in data and len(data['data']) >= 1 * 1024 * 1024 * 1024:  # ข้อมูลขนาด >= 1GB
        return jsonify({"message": "Large JSON processed successfully"}), 200
    return jsonify({"error": "JSON data too small"}), 400

if __name__ == '__main__':
    app.run(debug=True)
