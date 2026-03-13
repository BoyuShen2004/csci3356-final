"""Load mock data from bc-housing-demo-app schema."""
import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings
from perchapp.models import Profile, Listing, Application, Favorite, Message, Report, Review


# Exact user templates from bc-housing-demo-app mockUsers; all are created as real DB users (login with demo123123).
DEMO_PASSWORD = "demo123123"

MOCK_USERS = [
    # id 1 – Sarah Chen
    {"first_name": "Sarah", "last_name": "Chen", "email": "chen.sarah@bc.edu", "year": "Junior", "major": "Computer Science",
     "bio": "Junior CS major looking for summer subletters for my Comm Ave apartment. Clean, quiet, and pet-friendly!",
     "phone": "(617) 555-0101", "img": "1", "role": "student"},
    # id 2 – James Murphy
    {"first_name": "James", "last_name": "Murphy", "email": "murphy.james@bc.edu", "year": "Senior", "major": "Finance",
     "bio": "Senior finance student graduating in May. Great apartment available for summer sublet near Cleveland Circle.",
     "phone": "(617) 555-0102", "img": "3", "role": "student"},
    # id 3 – Maria Santos
    {"first_name": "Maria", "last_name": "Santos", "email": "santos.maria@bc.edu", "year": "Sophomore", "major": "Biology",
     "bio": "Looking for affordable summer housing near BC campus. Non-smoker, clean, and studious.",
     "phone": "(617) 555-0103", "img": "5", "role": "student"},
    # id 4 – Alex Kim
    {"first_name": "Alex", "last_name": "Kim", "email": "kim.alex@bc.edu", "year": "Graduate", "major": "MBA",
     "bio": "MBA candidate with a great apartment in Brighton. Looking for responsible summer subletters.",
     "phone": "(617) 555-0104", "img": "8", "role": "student"},
    # id 5 – Emily O'Brien
    {"first_name": "Emily", "last_name": "O'Brien", "email": "obrien.emily@bc.edu", "year": "Junior", "major": "Nursing",
     "bio": "Nursing student looking for a quiet place for the summer while I do clinicals at BC.",
     "phone": "(617) 555-0105", "img": "9", "role": "student"},
    # id 6 – Admin (demo app: admin@bc.edu)
    {"first_name": "Admin", "last_name": "User", "email": "admin@bc.edu", "year": "", "major": "",
     "bio": "Platform administrator", "phone": "", "img": "12", "role": "admin"},
]


