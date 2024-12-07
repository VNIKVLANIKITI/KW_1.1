from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import User
from django import forms


class UserRegisterForm (UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'phone', 'country', 'password1', 'password2',)


class UserEditForm (UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'phone', 'country', 'avatar',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.HiddenInput()

class UserLogoutForm (UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)