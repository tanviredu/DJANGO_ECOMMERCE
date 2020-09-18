from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.urls import reverse
from .models import User,Profile
from .forms import SignUpForm,ProfileForm
from django.contrib import messages


##froms import here
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate

def sign_up(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            # profile is created by signals
            form.save()
            messages.success(request,"Account is created Successfully")
            return HttpResponseRedirect(reverse('App_LOgin:login'))
    return render(request,'App_LOgin/signup.html',{'form':form})
            


def login_user(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            ## this username is email
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user     = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                ## this is temporary
                return HttpResponse("you are logged in")
    return render(request,"App_LOgin/login.html",{'form':form})
    
@login_required
def logout_user(request):
    logout(request)
    messages.warning(request,"You are logged out")
    ## this is temporary
    return HttpResponse("you are logged out")

@login_required
def user_profile(request):
    profile = Profile.objects.get(user=request.user)
    form    = ProfileForm(instance=profile)
    if request.method == "POST":
        form = ProfileForm(request.POST,instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request,'Changed Saved')
    return render(request,'App_LOgin/change_profile.html',{'form':form})