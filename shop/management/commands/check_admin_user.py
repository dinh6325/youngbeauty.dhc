from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Check the admin user status and password correctness.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = 'admin123'

        user_qs = User.objects.filter(username=username)
        if not user_qs.exists():
            self.stdout.write(self.style.ERROR(f"User '{username}' does not exist."))
            return

        user = user_qs.first()
        self.stdout.write(f"User: {user}")
        self.stdout.write(f"is_active: {user.is_active}")
        self.stdout.write(f"is_superuser: {user.is_superuser}")
        self.stdout.write(f"is_staff: {user.is_staff}")
        password_correct = user.check_password(password)
        self.stdout.write(f"Password correct for '{password}': {password_correct}")
