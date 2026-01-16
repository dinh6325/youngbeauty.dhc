from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('order-tracking/<int:order_id>/', views.order_tracking, name='order_tracking'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),

    # Admin CRUD sản phẩm
    path('admin/products/',                             views.admin_product_list,   name='admin_product_list'),
    path('admin/products/add/',                         views.admin_product_create, name='admin_product_create'),
    path('admin/products/<int:pk>/edit/',               views.admin_product_update, name='admin_product_update'),
    path('admin/products/<int:pk>/delete/',             views.admin_product_delete, name='admin_product_delete'),

    # Admin CRUD đơn hàng
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:order_id>/edit/', views.admin_order_update, name='admin_order_update'),
]
