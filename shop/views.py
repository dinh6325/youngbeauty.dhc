from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Category, Order, OrderItem
from django.contrib.auth.models import User
from .forms import ProductForm
from .forms import OrderStatusForm
from django.shortcuts import redirect

def home(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('shop:admin_product_list')
    else:
        # Lấy hết category để render menu
        categories = Category.objects.all()
        # (Tuỳ chọn) Lấy sản phẩm để hiển thị trên trang chủ
        products = Product.objects.all()
        return render(request, 'shop/home.html', {
            'categories': categories,
            'products': products,
        })
# Hiển thị danh sách sản phẩm với tìm kiếm & lọc
def superuser_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
# shop/views.py
from django.shortcuts import get_object_or_404

def category_products(request, slug):
    categories = Category.objects.all()
    cat = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=cat)
    return render(request, 'shop/product_list.html', {
        'categories': categories,
        'products': products,
        'current_category': slug,
        'q': '',
        'category_filter': '',
        'category_slug': None,
        # bỏ qua các filter khác
    })  
from django.core.paginator import Paginator

def home(request):
    categories = Category.objects.all()
    qs = Product.objects.all()

    # Get filter parameters
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    rating_min = request.GET.get('rating_min', '')

    # Apply filters
    if q:
        qs = qs.filter(name__icontains=q)
    if cat:
        try:
            cat_id = int(cat)
            qs = qs.filter(category__id=cat_id)
        except ValueError:
            pass
    if price_min:
        try:
            price_min_val = float(price_min)
            qs = qs.filter(price__gte=price_min_val)
        except ValueError:
            pass
    if price_max:
        try:
            price_max_val = float(price_max)
            qs = qs.filter(price__lte=price_max_val)
        except ValueError:
            pass
    if rating_min:
        try:
            rating_min_val = int(rating_min)
            qs = qs.filter(rating__gte=rating_min_val)
        except ValueError:
            pass

    # Pagination
    qs = qs.order_by('id')  # Ensure queryset is ordered for pagination
    paginator = Paginator(qs, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/product_list.html', {
        'products': page_obj,
        'categories': categories,
        'q': q,
        'category_filter': cat,
        'price_min': price_min,
        'price_max': price_max,
        'rating_min': rating_min,
        'page_obj': page_obj,
    })

# Chi tiết sản phẩm

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import ProductCommentForm, OrderStatusForm, CheckoutForm

from django.db import OperationalError

from django.contrib import messages

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        from .models import ProductComment
        comments = ProductComment.objects.filter(product=product).order_by('-created_at')
        print(f"Fetched {comments.count()} comments for product {product_id}")
        for c in comments:
            print(f"Comment by {c.user.username}: {c.comment}")
    except OperationalError:
        comments = []
        print("OperationalError when fetching comments")
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = ProductCommentForm(request.POST)
        if form.is_valid():
            try:
                comment = form.save(commit=False)
                comment.user = request.user
                comment.product = product
                comment.save()
                print(f"Saved comment by {comment.user.username} for product {product_id}")
                messages.success(request, "Đánh giá của bạn đã được gửi thành công.")
                return redirect('shop:product_detail', product_id=product.id)
            except OperationalError:
                messages.error(request, "Hiện tại không thể gửi đánh giá. Vui lòng thử lại sau.")
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, "Vui lòng sửa các lỗi trong biểu mẫu.")
    else:
        form = ProductCommentForm()
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'comments': comments,
        'form': form,
    })

# Giỏ hàng (session-based)

def cart_view(request):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        if 'selected_products' in request.POST:
            selected = request.POST.getlist('selected_products')
            if not selected:
                messages.error(request, "Vui lòng chọn ít nhất một sản phẩm để thanh toán.")
                return redirect('shop:cart')
            selected_cart = {pid: cart[pid] for pid in selected if pid in cart}
            request.session['selected_cart'] = selected_cart
            return redirect('shop:checkout')
        else:
            pid = request.POST.get('product_id')
            qty_str = request.POST.get('quantity', '1')
            try:
                qty = int(qty_str)
                if qty < 1:
                    messages.error(request, "Số lượng phải là số nguyên dương.")
                    return redirect('shop:cart')
            except ValueError:
                messages.error(request, "Số lượng không hợp lệ.")
                return redirect('shop:cart')

            try:
                product = Product.objects.get(id=pid)
            except Product.DoesNotExist:
                messages.error(request, "Sản phẩm không tồn tại.")
                return redirect('shop:cart')

            current_qty = cart.get(str(pid), 0)
            new_qty = current_qty + qty
            if new_qty > product.stock:
                messages.error(request, f"Số lượng vượt quá tồn kho. Tồn kho hiện tại: {product.stock}.")
                return redirect('shop:cart')

            cart[str(pid)] = new_qty
            request.session['cart'] = cart
            messages.success(request, f"Đã thêm {qty} sản phẩm '{product.name}' vào giỏ hàng.")
            return redirect('shop:cart')

    items, total = [], 0
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=pid)
        except Product.DoesNotExist:
            continue
        line_total = product.price * qty
        items.append({
            'product': product,
            'quantity': qty,
            'price_vnd': product.price_vnd,
            'line_total_vnd': f"{int(line_total):,}".replace(",", ".") + " VND",
        })
        total += line_total
    total_vnd = f"{int(total):,}".replace(",", ".") + " VND"
    return render(request, 'shop/cart.html', {
        'items': items,
        'total': total,
        'total_vnd': total_vnd,
    })

