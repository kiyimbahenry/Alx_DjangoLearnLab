from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Post, Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def post_list(request):
    posts = Post.objects.all()
    context = {'posts': posts}
    return render(request, 'blog/post_list.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    context = {'form': form}
    return render(request, 'blog/register.html', context)

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('post_list')
    else:
        form = AuthenticationForm()
    
    context = {'form': form}
    return render(request, 'blog/login.html', context)

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('post_list')

@login_required
def profile(request):
    if request.method == 'POST':
        # Handle user update
        user_form = UserUpdateForm(request.POST, instance=request.user)
        # Handle profile update
        try:
            profile_instance = request.user.profile
        except Profile.DoesNotExist:
            profile_instance = Profile.objects.create(user=request.user)
        
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=profile_instance
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        try:
            profile_form = ProfileUpdateForm(instance=request.user.profile)
        except Profile.DoesNotExist:
            profile_instance = Profile.objects.create(user=request.user)
            profile_form = ProfileUpdateForm(instance=profile_instance)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'blog/profile.html', context)
