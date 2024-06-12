from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']
