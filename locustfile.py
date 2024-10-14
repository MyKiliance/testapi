from locust import HttpUser, TaskSet, task, between
import json
import random
import uuid
import os

# Configuration: สามารถปรับ flag ตามกรณีที่ต้องการทดสอบได้
USE_REDIS = bool(int(os.getenv('USE_REDIS', '0')))  # ค่า 1 จะใช้ Redis
USE_RABBITMQ = bool(int(os.getenv('USE_RABBITMQ', '0')))  # ค่า 1 จะใช้ RabbitMQ

# ฟังก์ชันจำลองการใช้ Redis cache
def get_from_redis_cache(key):
    if USE_REDIS:
        print(f"Fetching {key} from Redis cache")
        return "Some cached data"
    return None

# ฟังก์ชันจำลองการส่งข้อความผ่าน RabbitMQ
def send_message_to_rabbitmq(queue, message):
    if USE_RABBITMQ:
        print(f"Sending message to RabbitMQ queue {queue}")
    else:
        print(f"RabbitMQ is not enabled. Skipping message to {queue}")

class UserBehavior(TaskSet):
    orders = []  # ตัวแปรสำหรับเก็บ Order ID ที่ถูกสร้างขึ้น

    @task(1)
    def create_order(self):
        """จำลองการสั่งซื้อสินค้า"""
        order_id = str(uuid.uuid4())
        product_id = random.randint(1, 100)
        quantity = random.randint(1, 5)

        response = self.client.post("/order", json={
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity
        })

        if response.status_code == 200:
            print(f"Order {order_id} created successfully")
            # เก็บ Order ID ที่สร้างสำเร็จ
            self.orders.append(order_id)
        else:
            print(f"Failed to create order {order_id}")

    @task(2)
    def check_inventory(self):
        """จำลองการตรวจสอบสถานะสินค้าคงคลัง"""
        product_id = random.randint(1, 100)
        response = self.client.get(f"/inventory/{product_id}")

        if response.status_code == 200:
            print(f"Inventory for product {product_id}: {response.json()}")
        else:
            print(f"Failed to check inventory for product {product_id}")

    @task(3)
    def update_order_status(self):
        """จำลองการอัปเดตสถานะคำสั่งซื้อ"""
        if not self.orders:
            return  # ถ้าไม่มี Order ให้ข้ามการอัปเดต

        order_id = random.choice(self.orders)  # ใช้ Order ID ที่ถูกสร้างจริง
        new_status = random.choice(["pending", "shipped", "delivered", "canceled"])

        response = self.client.put(f"/order/{order_id}/status", json={"status": new_status})

        if response.status_code == 200:
            print(f"Order {order_id} status updated to {new_status}")
        else:
            print(f"Failed to update order {order_id}")

    @task(4)
    def get_product_info(self):
        """จำลองการดึงข้อมูลสินค้า"""
        product_id = random.randint(1, 100)
        response = self.client.get(f"/product/{product_id}")

        if response.status_code == 200:
            print(f"Product info for {product_id}: {response.json()}")
        else:
            print(f"Failed to get product info for {product_id}")

# กำหนดผู้ใช้และ tasks ที่ต้องทดสอบ
class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "http://localhost:8000"  # URL ของ API ที่ทดสอบ
