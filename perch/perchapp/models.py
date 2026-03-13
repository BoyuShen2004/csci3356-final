"""Perch BC Housing models - matches bc-housing-demo-app schema."""
from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extended user profile for BC students."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    year = models.CharField(max_length=20, blank=True)
    major = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    profile_image = models.URLField(blank=True, default="https://i.pravatar.cc/150?img=1")
    verified = models.BooleanField(default=True)
    role = models.CharField(max_length=20, default="student")  # student, admin

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Listing(models.Model):
    """Housing listing - matches mockData listing schema."""
    STATUS_CHOICES = [
        ("available", "Available"),
        ("pending", "Pending"),
        ("rented", "Rented"),
    ]
    PROPERTY_TYPES = ["Apartment", "House", "Studio", "Room"]
    LEASE_TYPES = ["Sublease", "Short-term", "Full Lease"]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=10, default="MA")
    zip_code = models.CharField(max_length=10)
    lat = models.FloatField(default=42.3382)
    lng = models.FloatField(default=-71.1530)

    property_type = models.CharField(max_length=50, default="Apartment")
    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    sqft = models.PositiveIntegerField(default=0)
    floor = models.PositiveSmallIntegerField(default=1)

    monthly_rent = models.PositiveIntegerField()
    utilities_included = models.BooleanField(default=False)
    estimated_utilities = models.PositiveIntegerField(default=0)
    security_deposit = models.PositiveIntegerField(default=0)
    broker_fee = models.PositiveIntegerField(default=0)
    application_fee = models.PositiveIntegerField(default=0)

    lease_type = models.CharField(max_length=50, default="Sublease")
    available_from = models.DateField()
    available_to = models.DateField()
    landlord_approval_required = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    parking = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    has_stairs = models.BooleanField(default=True)
    furnished = models.BooleanField(default=False)
    laundry = models.CharField(max_length=50, default="In-Building")
    amenities = models.TextField(blank=True)  # JSON or comma-separated
    rules = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    images = models.TextField(blank=True)  # JSON array of URLs
    verified = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def amenities_list(self):
        if not self.amenities:
            return []
        return [a.strip() for a in self.amenities.split(",") if a.strip()]

    @property
    def rules_list(self):
        if not self.rules:
            return []
        return [r.strip() for r in self.rules.split(",") if r.strip()]

    @property
    def requirements_list(self):
        if not self.requirements:
            return []
        return [r.strip() for r in self.requirements.split(",") if r.strip()]

    @property
    def owner_image(self):
        try:
            return self.owner.profile.profile_image or "https://i.pravatar.cc/150?img=1"
        except Exception:
            return "https://i.pravatar.cc/150?img=1"

    @property
    def images_list(self):
        if not self.images:
            return ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800"]
        import json
        try:
            return json.loads(self.images)
        except Exception:
            return [u.strip() for u in self.images.split(",") if u.strip()] or [
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800"
            ]


class Application(models.Model):
    """Application for a listing."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("withdrawn", "Withdrawn"),
    ]
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    message = models.TextField()
    requested_from = models.DateField()
    requested_to = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateField(auto_now_add=True)


class Favorite(models.Model):
    """User's favorited listing."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="favorited_by")


class Message(models.Model):
    """Direct message between users about a listing."""
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages"
    )
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


class Review(models.Model):
    """Review of a user (lister/subletter)."""
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_given"
    )
    reviewed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_received"
    )
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateField(auto_now_add=True)


class Report(models.Model):
    """User or listing report for admin moderation."""
    TYPE_CHOICES = [("listing", "Listing"), ("user", "User")]
    STATUS_CHOICES = [("pending", "Pending"), ("resolved", "Resolved"), ("dismissed", "Dismissed")]
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_submitted"
    )
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    target_listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, null=True, blank=True, related_name="reports"
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="reports_against"
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateField(auto_now_add=True)
