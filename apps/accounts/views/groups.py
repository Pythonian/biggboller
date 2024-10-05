from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from apps.accounts.models import Group
from apps.accounts.forms import GroupCreateForm, GroupUpdateForm
from django.http import JsonResponse
from django.template.loader import render_to_string


def is_admin(user):
    """
    Check if the user has admin privileges.
    Adjust this function based on your authentication setup.
    """
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def list_group(request):
    """View to list all betting groups."""

    groups = Group.objects.all()
    create_form = GroupCreateForm()

    template = "accounts/administrator/groups/list_group.html"
    context = {
        "groups": groups,
        "create_form": create_form,
        "title": "Manage Groups",
    }

    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def create_group_ajax(request):
    """
    Handle AJAX request to create a new group.
    Returns JSON response with success status and updated table row.
    """
    if request.method == "POST" and request.is_ajax():
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.status = Group.Status.RUNNING
            group.save()
            messages.success(
                request, f'Group "{group.name}" has been created successfully.'
            )
            # Render the new row
            html = render_to_string(
                "accounts/administrator/groups/partials/_group_row.html",
                {"group": group},
                request=request,
            )
            return JsonResponse({"success": True, "html": html})
        else:
            # Return form errors
            html = render_to_string(
                "accounts/administrator/groups/partials/_create_group_form.html",
                {"form": form},
                request=request,
            )
            return JsonResponse({"success": False, "html": html})
    return JsonResponse({"success": False, "error": "Invalid request."})


@login_required
@user_passes_test(is_admin)
def view_group_ajax(request, group_id):
    """
    Handle AJAX request to view group details.
    Returns JSON response with rendered HTML for the modal.
    """
    group = get_object_or_404(Group, id=group_id)
    html = render_to_string(
        "accounts/administrator/groups/partials/_view_group_modal.html",
        {"group": group},
        request=request,
    )
    return JsonResponse({"success": True, "html": html})


@login_required
@user_passes_test(is_admin)
def update_group_ajax(request, group_id):
    """
    Handle AJAX request to update a group.
    Returns JSON response with success status and updated table row.
    """
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST" and request.is_ajax():
        form = GroupUpdateForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Group "{group.name}" has been updated successfully.'
            )
            # Render the updated row
            html = render_to_string(
                "accounts/administrator/groups/partials/_group_row.html",
                {"group": group},
                request=request,
            )
            return JsonResponse({"success": True, "html": html})
        else:
            # Return form errors
            html = render_to_string(
                "accounts/administrator/groups/partials/_edit_group_form.html",
                {"form": form, "group": group},
                request=request,
            )
            return JsonResponse({"success": False, "html": html})
    return JsonResponse({"success": False, "error": "Invalid request."})


@login_required
@user_passes_test(is_admin)
def close_group_ajax(request, group_id):
    """
    Handle AJAX request to close a group.
    Returns JSON response with success status and updated table row.
    """
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST" and request.is_ajax():
        group.status = Group.Status.CLOSED
        group.save()
        messages.success(request, f'Group "{group.name}" has been closed successfully.')
        # Render the updated row
        html = render_to_string(
            "accounts/administrator/groups/partials/_group_row.html",
            {"group": group},
            request=request,
        )
        return JsonResponse({"success": True, "html": html})
    return JsonResponse({"success": False, "error": "Invalid request."})
