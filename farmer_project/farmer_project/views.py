from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from farmer.models import Farmer
from crop.models import Crop, LearningContent
from farmer.forms import CustomUserCreationForm, CustomAuthenticationForm
from crop.prediction_views import get_crop_prediction_context
from django.conf import settings
from django.http import JsonResponse # Import JsonResponse
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.api_core.exceptions # Import this for specific exception handling

# Configure Gemini API
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    print(f"Gemini API Key loaded: {settings.GEMINI_API_KEY[:4]}...{settings.GEMINI_API_KEY[-4:]}")
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        system_instruction=(
            "You are a helpful AI assistant specializing in crop diseases and farming suggestions. "
            "Your primary goal is to assist farmers in identifying potential crop diseases based on their descriptions, "
            "and to provide relevant suggestions for prevention, diagnosis, and treatment. "
            "You should also offer general farming advice and best practices. "
            "If a user asks a question that is irrelevant to crop diseases, farming, or agriculture, "
            "gently steer them back to the topic or state that you can only assist with farming-related queries. "
            "Always format your responses using Markdown for clarity and readability, including bullet points, bold text, and code blocks where appropriate. "
            "Be concise but informative."
        )
    )
else:
    model = None
    print("GEMINI_API_KEY not found in settings. Gemini chatbot will not function.")

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
    context = get_crop_prediction_context(request)
    return render(request, 'recommendation.html', context)

@login_required(login_url='/login/')
def crop_information(request):
    contents = LearningContent.objects.all()
    return render(request, 'crop_information.html', {'contents': contents})

@login_required(login_url='/login/')
def chatbot(request):
    if request.method == 'GET':
        request.session['conversation_history'] = [] # Clear history on GET request (page refresh)

    conversation_history = request.session.get('conversation_history', [])
    user_message = None
    chatbot_response = None

    if request.method == 'POST':
        if 'clear_history' in request.POST:
            request.session['conversation_history'] = []
            return redirect('chatbot')

        user_message = request.POST.get('user_message')
        if user_message and model:
            try:
                # Add user message to history
                conversation_history.append({'role': 'user', 'text': user_message})

                # Prepare messages for Gemini API
                gemini_messages = []
                for msg in conversation_history:
                    gemini_messages.append({'role': msg['role'], 'parts': [msg['text']]})

                print(f"Sending messages to Gemini: {gemini_messages}")
                response = model.generate_content(
                    gemini_messages,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    },
                )
                chatbot_response = response.text
                print(f"Received response from Gemini: {chatbot_response}")

                # Add chatbot response to history
                conversation_history.append({'role': 'model', 'text': chatbot_response})

            except google.api_core.exceptions.ResourceExhausted as e:
                print(f"Quota Exceeded Error: {e}")
                chatbot_response = "I'm sorry, I've exceeded my usage quota. Please try again later or contact support."
                conversation_history.append({'role': 'model', 'text': chatbot_response})
            except Exception as e:
                print(f"Exception during Gemini API call: {e}")
                chatbot_response = f"Error communicating with the chatbot: {e}"
                conversation_history.append({'role': 'model', 'text': chatbot_response})
        elif not model:
            print("Model is None. GEMINI_API_KEY might be missing or invalid.")
            chatbot_response = "Chatbot is not configured. Please check GEMINI_API_KEY."
            conversation_history.append({'role': 'model', 'text': chatbot_response})

        request.session['conversation_history'] = conversation_history
        return JsonResponse({'chatbot_response': chatbot_response})

    context = {
        'conversation_history': conversation_history,
    }
    return render(request, 'chatbot.html', context)

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
