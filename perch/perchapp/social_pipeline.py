"""Custom social-auth pipeline steps for Perch Google OAuth."""

from social_core.exceptions import AuthForbidden
from django.conf import settings

from .models import Profile


def require_bc_email(backend, details, **kwargs):
    """Reject non @bc.edu Google accounts."""
    email = (details.get("email") or "").lower()
    if not email.endswith("@bc.edu"):
        raise AuthForbidden(backend, "You must use a @bc.edu email to log in.")




def prevent_duplicate_signup(backend, details, request=None, **kwargs):
    """During signup, block creating a second account for the same email."""
    if request is None:
        return
    # Only care about explicit signup flow (we set this in signup_view).
    if not request.session.get('signup_flow'):
        return

    # Also confirm that the redirect target is the signup complete page, not dashboard/login.
    next_url = backend.strategy.session_get('next') or ''
    if 'signup/complete' not in str(next_url):
        return

    email = (details.get('email') or '').lower()
    if not email:
        return
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if User.objects.filter(email__iexact=email).exists():
        # Clear signup flag and redirect back to login with an explicit error message.
        request.session.pop('signup_flow', None)
        return backend.strategy.redirect('/login/?message=email_already_used')

def ensure_profile_and_role(backend, user, request=None, **kwargs):
    """Make sure the user has a Profile and mark the configured admin email."""
    if not user:
        return
    profile, _ = Profile.objects.get_or_create(user=user)

    admin_email = (getattr(settings, "PERCH_ADMIN_EMAIL", "") or "").lower()
    if user.email.lower() == admin_email:
        profile.role = "admin"
        profile.save(update_fields=["role"])