@login_required
def checkout(request):
    selected_cart = request.session.get('selected_cart', {})
    cart = selected_cart if selected_cart else request.session.get('cart', {})
    if not cart:
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
            )
            for pid, qty in cart.items():
                product = get_object_or_404(Product, id=pid)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=qty,
                )
                # Giảm số lượng tồn kho sản phẩm
                product.stock -= qty
                if product.stock < 0:
                    product.stock = 0
                product.save()
            # Xóa sản phẩm đã chọn khỏi giỏ hàng sau khi đặt xong
            if 'selected_cart' in request.session:
                for pid in request.session['selected_cart']:
                    if pid in request.session.get('cart', {}):
                        del request.session['cart'][pid]
                del request.session['selected_cart']
            else:
                del request.session['cart']

            # Get selected payment method
            payment_method = request.POST.get('payment_method', 'BANK_TRANSFER')

            if payment_method == 'PAYOS':
                return redirect('pay', order_id=order.id)
            elif payment_method == 'BANK_TRANSFER':
                # Redirect to bank transfer confirmation or similar page
                return redirect('shop:order_success', order_id=order.id)
            elif payment_method == 'COD':
                # Redirect to COD confirmation or similar page
                return redirect('shop:order_success', order_id=order.id)
            elif payment_method == 'BANK_CARD':
                # Redirect to card payment page or handle accordingly
                return redirect('shop:order_success', order_id=order.id)
            else:
                # Default fallback
                return redirect('shop:order_success', order_id=order.id)
    else:
        form = CheckoutForm()

    # Chuẩn bị dữ liệu để hiển thị lên template
    items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        line_total = product.price * qty
        items.append({
            'product': product,
            'quantity': qty,
            'price_vnd': product.price_vnd,
            'line_total': line_total,
            'line_total_vnd': f"{int(line_total):,}".replace(",", ".") + " VND",
        })
        total += line_total
    total_vnd = f"{int(total):,}".replace(",", ".") + " VND"

    return render(request, 'shop/checkout.html', {
        'form': form,
        'items': items,
        'total': total,
        'total_vnd': total_vnd,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_success.html', {'order': order})

from django.apps import apps

@login_required
def order_tracking(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    try:
        # Try common related names
        if hasattr(order, 'orderitem_set'):
            order_items = order.orderitem_set.all()
        elif hasattr(order, 'order_items'):
            order_items = order.order_items.all()
        elif hasattr(order, 'items'):
            order_items = order.items.all()
        else:
            # Try to find related objects dynamically
            OrderItem = apps.get_model('shop', 'OrderItem')
            order_items = OrderItem.objects.filter(order=order)
    except Exception:
        order_items = []
    # Calculate total for each item
    for item in order_items:
        item.total = item.price * item.quantity
    return render(request, 'shop/order_tracking.html', {'order': order, 'order_items': order_items})
# Decorator chỉ cho phép superuser
 
# Admin CRUD sản phẩm
@superuser_required
def admin_product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'shop/admin_product_list.html', {'products': products})

@superuser_required
def admin_dashboard(request):
    return render(request, 'shop/admin_dashboard.html')

@superuser_required
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully.")
            return redirect('shop:admin_product_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()
    return render(request, 'shop/admin_product_form.html', {'form': form})

@superuser_required
def admin_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    print(f"Admin update product view called for product id: {pk}")
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            print(f"Product {pk} updated successfully.")
            messages.success(request, "Product updated successfully.")
            return redirect('shop:admin_product_list')
        else:
            print(f"Form errors on update: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/admin_product_form.html', {
        'form': form,
        'product': product,
    })

@superuser_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    print(f"Admin delete product view called for product id: {pk}")
    if request.method == 'POST':
        product.delete()
        print(f"Product {pk} deleted successfully.")
        return redirect('shop:admin_product_list')
    return render(request, 'shop/admin_product_confirm_delete.html', {
        'product': product,
    })

@superuser_required
def admin_order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'shop/admin_order_list.html', {'orders': orders})

@superuser_required
def admin_order_update(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.id} status updated successfully.")
            return redirect('shop:admin_order_list')
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'shop/admin_order_update.html', {'form': form, 'order': order})
