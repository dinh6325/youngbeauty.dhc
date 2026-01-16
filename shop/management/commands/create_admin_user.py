from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a superuser/admin account with default credentials.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'

        user_qs = User.objects.filter(username=username)
        if user_qs.exists():
            user = user_qs.first()
            user.set_password(password)
            user.is_active = True
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User '{username}' already exists. Password has been reset."))
            self.stdout.write("Please login and change the password immediately.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
        self.stdout.write("Please login and change the password immediately.")
