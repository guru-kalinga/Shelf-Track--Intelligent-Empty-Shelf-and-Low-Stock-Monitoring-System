from django import forms
from django.contrib.auth.models import User
from .models import Employee_Enrol


class Employee_EditForm(forms.ModelForm):
    class Meta:
        model = Employee_Enrol 
        fields = ['name', 'phone', 'email']

class Employee_EditForm1(forms.ModelForm):

    class Meta:
        model =User
        fields = ['username',  'password']