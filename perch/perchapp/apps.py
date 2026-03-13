from django.apps import AppConfig


class PerchappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "perchapp"
    verbose_name = "Perch Housing"

    def ready(self):
        import perchapp.signals  # noqa: F401 - keep admin Profile.role and User.is_staff in sync

