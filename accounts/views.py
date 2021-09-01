from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, auth
from django.contrib import messages

# Create your views here.

def register(request):
    # When submitted
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Confirm password is different
        if password1 != password2:     
            messages.info(request, 'Passwords don\'t match')           
            return redirect('accounts:register')
            
        # Username taken
        elif User.objects.filter(username=username).exists():    
            messages.info(request, 'Username already taken')           
            return redirect('accounts:register')

        # Email taken
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already taken')           
            return redirect('accounts:register')

        # Save new user
        else:
            user = User.objects.create_user(username=username, password=password1, 
                                email=email, first_name=first_name, last_name=last_name)
            return redirect('accounts:login')

    # Register page
    else:
        return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print("username: " + username + ", password: " + password)

        user = authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('webapp:index')
        else:
            messages.info(request, "Invalid credentials")
            return redirect('accounts:login')
    else:
        return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('webapp:index')