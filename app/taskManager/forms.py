from .models import Task
from django.forms import ModelForm
from django import forms


class TaskAdding(ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'finish': forms.DateTimeInput(attrs={'placeholder': 'YYYY-MM-DD HH:MM'}),
        }
        exclude = ['id', 'pub_date', 'user_creator']
