"""Keep admin state in sync: User.is_staff and Profile.role == 'admin'.

Whenever an admin is created or promoted (Django admin, load_mock_data, shell, etc.),
the other side is updated so the in-app Admin Dashboard always appears for that user.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Profile


@receiver(post_save, sender=get_user_model())
def ensure_admin_profile_synced(sender, instance, created, **kwargs):
    """If User.is_staff is True, ensure Profile exists with role='admin'."""
    if not instance.is_staff:
        return
    profile, _ = Profile.objects.get_or_create(
        user=instance,
        defaults={"role": "admin"},
    )
    if profile.role != "admin":
        profile.role = "admin"
        profile.save(update_fields=["role"])


@receiver(post_save, sender=Profile)
def ensure_admin_user_staff(sender, instance, created, **kwargs):
    """If Profile.role is 'admin', ensure User.is_staff is True."""
    if (instance.role or "").strip().lower() != "admin":
        return
    user = instance.user
    if not user.is_staff:
        user.is_staff = True
        user.save(update_fields=["is_staff"])