def load_listings(users):
    listings_data = [
        {"owner_idx": 0, "title": "Sunny 2BR on Comm Ave - Perfect for Summer", "address": "1945 Commonwealth Ave",
         "city": "Brighton", "zip": "02135", "lat": 42.3398, "lng": -71.1528, "property_type": "Apartment",
         "bedrooms": 2, "bathrooms": 1, "sqft": 850, "monthly_rent": 2200, "utilities_included": False,
         "est_util": 150, "deposit": 2200, "broker": 0, "app_fee": 0, "lease_type": "Sublease",
         "from": "2026-05-15", "to": "2026-08-31", "landlord_ok": True, "status": "available",
         "parking": True, "shared": False, "pets": True, "stairs": True, "floor": 3, "furnished": True,
         "laundry": "In-Unit", "amenities": "Hardwood Floors,Natural Light,Kitchen,Laundry,Near T Stop",
         "rules": "No Smoking,No Parties,Quiet Hours 10pm-8am", "reqs": "Non-smoker,BC Student",
         "imgs": '["https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800","https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800"]',
         "verified": True, "views": 234, "desc": "Spacious 2-bedroom apartment on Commonwealth Avenue..."},
        {"owner_idx": 1, "title": "Cozy Studio near Cleveland Circle", "address": "52 Chestnut Hill Ave",
         "city": "Brighton", "zip": "02135", "lat": 42.3365, "lng": -71.1495, "property_type": "Studio",
         "bedrooms": 0, "bathrooms": 1, "sqft": 450, "monthly_rent": 1600, "utilities_included": True,
         "est_util": 0, "deposit": 1600, "broker": 0, "app_fee": 25, "lease_type": "Sublease",
         "from": "2026-06-01", "to": "2026-08-15", "landlord_ok": False, "status": "available",
         "parking": False, "shared": False, "pets": False, "stairs": True, "floor": 2, "furnished": True,
         "laundry": "In-Building", "amenities": "Renovated,Granite Counters,Near T Stop,Heat Included",
         "rules": "No Smoking,No Pets", "reqs": "Non-smoker,BC Student,Quiet",
         "imgs": '["https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800"]',
         "verified": True, "views": 187, "desc": "Charming studio apartment steps from Cleveland Circle..."},
        {"owner_idx": 3, "title": "Large 3BR House - Great for Group", "address": "78 Foster St",
         "city": "Brighton", "zip": "02135", "lat": 42.3490, "lng": -71.1580, "property_type": "House",
         "bedrooms": 3, "bathrooms": 2, "sqft": 1400, "monthly_rent": 3600, "utilities_included": False,
         "est_util": 250, "deposit": 3600, "broker": 0, "app_fee": 0, "lease_type": "Sublease",
         "from": "2026-05-20", "to": "2026-08-31", "landlord_ok": True, "status": "available",
         "parking": True, "shared": False, "pets": True, "stairs": False, "floor": 1, "furnished": False,
         "laundry": "In-Unit", "amenities": "Backyard,Driveway Parking,Updated Kitchen,Near Shuttle",
         "rules": "No Smoking Indoors,Lawn Maintenance Required", "reqs": "BC Students Only",
         "imgs": '["https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800"]',
         "verified": True, "views": 312, "desc": "Beautiful 3-bedroom house in Brighton with a backyard..."},
        {"owner_idx": 0, "title": "Private Room in 4BR - South Street", "address": "210 South St",
         "city": "Brighton", "zip": "02135", "lat": 42.3360, "lng": -71.1630, "property_type": "Room",
         "bedrooms": 1, "bathrooms": 1, "sqft": 180, "monthly_rent": 950, "utilities_included": True,
         "est_util": 0, "deposit": 950, "broker": 0, "app_fee": 0, "lease_type": "Sublease",
         "from": "2026-06-01", "to": "2026-08-01", "landlord_ok": False, "status": "available",
         "parking": False, "shared": True, "pets": False, "stairs": True, "floor": 2, "furnished": True,
         "laundry": "In-Building", "amenities": "Furnished,Utilities Included,Shared Kitchen,Near Bus",
         "rules": "No Smoking,Shared Space Respect", "reqs": "BC Student,Non-smoker",
         "imgs": '["https://images.unsplash.com/photo-1540518614846-7eded433c457?w=800"]',
         "verified": False, "views": 145, "desc": "One private bedroom available in a shared 4-bedroom..."},
        {"owner_idx": 3, "title": "Modern 1BR - Lake Street", "address": "15 Lake St",
         "city": "Brighton", "zip": "02135", "lat": 42.3410, "lng": -71.1555, "property_type": "Apartment",
         "bedrooms": 1, "bathrooms": 1, "sqft": 650, "monthly_rent": 1900, "utilities_included": False,
         "est_util": 120, "deposit": 1900, "broker": 0, "app_fee": 50, "lease_type": "Short-term",
         "from": "2026-06-01", "to": "2026-07-31", "landlord_ok": False, "status": "available",
         "parking": False, "shared": False, "pets": False, "stairs": False, "floor": 1, "furnished": True,
         "laundry": "In-Unit", "amenities": "Modern Build,Quartz Counters,Elevator,Near T Stop",
         "rules": "No Smoking,No Pets", "reqs": "BC Student",
         "imgs": '["https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800"]',
         "verified": True, "views": 198, "desc": "Sleek, modern 1-bedroom apartment on Lake Street..."},
    ]
    listings = []
    for d in listings_data:
        owner = users[d["owner_idx"]]
        l = Listing.objects.create(
            owner=owner,
            title=d["title"],
            description=d["desc"],
            address=d["address"],
            city=d["city"],
            state="MA",
            zip_code=d["zip"],
            lat=d["lat"],
            lng=d["lng"],
            property_type=d["property_type"],
            bedrooms=d["bedrooms"],
            bathrooms=d["bathrooms"],
            sqft=d["sqft"],
            floor=d["floor"],
            monthly_rent=d["monthly_rent"],
            utilities_included=d["utilities_included"],
            estimated_utilities=d["est_util"],
            security_deposit=d["deposit"],
            broker_fee=d["broker"],
            application_fee=d["app_fee"],
            lease_type=d["lease_type"],
            available_from=d["from"],
            available_to=d["to"],
            landlord_approval_required=d["landlord_ok"],
            status=d["status"],
            parking=d["parking"],
            shared=d["shared"],
            pets_allowed=d["pets"],
            has_stairs=d["stairs"],
            furnished=d["furnished"],
            laundry=d["laundry"],
            amenities=d["amenities"],
            rules=d["rules"],
            requirements=d["reqs"],
            images=d["imgs"],
            verified=d["verified"],
            views=d["views"],
        )
        listings.append(l)
    return listings


