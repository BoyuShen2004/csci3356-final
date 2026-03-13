from django import forms
from django.contrib.auth import get_user_model

from .models import Listing


class CompleteSignupForm(forms.Form):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
        label="Username",
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
        label="First name",
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
        label="Last name",
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
        label="Password",
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"}),
        label="Confirm password",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise forms.ValidationError("Please choose a username.")
        User = get_user_model()
        # Allow keeping the same username
        if User.objects.filter(username__iexact=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "title", "description", "address", "city", "state", "zip_code",
            "lat", "lng", "property_type", "bedrooms", "bathrooms", "sqft", "floor",
            "monthly_rent", "utilities_included", "estimated_utilities",
            "security_deposit", "broker_fee", "application_fee",
            "lease_type", "available_from", "available_to", "landlord_approval_required",
            "parking", "shared", "pets_allowed", "has_stairs", "furnished", "laundry",
            "amenities", "rules", "requirements", "images",
        ]
        widgets = {
            "available_from": forms.DateInput(attrs={"type": "date"}),
            "available_to": forms.DateInput(attrs={"type": "date"}),
        }
