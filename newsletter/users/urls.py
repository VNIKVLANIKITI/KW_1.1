from django.urls import path
from django.contrib.auth.views import LoginView
from users.views import RegisterView, EditView, LogoutView
from users.apps import UsersConfig
from django.contrib.auth import views as auth_views

app_name = UsersConfig.name

urlpatterns = [
    path('', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('edit/', EditView.as_view(), name='edit'),
]
