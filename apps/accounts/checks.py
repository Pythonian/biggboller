from django.core.checks import Tags, Warning, register

# To check for missing settings in a project


@register(Tags.compatibility)
def settings_check(app_configs, **kwargs):
    from django.conf import settings

    errors = []
    if not settings.ADMINS:
        errors.append(
            Warning(
                """The system admins are not set in the project settings""",
                hint="""In order to receive notifications about account activities, define system admins like ADMINS=(("Admin", "admin@example.com"),) in your settings""",
                id="account.W001",
            )
        )
    return errors
