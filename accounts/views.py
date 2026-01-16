from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'accounts/admin_user_list.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_users(request):
    if request.method == 'POST':
        user_ids = request.POST.getlist('user_ids')
        # Prevent deleting self or superusers accidentally
        user_ids = [uid for uid in user_ids if uid != str(request.user.id)]
        users_to_delete = User.objects.filter(id__in=user_ids).exclude(is_superuser=True)
        deleted_count = users_to_delete.count()
        users_to_delete.delete()
        messages.success(request, f"Đã xóa {deleted_count} người dùng.")
    return redirect('admin_user_list')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_superuser(request, user_id):
    user_obj = User.objects.filter(id=user_id, is_superuser=True).first()
    if not user_obj:
        messages.error(request, "Người dùng không tồn tại hoặc không phải admin.")
        return redirect('admin_user_list')

    if user_obj == request.user:
        messages.error(request, "Bạn không thể xóa chính mình.")
        return redirect('admin_user_list')

    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, f"Đã xóa admin {user_obj.username}.")
        return redirect('admin_user_list')

    return render(request, 'accounts/admin_user_confirm_delete.html', {'user_obj': user_obj})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_user_edit(request, user_id):
    user_obj = User.objects.filter(id=user_id).first()
    if not user_obj:
        messages.error(request, "Người dùng không tồn tại.")
        return redirect('admin_user_list')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật người dùng thành công.")
            return redirect('admin_user_list')
        else:
            messages.error(request, "Vui lòng sửa các lỗi bên dưới.")
    else:
        form = UserProfileForm(instance=user_obj)

    return render(request, 'accounts/admin_user_edit.html', {'form': form, 'user_obj': user_obj})
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import RegisterForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

User = get_user_model()
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Nếu là admin, chuyển đến trang CRUD sản phẩm
        if self.request.user.is_superuser:
            return reverse('shop:admin_product_list')
        return reverse('shop:home')
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # UserCreationForm.save() đã gọi set_password(password1)
            user = form.save()
            # Tự động đăng nhập
            login(request, user)
            return redirect('shop:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def user_profile(request):
    user = request.user
    return render(request, 'accounts/profile.html', {'user': user})

@login_required
def user_profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('user_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'accounts/profile_edit.html', {'form': form})
