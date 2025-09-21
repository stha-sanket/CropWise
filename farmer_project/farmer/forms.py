from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-focus pl-10 w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none transition placeholder-gray-500',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input-focus pl-10 w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none transition placeholder-gray-500',
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'input-focus pl-10 w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none transition placeholder-gray-500',
            }),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input-focus pl-10 w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none transition placeholder-gray-500',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input-focus pl-10 w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none transition placeholder-gray-500',
    }))