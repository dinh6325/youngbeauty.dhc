import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from shop.models import Product, Category

class Command(BaseCommand):
    help = 'Update product information from JSON fixture file for CPU, Màn hình, and Card đồ họa categories, matching by product name.'

    def handle(self, *args, **options):
        json_path = os.path.join(settings.BASE_DIR, 'shop', 'fixtures', 'tech_products.json')
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"JSON file not found: {json_path}"))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Category names to update
        target_categories = ['CPU', 'Màn hình', 'Card đồ họa']

        # Build category map: pk to Category instance
        categories = Category.objects.all()
        category_map = {cat.pk: cat for cat in categories}

        updated_count = 0
        for entry in data:
            if entry['model'] == 'shop.product':
                fields = entry['fields']
                category_pk = fields.get('category')
                category = category_map.get(category_pk)
                if not category or category.name not in target_categories:
                    continue

                name = fields.get('name')
                try:
                    product = Product.objects.get(name=name)
                except Product.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Product with name '{name}' not found. Skipping."))
                    continue

                # Update product fields
                product.description = fields.get('description', product.description)
                product.price = fields.get('price', product.price)
                product.stock = fields.get('stock', product.stock)
                product.rating = fields.get('rating', product.rating)

                # Update category if exists
                if category:
                    product.category = category

                # Update image path if provided
                image_path = fields.get('image')
                if image_path:
                    product.image = image_path

                product.save()
                updated_count += 1
                self.stdout.write(f"Updated product '{product.name}' in category '{category.name}'")

        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} products in categories {', '.join(target_categories)} from JSON file."))
