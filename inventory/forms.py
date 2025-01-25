# inventory/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
    
    
    
# inventory/forms.py
from .models import InvitationCode  # Asegúrate de que esta línea esté al principio
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class StaffUserCreationForm(UserCreationForm):
    invitation_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "invitation_code")

    def clean_invitation_code(self):
        code = self.cleaned_data.get('invitation_code')
        try:
            invitation = InvitationCode.objects.get(code=code, is_used=False)
        except InvitationCode.DoesNotExist:
            raise forms.ValidationError("Código de invitación inválido o ya usado")
        return code
    
