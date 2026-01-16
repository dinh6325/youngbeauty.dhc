from .models import Order

def latest_order_status(request):
    if request.user.is_authenticated:
        latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        if latest_order:
            return {'latest_order_status': latest_order.status, 'latest_order_id': latest_order.id}
    return {}
