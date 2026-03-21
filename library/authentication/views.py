from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser


def home(request):
    return render(request, 'authentication/home.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = int(request.POST.get('role', 0))

        errors = []

        if not first_name or not last_name or not email or not password:
            errors.append('All fields except middle name are required.')

        if password != password_confirm:
            errors.append('Passwords do not match.')

        if CustomUser.objects.filter(email=email).exists():
            errors.append('A user with this email already exists.')

        if errors:
            return render(request, 'authentication/register.html', {
                'errors': errors,
                'first_name': first_name,
                'last_name': last_name,
                'middle_name': middle_name,
                'email': email,
                'role': role,
            })

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            role=role,
            is_active=True,
        )
        login(request, user)
        return redirect('authentication:home')

    return render(request, 'authentication/register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('authentication:home')
        else:
            return render(request, 'authentication/login.html', {
                'error': 'Invalid email or password.',
                'email': email,
            })

    return render(request, 'authentication/login.html')


@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('authentication:home')


@login_required(login_url='/login/')
def user_list(request):
    if request.user.role != 1:
        return render(request, 'authentication/access_denied.html')

    users = CustomUser.objects.all()
    return render(request, 'authentication/user_list.html', {'users': users})


@login_required(login_url='/login/')
def user_detail(request, user_id):
    if request.user.role != 1:
        return render(request, 'authentication/access_denied.html')

    user = CustomUser.get_by_id(user_id)
    if user is None:
        return render(request, 'authentication/user_not_found.html')

    return render(request, 'authentication/user_detail.html', {'profile_user': user})
