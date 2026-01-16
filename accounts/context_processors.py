from django.contrib.auth import get_user_model

User = get_user_model()

def user_count(request):
    if request.user.is_authenticated and request.user.is_superuser:
        count = User.objects.count()
    else:
        count = None
    return {'user_count': count}
