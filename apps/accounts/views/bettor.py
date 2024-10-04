from django.shortcuts import render


def bettor_dashboard(request):
    template = "accounts/bettor/dashboard.html"
    context = {}

    return render(request, template, context)
