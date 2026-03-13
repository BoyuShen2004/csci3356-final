from django.urls import path
from . import views

app_name = "perchapp"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("signup/complete/", views.signup_complete, name="signup_complete"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("search/", views.search, name="search"),
    path("listings/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("listings/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("listings/create/", views.create_listing, name="create_listing"),
    path("listings/edit/<int:pk>/", views.create_listing, name="edit_listing"),
    path("listings/<int:pk>/apply/", views.apply, name="apply"),
    path("my-listings/", views.my_listings, name="my_listings"),
    path("applications/", views.applications, name="applications"),
    path("applications/<int:pk>/<str:status>/", views.update_application_status, name="update_application_status"),
    path("favorites/", views.favorites, name="favorites"),
    path("messages/", views.messages, name="messages"),
    path("profile/", views.profile, name="profile"),
    path("app-admin/", views.admin_dashboard, name="admin_dashboard"),
    path("app-admin/reports/<int:pk>/<str:status>/", views.report_resolve, name="report_resolve"),
]
