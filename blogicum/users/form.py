from django import forms
<<<<<<< HEAD
=======
from django.contrib.auth.forms import UserChangeForm
>>>>>>> 6ba8cd4bdf27b74e5f926cb44eaca490ac29a0a6
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


User = get_user_model()


<<<<<<< HEAD
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1')


=======
>>>>>>> 6ba8cd4bdf27b74e5f926cb44eaca490ac29a0a6
class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']
