"""
Views for 'web' app
"""
import traceback

from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import get_root_items_recursive, get_suggested_items, \
    add_item_recursive, remove_item_recursive, SharedItem
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


def shared_items(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('/login?err=Login required')
    user = User.objects.filter(username=username)
    if len(user) == 0:
        return redirect('/login?err=No such user')
    user = user[0]
    errors = []
    messages = []
    if not user.is_superuser:
        return redirect('/')
    if request.POST.get('add', None):
        print('Requested to add items')
        location = request.POST.get('location')
        while location[-1] == '/':
            location = location[:-1]
        print('Location : ' + location)
        permission = request.POST.get('permission', 'all')
        print('Permission : ' + permission)
        permission = permission.lower()
        if permission not in ('all', 'admin', 'self'):
            permission = 'all'
        try:
            item_count = add_item_recursive(location, user, permission)
            messages.append('Successfully added {0} items'.format(item_count))
        except Exception:
            errors.append('Problem adding item(s)')
            traceback.print_exc()
    elif request.POST.get('remove', None):
        _id = request.POST.get('id')
        item = SharedItem.objects.filter(id=int(_id))
        if len(item) == 0:
            errors.append('The item you are trying to delete is not found')
        else:
            item_count = remove_item_recursive(item[0])
            messages.append('Successfully deleted {0} items'.format(item_count))
    tree = get_root_items_recursive(user)
    return render(
        request,
        'items.html',
        {
            'tree': tree,
            'number_of_errors': len(errors),
            'number_of_mesages': len(messages),
            'errors': errors,
            'messages': messages
        }
    )
