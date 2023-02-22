from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.generic import TemplateView


class AboutTemplateView(TemplateView):
    template_name = "about.html"


def logout_view(request):
    logout(request)
    return redirect("login")


def login_view(request):
    error_message = None
    form = AuthenticationForm()

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                if request.GET.get("next"):
                    return redirect(request.GET.get("next"))
                else:
                    return redirect("reviewer:home")

        else:
            error_message = "Ups... something went wrong"

    contect = {"form": form, "error_message": error_message}

    return render(request, "auth/login.html", contect)


def register_view(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect("reviewer:home")

    return render(request, "auth/register.html", {"form": form})
