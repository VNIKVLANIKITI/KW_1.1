from users.forms import UserRegisterForm, UserEditForm
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LogoutView
from users.models import User
from users.forms import UserLogoutForm
from django.urls import reverse_lazy


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy('users:login')


class EditView(UpdateView):
    model = User
    form_class = UserEditForm
    template_name = "users/edit.html"
    success_url = reverse_lazy('users:edit')

    def get_object(self, queryset=None):
        return self.request.user


class LogoutView(UpdateView):
    model = User
    form_class = UserLogoutForm
    template_name = "users/logout.html"
    success_url = reverse_lazy('/')
