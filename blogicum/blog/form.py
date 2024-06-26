from django import forms
from django.utils import timezone

from .models import Comments, Post


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
