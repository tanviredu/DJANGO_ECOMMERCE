from django import forms
from .models import User,Profile
from django.contrib.auth.forms import UserCreationForm


class ProfileForm(forms.ModelForm):
    ''' Form for the profile '''
    class Meta:
        model = Profile
        exclude = ('user',) ## we will create the user with the signals




class SignUpForm(UserCreationForm):
    ''' Sign up form fetching form the User creation form
        and the email and password is necessary not the user '''
    class Meta:
        model  = User
        fields = ('email','password1','password2')
