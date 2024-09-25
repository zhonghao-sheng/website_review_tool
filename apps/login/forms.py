from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.validators import RegexValidator
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Provide a valid email address.')
    username_regex = RegexValidator(
        regex = r'[a-zA-Z0-9_-]{5,20}$',
        message= 'Username must be 5-20 characters long and can only contain letters, numbers, and underscores'
    )
    username = forms.CharField(validators=[username_regex], max_length=20, required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())