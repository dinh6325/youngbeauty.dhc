import time
from django.shortcuts import redirect, render, get_object_or_404
from payos import PayOS
from payos.types import CreatePaymentLinkRequest   # ✅ import đúng class

# ⚡ Thông tin cấu hình PayOS (test credentials)
payOS = PayOS(
    client_id="518e8d5f-420d-4277-819b-cb0d752acf55",
    api_key="eeacd414-ce38-4a12-aa48-5702674912c8",
    checksum_key="360443da3d9b6cba9bdc2b36a1c04b5ae63653c60c3c43b7138edc5063546d25"
)

def create_payment(request):
    # Tạo orderCode duy nhất (timestamp)
    order_code = int(time.time())

    # Thông tin sản phẩm
    item = {
        "name": "Mì tôm Hảo Hảo ly",
        "quantity": 1,
        "price": 1000,
    }

    # ✅ Tạo object payment_data theo đúng SDK
    payment_data = CreatePaymentLinkRequest(
        order_code=order_code,
        amount=1000,
        description="THANH TOÁN XONG",
        items=[item],
        cancel_url="http://localhost:8000/payments/payment-cancel/",
        return_url="http://localhost:8000/payments/payment-success/"
    )

    # ✅ Gọi API tạo link thanh toán
    payment_link = payOS.payment_requests.create(payment_data=payment_data)

    # Redirect sang trang thanh toán PayOS
    return redirect(payment_link.checkout_url)

def payment_success(request):
    order_id = request.GET.get('orderCode')
    if order_id:
        return redirect('shop:order_tracking', order_id=order_id)
    else:
        return render(request, "payments/payment_success.html")

def payment_cancel(request):
    return render(request, "payments/payment_cancel.html")

def pay(request, order_id):
    from shop.models import Order, OrderItem
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_code = order.id  # Use order.id as order_code

    # Get order items
    order_items = OrderItem.objects.filter(order=order)
    items = []
    total = 0
    for item in order_items:
        items.append({
            "name": item.product.name,
            "quantity": item.quantity,
            "price": int(item.price),  # Price in VND
        })
        total += item.price * item.quantity

    payment_data = CreatePaymentLinkRequest(
        order_code=order_code,
        amount=int(total),  # Total amount in VND
        description=f"Thanh toán đơn hàng #{order.id}",
        items=items,
        cancel_url="http://localhost:8000/payments/payment-cancel/",
        return_url="http://localhost:8000/payments/payment-success/"
    )

    payment_link = payOS.payment_requests.create(payment_data=payment_data)
    return redirect(payment_link.checkout_url)
