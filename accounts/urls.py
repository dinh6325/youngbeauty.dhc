# accounts/urls.py
from django.urls import path
from . import views
from .views import CustomLoginView, register, user_logout, user_profile, user_profile_edit

urlpatterns = [
    # existing url patterns here
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/delete/', views.delete_users, name='delete_users'),
    path('admin/users/edit/<int:user_id>/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/delete_superuser/<int:user_id>/', views.delete_superuser, name='delete_superuser'),
    path('login/',    CustomLoginView.as_view(), name='login'),
    path('logout/',   user_logout,                name='logout'),
    path('register/', register,                   name='register'),
    path('profile/',  user_profile,               name='user_profile'),
    path('profile/edit/', user_profile_edit,      name='user_profile_edit'),
]
