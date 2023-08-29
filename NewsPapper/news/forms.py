from django.forms import ModelForm
from .models import Post
from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class NewsForm(ModelForm):

    class Meta:
        model = Post
        fields = ['author', 'postType', 'postCategory', 'title', 'text']
        widgets = {
            'author': forms.Select(attrs={
                'class': 'form-control'
            }),
            'postType': forms.Select(attrs={
                'class': 'form-control'
            }),
            'postCategory': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter title of post'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write you text in here'
            }),
        }


class MySignupForm(SignupForm):

    def save(self, request):
        user = super(MySignupForm, self).save(request)
        common_group = Group.objects.get_or_create(name='common')[0]
        common_group.user_set.add(user)
        return user