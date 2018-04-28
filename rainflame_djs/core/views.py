from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import update_session_auth_hash, login, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth

import os

#todo: If user is signed into Facebook, don't let them authenticate with it again...
# for a default view with no user login
def index(request):
    return render(request, 'core/index.html')

def loginDirect(request):
    if request.user.is_authenticated():
        # direct already authenticated users to their info 
        return HttpResponseRedirect()
    else:
        # direct new users to signup
        # case 1: they already had an account 
            # get them to login with their facebook again
        #case 2: they have never had an account
            # go through the process of creating an account with facebook
        return login(request)

# signup manually 
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password1')
            )
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# home page, visible to anyone 
#@login_required
def home(request):
    return render(request, 'core/home.html')

# settings view, give the option to sign out from the connected facebook account 
@login_required
def settings(request):

    user = request.user
    try:
        twitter_login = user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None
    try:
        facebook_login = user.social_auth.get(provider='facebook')
        # got the access token!
        print(user.social_auth.get(provider='facebook').extra_data.get('access_token'))
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    return render(request, 'core/settings.html', {
        'twitter_login': twitter_login,
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect
    })

# when the user wants to disconnect their facebook account, prompt a password 
# don't need to do this because each user doesn't have a unique password on the
# site, just a facebook id 
@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'core/password.html', {'form': form})
