from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from .models import Room, User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['avatar' ,'name', 'username', 'email', 'password1', 'password2']
        # fields = '__all__'

class RoomForm(ModelForm):
    '''Форма создания поста'''
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    '''pass'''
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
