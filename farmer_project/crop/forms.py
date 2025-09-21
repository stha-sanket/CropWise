from django import forms
from .models import LearningContent

class LearningContentForm(forms.ModelForm):
    class Meta:
        model = LearningContent
        fields = ['title', 'description', 'image']
