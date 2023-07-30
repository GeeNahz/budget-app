from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Budget, Context, Item


class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class SigninForm(AuthenticationForm):
    pass


class CreateBudgetForm(forms.ModelForm):
    # profile = forms.CharField(max_length=200, disabled=True)
    name = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={"autofocus": True}))
    actual_total_income = forms.FloatField(widget=forms.NumberInput(attrs={"required": False, "value": 0.0}))
    
    class Meta:
        model = Budget
        fields = "__all__"
        exclude = ["profile"]


class CreateContextForm(forms.ModelForm):
    class Meta:
        model = Context
        fields = "__all__"


class CreateItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"
