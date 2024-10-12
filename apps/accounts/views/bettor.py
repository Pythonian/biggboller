from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def bettor_dashboard(request):
    template = "accounts/bettor/dashboard.html"
    context = {}

    return render(request, template, context)
