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

# ฟังก์ชันจำลองการสร้างไฟล์ขนาดใหญ่
def generate_large_data(size_in_gb):
    return "A" * (size_in_gb * 1024 * 1024 * 1024)  # ข้อมูลขนาด size_in_gb GB

class UserBehavior(TaskSet):
    
    @task(1)
    def create_order(self):
        """จำลองการสั่งซื้อสินค้า"""
        order_id = str(uuid.uuid4())
        product_id = random.randint(1, 100)  # สุ่มสินค้า
        quantity = random.randint(1, 5)  # สุ่มจำนวนสินค้า

        cached_data = get_from_redis_cache(f"product_{product_id}")
        
        if cached_data:
            print(f"Using cached data for product {product_id}")
        else:
            response = self.client.post("/order", json={
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity
            })

            if response.status_code == 200:
                print(f"Order {order_id} created successfully")
                send_message_to_rabbitmq("orders", {"order_id": order_id, "product_id": product_id})
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
    def payment_process(self):
        """จำลองการทดสอบกระบวนการชำระเงิน"""
        order_id = str(uuid.uuid4())
        response = self.client.post(f"/payment", json={
            "order_id": order_id,
            "amount": random.uniform(10.0, 500.0)
        })

        if response.status_code == 200:
            print(f"Payment for order {order_id} processed successfully")
        else:
            print(f"Failed to process payment for order {order_id}")

    @task(4)
    def upload_large_file(self):
        """จำลองการอัปโหลดไฟล์ขนาดใหญ่ (1GB ขึ้นไป)"""
        large_data = generate_large_data(1)  # สร้างข้อมูลขนาด 1GB
        response = self.client.post("/upload", data=large_data)

        if response.status_code == 200:
            print("Large file uploaded successfully")
        else:
            print(f"Failed to upload large file: {response.status_code}")

    @task(5)
    def process_large_json(self):
        """จำลองการส่งข้อมูล JSON ขนาดใหญ่"""
        large_json_data = {
            "id": str(uuid.uuid4()),
            "data": generate_large_data(1)  # ส่งข้อมูล JSON ขนาด 1GB
        }
        
        response = self.client.post("/process-large-json", json=large_json_data)

        if response.status_code == 200:
            print("Large JSON processed successfully")
        else:
            print(f"Failed to process large JSON: {response.status_code}")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = ""  # URL ของ API ที่ทดสอบ
