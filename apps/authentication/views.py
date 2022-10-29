from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .forms import LoginForm, SignUpForm, EditProfileForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                print('User: ', user.is_worker)
                if request.user.is_worker:
                    return redirect(reverse("sales_page"))
                return redirect(reverse("dashboard"))
            else:
                msg = "Invalid credentials"
        else:
            msg = "Error validating the form"

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            return redirect("/login/")

        else:
            msg = "Form is not valid"
    else:
        form = SignUpForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form, "msg": msg, "success": success},
    )


@staff_member_required
def register_staff(request):
    msg = None
    success = False

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        password = username + phone_number[-2:]

        try:
            user = get_user_model().objects.create(
                username=username,
                full_name=full_name,
                phone_number=phone_number,
                password=password,
            )
        except Exception as IntegrityError:
            msg = "Staff not created - Staff with the provided detail exist."
            # success =
        else:
            user.is_worker = True
            user.set_password(password)
            user.save()

            msg = f"Staff created - \n Username is {username}, and password is {password} (username + last 2 digit of phone number)"
            success = True
            messages.success(request, msg)

        # return redirect("register_staff")

    return render(
        request,
        "accounts/register_worker.html",
        {"msg": msg, "success": success},
    )


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("login")
    return redirect("login")


@login_required
def user_profile(request):
    return render(request, 'home/profile.html', {})


@login_required
def edit_profile(request):
    user = request.user
    form = EditProfileForm(instance=user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        print(form)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            return redirect('user_profile')
        else:
            messages.warning(request, 'You have an error in your form')
            return render(request, 'home/edit_profile.html', {'form': form})

    return render(request, 'home/edit_profile.html', {'form': form})