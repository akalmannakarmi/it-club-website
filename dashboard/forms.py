from django import forms
from user.models import User

BASE_INPUT_CLASS = (
    "w-full bg-slate-950 border border-slate-800 rounded-xl "
    "px-4 py-2 text-slate-200 placeholder-slate-500 "
    "focus:outline-none focus:ring-2 focus:ring-indigo-500"
)

class MemberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "faculty",
            "batch",
            "is_active",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Username"
            }),
            "email": forms.EmailInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Email address"
            }),
            "phone": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Phone number"
            }),
            "faculty": forms.Select(attrs={
                "class": BASE_INPUT_CLASS
            }),
            "batch": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Batch"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 rounded border-slate-700 bg-slate-900 text-indigo-600"
            }),
        }
