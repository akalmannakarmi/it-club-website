from django import forms
from dashboard.models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'semester', 'phone', 'faculty', 'interested_topics']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter your name',
            }),
             'semester': forms.TextInput(attrs={
                'placeholder':'semester',  
            }),
             'phone': forms.TextInput(attrs={
                'placeholder': ' phone No.',
            }),
            'interested_topics': forms.Textarea(attrs={'rows': 3}),
        }


    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip().title()
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError("Name can only contain letters and spaces.")
        return name
    

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if not phone.isdigit() or len(phone) != 10 or not phone.startswith(('98','97')):
            raise forms.ValidationError(" Please Enter your correct phone number.")
        return phone