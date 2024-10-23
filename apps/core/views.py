from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home(request):
    template = "core/home.html"
    context = {}

    return render(request, template, context)


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect("administrator:dashboard")
    elif request.user.profile.phone_number:
        return redirect("bettor:dashboard")
    else:
        return redirect("core:home")
