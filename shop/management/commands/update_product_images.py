import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from shop.models import Product, Category

class Command(BaseCommand):
    help = 'Update product images and limit products per category to 3. Run this command from the Project_Python directory where manage.py is located.'

    def handle(self, *args, **options):
        self.stdout.write(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
        media_dir = os.path.join(settings.MEDIA_ROOT, 'Products')
        self.stdout.write(f"Looking for images in: {media_dir}")
        if not os.path.exists(media_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {media_dir}"))
            return

        # List image files in media/Products/
        image_files = [f for f in os.listdir(media_dir) if os.path.isfile(os.path.join(media_dir, f))]
        if not image_files:
            self.stdout.write(self.style.ERROR(f"No image files found in {media_dir}"))
            return

        products = Product.objects.all().order_by('id')
        if not products:
            self.stdout.write(self.style.WARNING("No products found in the database."))
            return

        self.stdout.write(f"Found {len(products)} products and {len(image_files)} images.")
        self.stdout.write("Make sure to run this command from the Project_Python directory where manage.py is located.")

        # Assign unique images to products up to the number of images
        for i, product in enumerate(products):
            if i < len(image_files):
                image_file = image_files[i]
                full_image_path = os.path.join(media_dir, image_file)
                if not os.path.exists(full_image_path):
                    self.stdout.write(self.style.WARNING(f"Image file does not exist: {full_image_path}. Skipping product '{product.name}'."))
                    continue
                with open(full_image_path, 'rb') as f:
                    django_file = File(f)
                    product.image.save(image_file, django_file, save=True)
                self.stdout.write(f"Updated product '{product.name}' with image '{image_file}'")
            else:
                # Clear image for products beyond available images
                product.image.delete(save=True)
                self.stdout.write(f"Cleared image for product '{product.name}'")

        self.stdout.write(self.style.SUCCESS("Product images updated successfully with unique images assigned."))

        # Delete products without images
        products_without_images = Product.objects.filter(image__isnull=True) | Product.objects.filter(image='')
        count_deleted, _ = products_without_images.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count_deleted} products without images."))

        # Limit products per category to 3
        categories = Category.objects.all()
        for category in categories:
            products_in_cat = Product.objects.filter(category=category).order_by('id')
            products_to_keep = products_in_cat[:3]
            products_to_delete = products_in_cat[3:]
            count_del = products_to_delete.count()
            # Fix: cannot delete queryset slice directly, get IDs and delete by filter
            ids_to_delete = products_to_delete.values_list('id', flat=True)
            Product.objects.filter(id__in=ids_to_delete).delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count_del} products in category '{category.name}', kept 3."))

        self.stdout.write(self.style.SUCCESS("Limited products per category to 3."))
