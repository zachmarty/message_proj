from users.apps import UsersConfig
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from users.views import RegisterView, VerifyView, generate_new_password

app_name = UsersConfig.name

urlpatterns = [
    path("", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout", LogoutView.as_view(), name="logount"),
    path("register", RegisterView.as_view(), name="register"),
    path("verify", VerifyView.as_view(), name="verify"),
    path("genpass", generate_new_password, name="generate_new_password"),
]
