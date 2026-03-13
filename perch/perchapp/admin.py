from django.contrib import admin
from .models import Profile, Listing, Application, Favorite, Message, Review, Report


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "year", "major", "role", "verified")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "city", "monthly_rent", "status", "property_type")
    list_filter = ("status", "property_type", "city")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("listing", "applicant", "status", "created_at")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "listing")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "listing", "timestamp")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("reviewer", "reviewed_user", "rating", "created_at")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "report_type", "status", "created_at")