class Command(BaseCommand):
    help = "Load mock BC housing data"

    def handle(self, *args, **options):
        # Use configured admin email or fall back to demo app default
        admin_email = (getattr(settings, "PERCH_ADMIN_EMAIL", None) or "").strip() or "admin@bc.edu"
        q = Q(email__endswith="@bc.edu") | Q(email=admin_email)
        User.objects.filter(q).delete()
        Profile.objects.all().delete()
        Listing.objects.all().delete()
        Application.objects.all().delete()
        Favorite.objects.all().delete()
        Message.objects.all().delete()
        Review.objects.all().delete()
        Report.objects.all().delete()

        users = []
        for i, u in enumerate(MOCK_USERS):
            # Admin: use configured email so it’s overridable; otherwise demo’s admin@bc.edu
            if u["role"] == "admin":
                email, username = admin_email, "admin"
            else:
                email = u["email"]
                username = email
            user = User.objects.create_user(
                username=username,
                email=email,
                password=DEMO_PASSWORD,
                first_name=u["first_name"],
                last_name=u["last_name"],
            )
            # Create Profile before setting is_staff, so the admin sync signal doesn’t create a duplicate profile
            Profile.objects.create(
                user=user,
                year=u.get("year") or "",
                major=u.get("major") or "",
                bio=u.get("bio") or "",
                phone=u.get("phone") or "",
                profile_image=f"https://i.pravatar.cc/150?img={u['img']}",
                verified=True,
                role=u["role"],
            )
            if u["role"] == "admin":
                user.is_staff = True
                user.is_superuser = True
                user.save()
            users.append(user)

        listings = load_listings(users)

        # Applications
        Application.objects.create(
            listing=listings[0], applicant=users[2],
            message="Hi Sarah! I'm a sophomore biology major looking for summer housing...",
            requested_from="2026-05-15", requested_to="2026-08-31", status="pending",
        )
        Application.objects.create(
            listing=listings[0], applicant=users[4],
            message="Hello! I'm a nursing student staying at BC for summer clinicals...",
            requested_from="2026-05-15", requested_to="2026-07-31", status="pending",
        )

        # Favorites
        Favorite.objects.create(user=users[2], listing=listings[0])
        Favorite.objects.create(user=users[2], listing=listings[1])
        Favorite.objects.create(user=users[4], listing=listings[0])

        # Messages
        from django.utils import timezone
        Message.objects.create(sender=users[2], receiver=users[0], listing=listings[0], content="Hi Sarah! I submitted an application for your Comm Ave apartment. Would you be available to chat this week?")
        Message.objects.create(sender=users[0], receiver=users[2], listing=listings[0], content="Hi Maria! Thanks for your interest. I'd love to chat. Are you free Thursday afternoon?", read=True)

        # Reports (for admin dashboard)
        Report.objects.create(reporter=users[2], report_type="listing", target_listing=listings[3], reason="Listing photos look outdated and may not reflect current condition.", status="pending")
        Report.objects.create(reporter=users[4], report_type="user", target_user=users[1], reason="User did not respond to messages after accepting application.", status="pending")

        self.stdout.write(self.style.SUCCESS(
            "Demo users (from bc-housing-demo-app template) saved to DB. Password for all: demo123123"
        ))
        self.stdout.write(self.style.SUCCESS(
            "Log in with: chen.sarah@bc.edu, murphy.james@bc.edu, santos.maria@bc.edu, "
            "kim.alex@bc.edu, obrien.emily@bc.edu, or " + admin_email + " (admin)"
        ))
