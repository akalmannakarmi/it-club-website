from django import forms
from user.models import User


class MemberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "faculty", "batch", "phone", "interested_topics"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Enter your name",
                }
            ),
            "batch": forms.TextInput(
                attrs={
                    "placeholder": 'e.g. "2025"',
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": " phone No.",
                }
            ),
            "interested_topics": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if (
            not phone.isdigit()
            or len(phone) != 10
            or not phone.startswith(("98", "97"))
        ):
            raise forms.ValidationError(" Please Enter your correct phone number.")
        return phone
