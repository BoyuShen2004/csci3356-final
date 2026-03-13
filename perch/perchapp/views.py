"""Perch BC Housing views - matches bc-housing-demo-app workflow."""
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib import messages as dj_messages

from django.contrib.auth import get_user_model
from django.db.models import Avg

from .forms import CompleteSignupForm
from .models import Application, Favorite, Listing, Message, Profile, Report, Review


def _get_profile(user):
    try:
        return user.profile
    except Profile.DoesNotExist:
        return None


def _get_unread_count(user):
    return Message.objects.filter(receiver=user, read=False).count()


# ----- Public -----
def landing(request):
    return render(request, "perchapp/landing.html", {"user": request.user})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("perchapp:dashboard")
    error = ""
    # Surface Google OAuth errors (e.g. duplicate signup email) via ?message= query param
    if request.method == "GET":
        msg_code = request.GET.get("message")
        if msg_code == "email_already_used":
            error = "That BC email is already used. Please sign in with it or use a different email to sign up."
    if request.method == "POST":
        login_value = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not login_value or not password:
            error = "Please enter both email/username and password."
            return render(request, "perchapp/login.html", {"error": error})
        # Password login: look up user by username or email, then verify password directly.
        User = get_user_model()
        try:
            user = User.objects.get(Q(username__iexact=login_value) | Q(email__iexact=login_value))
        except User.DoesNotExist:
            user = None
        if user is not None and user.check_password(password):
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            profile_obj = Profile.objects.filter(user=user).first()
            if profile_obj and (profile_obj.role or "").strip().lower() == "admin":
                return redirect("perchapp:admin_dashboard")
            return redirect("perchapp:dashboard")
        error = "Invalid login. Please check your email/username and password."
    return render(request, "perchapp/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("perchapp:landing")


def signup_view(request):
    """Start signup: go to Google first, then complete profile/password."""
    if request.user.is_authenticated:
        return redirect("perchapp:dashboard")
    # Mark that we are in signup flow so pipeline can treat duplicate emails specially.
    request.session["signup_flow"] = True
    from django.urls import reverse
    next_url = reverse("perchapp:signup_complete")
    return redirect(f"{reverse('social:begin', args=['google-oauth2'])}?next={next_url}")


@login_required
def signup_complete(request):
    """Second step after Google: collect username, name, and password."""
    # Only allow immediately after a signup Google flow
    if not request.session.get("signup_flow", False):
        return redirect("perchapp:dashboard")
    user = request.user
    if request.method == "POST":
        form = CompleteSignupForm(user, request.POST)
        if form.is_valid():
            user.username = form.cleaned_data["username"]
            user.first_name = form.cleaned_data.get("first_name", "")
            user.last_name = form.cleaned_data.get("last_name", "")
            user.set_password(form.cleaned_data["password1"])
            user.save()
            # Ensure profile exists
            Profile.objects.get_or_create(user=user)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session.pop("signup_flow", None)
            return redirect("perchapp:dashboard")
    else:
        # Pre-fill from current user
        initial = {
            "username": user.username or (user.email.split("@", 1)[0] if user.email else ""),
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        form = CompleteSignupForm(user, initial=initial)
    return render(request, "perchapp/signup_complete.html", {"form": form, "user_email": user.email})


# ----- App (with sidebar) -----
@login_required
def dashboard(request):
    listings = Listing.objects.filter(status="available").order_by("-created_at")[:4]
    my_apps = Application.objects.filter(applicant=request.user, status="pending")
    my_favs = Favorite.objects.filter(user=request.user)
    unread = _get_unread_count(request.user)
    fav_ids = set(Favorite.objects.filter(user=request.user).values_list("listing_id", flat=True))
    listing_data = [{"listing": l, "is_favorite": l.pk in fav_ids} for l in listings]
    return render(request, "perchapp/dashboard.html", {
        "listing_data": listing_data,
        "available_count": Listing.objects.filter(status="available").count(),
        "pending_apps_count": my_apps.count(),
        "favorites_count": my_favs.count(),
        "unread_count": unread,
        "profile": _get_profile(request.user),
    })


@login_required
def search(request):
    qs = Listing.objects.filter(status="available")
    q = request.GET.get("search", "").strip()
    min_price = request.GET.get("minPrice", "").strip()
    max_price = request.GET.get("maxPrice", "").strip()
    bedrooms = request.GET.get("bedrooms", "").strip()
    property_type = request.GET.get("propertyType", "").strip()
    lease_type = request.GET.get("leaseType", "").strip()
    furnished = request.GET.get("furnished", "").strip()
    pets = request.GET.get("petsAllowed", "").strip()
    parking = request.GET.get("parking", "").strip()

    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(address__icontains=q) | Q(city__icontains=q) | Q(description__icontains=q)
        )
    if min_price:
        try:
            qs = qs.filter(monthly_rent__gte=int(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(monthly_rent__lte=int(max_price))
        except ValueError:
            pass
    if bedrooms:
        try:
            qs = qs.filter(bedrooms=int(bedrooms))
        except ValueError:
            pass
    if property_type:
        qs = qs.filter(property_type=property_type)
    if lease_type:
        qs = qs.filter(lease_type=lease_type)
    if furnished == "yes":
        qs = qs.filter(furnished=True)
    elif furnished == "no":
        qs = qs.filter(furnished=False)
    if pets == "yes":
        qs = qs.filter(pets_allowed=True)
    elif pets == "no":
        qs = qs.filter(pets_allowed=False)
    if parking == "yes":
        qs = qs.filter(parking=True)
    elif parking == "no":
        qs = qs.filter(parking=False)

    fav_ids = set()
    if request.user.is_authenticated:
        fav_ids = set(Favorite.objects.filter(user=request.user).values_list("listing_id", flat=True))
    listing_data = [{"listing": l, "is_favorite": l.pk in fav_ids} for l in qs]
    return render(request, "perchapp/search.html", {
        "listings": qs,
        "listing_data": listing_data,
        "filters": {
            "search": q,
            "minPrice": min_price,
            "maxPrice": max_price,
            "bedrooms": bedrooms,
            "propertyType": property_type,
            "leaseType": lease_type,
            "furnished": furnished,
            "petsAllowed": pets,
            "parking": parking,
        },
        "profile": _get_profile(request.user) if request.user.is_authenticated else None,
    })


@login_required
def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    listing.views += 1
    listing.save(update_fields=["views"])
    owner_profile = _get_profile(listing.owner)
    is_fav = False
    has_applied = False
    is_owner = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, listing=listing).exists()
        has_applied = Application.objects.filter(applicant=request.user, listing=listing).exists()
        is_owner = listing.owner_id == request.user.id
    owner_reviews = Review.objects.filter(reviewed_user=listing.owner)
    total_upfront = (
        listing.monthly_rent + listing.security_deposit + listing.broker_fee + listing.application_fee
        + (0 if listing.utilities_included else listing.estimated_utilities)
    )
    return render(request, "perchapp/listing_detail.html", {
        "listing": listing,
        "owner_profile": owner_profile,
        "is_favorite": is_fav,
        "has_applied": has_applied,
        "is_owner": is_owner,
        "owner_reviews": owner_reviews,
        "total_upfront": total_upfront,
        "profile": _get_profile(request.user) if request.user.is_authenticated else None,
    })


@login_required
def toggle_favorite(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
    if not created:
        fav.delete()
    next_url = request.GET.get("next") or reverse("perchapp:listing_detail", args=[pk])
    return redirect(next_url)


@login_required
def create_listing(request, pk=None):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user) if pk else None
    if request.method == "POST":
        from datetime import datetime
        try:
            data = request.POST
            obj = listing or Listing(owner=request.user)
            obj.title = data.get("title", "")
            obj.description = data.get("description", "")
            obj.address = data.get("address", "")
            obj.city = data.get("city", "Brighton")
            obj.state = data.get("state", "MA")
            obj.zip_code = data.get("zip_code", "02135")
            obj.lat = float(data.get("lat", 42.3382))
            obj.lng = float(data.get("lng", -71.1530))
            obj.property_type = data.get("property_type", "Apartment")
            obj.bedrooms = int(data.get("bedrooms", 1))
            obj.bathrooms = int(data.get("bathrooms", 1))
            obj.sqft = int(data.get("sqft") or 0)
            obj.floor = int(data.get("floor") or 1)
            obj.monthly_rent = int(data.get("monthly_rent", 0))
            obj.utilities_included = data.get("utilities_included") == "on"
            obj.estimated_utilities = int(data.get("estimated_utilities") or 0)
            obj.security_deposit = int(data.get("security_deposit") or 0)
            obj.broker_fee = int(data.get("broker_fee") or 0)
            obj.application_fee = int(data.get("application_fee") or 0)
            obj.lease_type = data.get("lease_type", "Sublease")
            obj.available_from = datetime.strptime(data.get("available_from", "2026-06-01"), "%Y-%m-%d").date()
            obj.available_to = datetime.strptime(data.get("available_to", "2026-08-31"), "%Y-%m-%d").date()
            obj.landlord_approval_required = data.get("landlord_approval_required") == "on"
            obj.parking = data.get("parking") == "on"
            obj.shared = data.get("shared") == "on"
            obj.pets_allowed = data.get("pets_allowed") == "on"
            obj.has_stairs = data.get("has_stairs") != "0"
            obj.furnished = data.get("furnished") == "on"
            obj.laundry = data.get("laundry", "In-Building")
            obj.amenities = data.get("amenities", "")
            obj.rules = data.get("rules", "")
            obj.requirements = data.get("requirements", "")
            obj.images = data.get("images", '["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800"]')
            obj.status = listing.status if listing else "available"
            obj.save()
            return redirect("perchapp:my_listings")
        except Exception as e:
            pass  # Fall through to re-render with errors
    form_data = {}
    if listing:
        form_data = {
            "title": listing.title, "description": listing.description, "address": listing.address,
            "city": listing.city, "state": listing.state, "zip_code": listing.zip_code,
            "property_type": listing.property_type, "bedrooms": listing.bedrooms, "bathrooms": listing.bathrooms,
            "sqft": listing.sqft, "floor": listing.floor, "monthly_rent": listing.monthly_rent,
            "utilities_included": listing.utilities_included, "estimated_utilities": listing.estimated_utilities,
            "security_deposit": listing.security_deposit, "lease_type": listing.lease_type,
            "available_from": listing.available_from, "available_to": listing.available_to,
            "parking": listing.parking, "furnished": listing.furnished, "pets_allowed": listing.pets_allowed,
            "amenities": listing.amenities, "rules": listing.rules,
        }
    return render(request, "perchapp/create_listing.html", {
        "form": form_data,
        "listing": listing,
        "profile": _get_profile(request.user),
    })


@login_required
def apply(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if listing.owner_id == request.user.id:
        return redirect("perchapp:listing_detail", pk=pk)
    if request.method == "POST":
        msg = request.POST.get("message", "").strip()
        from_date = request.POST.get("requestedFrom") or request.POST.get("requested_from")
        to_date = request.POST.get("requestedTo") or request.POST.get("requested_to")
        if msg and from_date and to_date:
            Application.objects.create(
                listing=listing,
                applicant=request.user,
                message=msg,
                requested_from=from_date,
                requested_to=to_date,
                status="pending",
            )
            return redirect("perchapp:applications")
    return render(request, "perchapp/apply.html", {
        "listing": listing,
        "owner_profile": _get_profile(listing.owner),
        "profile": _get_profile(request.user),
    })


@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user).order_by("-created_at")
    status_filter = request.GET.get("status", "all")
    if status_filter != "all":
        listings = listings.filter(status=status_filter)
    counts = {
        "all": Listing.objects.filter(owner=request.user).count(),
        "available": Listing.objects.filter(owner=request.user, status="available").count(),
        "pending": Listing.objects.filter(owner=request.user, status="pending").count(),
        "rented": Listing.objects.filter(owner=request.user, status="rented").count(),
    }
    return render(request, "perchapp/my_listings.html", {
        "listings": listings,
        "status_filter": status_filter,
        "counts": counts,
        "profile": _get_profile(request.user),
    })


@login_required
def applications(request):
    my_apps = Application.objects.filter(applicant=request.user).select_related("listing", "listing__owner")
    received_apps = Application.objects.filter(listing__owner=request.user).select_related("applicant", "listing")
    tab = request.GET.get("tab", "submitted")
    received_data = []
    for app in received_apps:
        try:
            prof = app.applicant.profile
        except Exception:
            prof = None
        received_data.append({"app": app, "applicant_profile": prof})
    return render(request, "perchapp/applications.html", {
        "my_applications": my_apps,
        "received_data": received_data,
        "tab": tab,
        "profile": _get_profile(request.user),
    })


@login_required
def favorites(request):
    fav_ids = Favorite.objects.filter(user=request.user).values_list("listing_id", flat=True)
    listings = Listing.objects.filter(pk__in=fav_ids, status="available")
    return render(request, "perchapp/favorites.html", {
        "listings": listings,
        "profile": _get_profile(request.user),
    })


@login_required
def messages(request):
    # Get conversations: users we've messaged or been messaged by
    sent = Message.objects.filter(sender=request.user).values_list("receiver_id", flat=True).distinct()
    received = Message.objects.filter(receiver=request.user).values_list("sender_id", flat=True).distinct()
    other_ids = set(sent) | set(received)
    conversations = []
    for uid in other_ids:
        msgs = Message.objects.filter(
            Q(sender=request.user, receiver_id=uid) | Q(sender_id=uid, receiver=request.user)
        ).order_by("timestamp")
        last = msgs.last()
        unread = msgs.filter(receiver=request.user, read=False).count()
        other = get_user_model().objects.get(pk=uid)
        try:
            other_prof = other.profile
        except Profile.DoesNotExist:
            other_prof = None
        conversations.append({
            "other_user": other,
            "other_profile": other_prof,
            "last_message": last,
            "unread_count": unread,
            "messages": list(msgs),
            "listing": msgs.first().listing if msgs.exists() else None,
        })
    conversations.sort(key=lambda c: c["last_message"].timestamp if c["last_message"] else timezone.min, reverse=True)
    selected_id = request.GET.get("with")
    selected = next((c for c in conversations if str(c["other_user"].id) == selected_id), conversations[0] if conversations else None)
    if request.method == "POST" and selected:
        content = request.POST.get("content", "").strip()
        listing = selected.get("listing") or Listing.objects.first()
        if content and listing:
            Message.objects.create(
                sender=request.user,
                receiver=selected["other_user"],
                listing=listing,
                content=content,
            )
            return redirect(reverse("perchapp:messages") + "?with=" + str(selected["other_user"].id))
    return render(request, "perchapp/messages.html", {
        "conversations": conversations,
        "selected": selected,
        "unread_count": _get_unread_count(request.user),
        "profile": _get_profile(request.user),
    })


@login_required
def profile(request):
    prof = _get_profile(request.user)
    can_edit = request.method == "POST" or request.GET.get("edit") == "1"
    if request.method == "POST":
        u = request.user
        u.first_name = (request.POST.get("first_name") or "").strip()
        u.last_name = (request.POST.get("last_name") or "").strip()
        u.save()
        if prof is not None:
            prof.phone = (request.POST.get("phone") or "").strip()
            prof.year = (request.POST.get("year") or "").strip()
            prof.major = (request.POST.get("major") or "").strip()
            prof.bio = (request.POST.get("bio") or "").strip()
            prof.save()
        dj_messages.success(request, "Profile updated.")
        return redirect("perchapp:profile")
    user_reviews = Review.objects.filter(reviewed_user=request.user)
    user_listings = Listing.objects.filter(owner=request.user)
    return render(request, "perchapp/profile.html", {
        "user_reviews": user_reviews,
        "user_listings": user_listings,
        "profile": prof,
        "can_edit": can_edit,
    })


@login_required
def update_application_status(request, pk, status):
    app = get_object_or_404(Application, pk=pk)
    if app.listing.owner_id != request.user.id:
        return redirect("perchapp:applications")
    if status in ("accepted", "declined"):
        app.status = status
        app.save()
    return redirect("perchapp:applications?tab=received")


@login_required
def admin_dashboard(request):
    """Admin Dashboard - only for users with profile.role == 'admin'."""
    profile_obj = _get_profile(request.user)
    if not profile_obj or profile_obj.role != "admin":
        return render(request, "perchapp/admin_denied.html", {"profile": profile_obj})

    listings = Listing.objects.all()
    applications_qs = Application.objects.all()
    reports = Report.objects.filter(status="pending").select_related("reporter", "target_listing", "target_user")
    User = get_user_model()
    admin_profiles = Profile.objects.filter(role="admin").values_list("user_id", flat=True)
    users_with_profiles = Profile.objects.exclude(role="admin").select_related("user")

    total_listings = listings.count()
    available = listings.filter(status="available").count()
    pending_listings = listings.filter(status="pending").count()
    rented = listings.filter(status="rented").count()
    total_users = users_with_profiles.count()
    verified_users = users_with_profiles.filter(verified=True).count()
    total_apps = applications_qs.count()
    pending_apps = applications_qs.filter(status="pending").count()
    accepted_apps = applications_qs.filter(status="accepted").count()
    declined_apps = applications_qs.filter(status="declined").count()
    avg_rent = listings.aggregate(avg=Avg("monthly_rent"))["avg"] or 0
    pending_reports = reports.count()
    verified_listings = listings.filter(verified=True).count()
    acceptance_rate = round((accepted_apps / total_apps * 100)) if total_apps else 0

    return render(request, "perchapp/admin_dashboard.html", {
        "stats": {
            "total_listings": total_listings,
            "available": available,
            "pending": pending_listings,
            "rented": rented,
            "total_users": total_users,
            "verified_users": verified_users,
            "total_applications": total_apps,
            "pending_apps": pending_apps,
            "accepted_apps": accepted_apps,
            "declined_apps": declined_apps,
            "avg_rent": int(round(avg_rent)),
            "pending_reports": pending_reports,
            "verified_listings": verified_listings,
            "acceptance_rate": acceptance_rate,
        },
        "pending_reports_list": reports,
        "users_with_profiles": users_with_profiles,
        "profile": profile_obj,
    })


@login_required
def report_resolve(request, pk, status):
    """Resolve or dismiss a report (admin only)."""
    profile_obj = _get_profile(request.user)
    if not profile_obj or profile_obj.role != "admin":
        return redirect("perchapp:dashboard")
    report = get_object_or_404(Report, pk=pk)
    if status in ("resolved", "dismissed"):
        report.status = status
        report.save()
    return redirect("perchapp:admin_dashboard")


def auth_error(request):
    """Display a friendly message when Google login fails (e.g. reused email or state issue)."""
    return render(request, 'perchapp/auth_error.html')
