import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api-merchant.payos.vn/v2/payment-requests"
headers = {
    "x-client-id": os.getenv("518e8d5f-420d-4277-819b-cb0d752acf55"),
    "x-api-key": os.getenv("eeacd414-ce38-4a12-aa48-5702674912c8"),
    "Content-Type": "application/json",
}
data = {
    "orderCode": "test12345",
    "amount": 10000,
    "description": "Thanh toán test PayOS",
    "returnUrl": "http://127.0.0.1:8000/payments/success/",
    "cancelUrl": "http://127.0.0.1:8000/payments/cancel/",
}

response = requests.post(url, headers=headers, json=data).json()
print(response)
