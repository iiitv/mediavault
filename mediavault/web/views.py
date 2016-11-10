"""
Views for 'web' app
"""
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import get_root_items_recursive, get_suggested_items
from .forms import LoginForm


def home(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('/login?err=Login required')
    user = User.objects.filter(username=username)
    if len(user) == 0:
        return redirect('/login?err=No such user')
    user = user[0]
    item_tree = get_root_items_recursive(user)
    suggested_items = get_suggested_items(user)
    return render(
        request,
        'home.html',
        {
            'is_admin': user.is_superuser,
            'tree': item_tree,
            'suggestions': suggested_items
        }
    )


def login(request):
    if request.session.get('username', None):
        return redirect('/')
    error = request.GET.get('err', None)
    if request.POST.get('login', None):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.filter(username=username)
            if len(user) == 1:
                user = user[0]
                if user.check_password(password):
                    token = Token.objects.get(user=user)
                    response = redirect('/')
                    request.session['username'] = user.username
                    request.session['key'] = token.key
                    return response
        error = 'Invalid Username and/or Password'
    return render(
        request,
        'login.html',
        {
            'error': error
        }
    )
