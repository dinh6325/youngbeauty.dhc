# ecommerce/urls.py
from django.contrib import admin
from django.urls import path, include

# Thêm 2 dòng import này:
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path("payments/", include("payments.urls")),
]

# Cho phép phục vụ media files (chỉ khi DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
