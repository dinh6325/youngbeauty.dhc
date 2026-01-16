
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category    = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    image       = models.ImageField(upload_to='Products/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    stock       = models.IntegerField(default=0)
    rating      = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def price_vnd(self):
        """
        Format price as VND with thousand separators.
        """
        try:
            amount = int(self.price)
        except (ValueError, TypeError):
            return str(self.price)
        s = f"{amount:,}".replace(",", ".")
        return f"{s} VND"


# ------------ Models cho Order & OrderItem ------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Đã đặt'),
        ('processing', 'Đang xử lý'),
        ('shipping', 'Đang giao'),
        ('delivered', 'Giao thành công'),
    ]

    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name   = models.CharField(max_length=255)
    address     = models.CharField(max_length=500)
    city        = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    created_at  = models.DateTimeField(auto_now_add=True)
    paid        = models.BooleanField(default=False)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    @property
    def total_cost(self):
        return sum(item.cost for item in self.items.all())

    @property
    def total_cost_vnd(self):
        try:
            amount = int(self.total_cost)
        except (ValueError, TypeError):
            return str(self.total_cost)
        s = f"{amount:,}".replace(",", ".")
        return f"{s} VND"


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    price    = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def cost(self):
        return self.price * self.quantity

    @property
    def cost_vnd(self):
        """
        Format line total as VND with thousand separators.
        """
        try:
            amount = int(self.cost)
        except (ValueError, TypeError):
            return str(self.cost)
        s = f"{amount:,}".replace(",", ".")
        return f"{s} VND"

    @property
    def price_vnd(self):
        """
        Format unit price as VND with thousand separators.
        """
        try:
            amount = int(self.price)
        except (ValueError, TypeError):
            return str(self.price)
        s = f"{amount:,}".replace(",", ".")
        return f"{s} VND"


class ProductComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"
