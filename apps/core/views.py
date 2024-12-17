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


##################################################
#                   ERROR PAGES                  #
##################################################


def error_400(request, exception):
    """Handle 400 Bad Request errors."""
    return render(request, "400.html", status=400)


def error_403(request, exception):
    """Handle 403 Forbidden errors."""
    return render(request, "403.html", status=403)


def error_405(request, exception):
    """Handle 405 Method Not Allowed errors."""
    return render(request, "405.html", status=405)


def error_404(request, exception):
    """Handle 404 Not Found errors."""
    return render(request, "404.html", status=404)


def error_500(request):
    """Handle 500 Internal Server Error errors."""
    return render(request, "500.html", status=500)
