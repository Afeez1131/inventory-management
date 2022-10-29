
from django.urls import path
from .views import login_view, register_user, logout_user, register_staff, user_profile, edit_profile
# from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/admin/', register_user, name="register"),
    path('register/staff/', register_staff, name="register_staff"),
    path("logout/", logout_user, name="logout"),

    path("profile/", user_profile, name="user_profile"),
    path("edit-profile/", edit_profile, name="edit_profile"),

]
