from django.db import models
from enumfields import EnumField
import datetime
from taskManager.enumTasks import Priority, Status
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class Task(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    title = models.CharField('Title', max_length=100)
    pub_date = datetime.datetime.now()
    finish = models.DateTimeField(null=True)
    priority = EnumField(Priority)
    status = EnumField(Status)
    information = models.TextField('Information')
    user_creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class UserProfile(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
