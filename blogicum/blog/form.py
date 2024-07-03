from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm

from .models import Comments, Post, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
            })
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['pub_date'].initial = timezone.now()


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('text',)


class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']
