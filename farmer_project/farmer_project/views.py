from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from farmer.models import Farmer
from crop.models import Crop
from farmer.forms import CustomUserCreationForm, CustomAuthenticationForm

def home(request):
    farmers = Farmer.objects.all()
    crops = Crop.objects.all()
    context = {
        'farmers': farmers,
        'crops': crops
    }
    return render(request, 'home.html', context)

@login_required(login_url='/login/')
def recommendation(request):
    return render(request, 'recommendation.html')

@login_required(login_url='/login/')
def crop_information(request):
    return render(request, 'crop_information.html')

@login_required(login_url='/login/')
def chatbot(request):
    return render(request, 'chatbot.html')

def contact(request):
    return render(request, 'contact.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')