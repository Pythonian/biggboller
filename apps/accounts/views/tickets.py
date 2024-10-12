from django.shortcuts import render, get_object_or_404, redirect

# from django.contrib.auth.decorators import login_required, user_passes_test
from apps.accounts.models import Ticket
from apps.core.utils import mk_paginator
from django.contrib import messages

PAGINATION_COUNT = 10


def is_admin(user):
    return user.is_staff


# @user_passes_test(is_admin)
