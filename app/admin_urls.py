from django.urls import path
from . import admin_views

urlpatterns = [
    # ============================================================
    # AUTH & DASHBOARD
    # ============================================================
    path("login/", admin_views.custom_admin_login, name="custom_admin_login"),
    path("logout/", admin_views.custom_admin_logout, name="custom_admin_logout"),
    path("", admin_views.custom_admin_dashboard, name="custom_admin_dashboard"),

    # ============================================================
    # INVENTORY SPECIFIC ROUTES
    # ============================================================
    path("inventory/", admin_views.custom_admin_inventory, name="custom_admin_inventory"),
    path("inventory/stock-in/", admin_views.custom_admin_stock_in, name="custom_admin_stock_in"),
    path("inventory/stock-out/", admin_views.custom_admin_stock_out, name="custom_admin_stock_out"),
    path("inventory/stock-history/", admin_views.custom_admin_stock_history, name="custom_admin_stock_history"),
    path("inventory/api/designs/", admin_views.api_get_designs_by_category, name="admin_api_designs_by_category"),
    path(
        "newsletter-subscribers/api/status/",
        admin_views.api_newsletter_subscriber_status,
        name="admin_api_newsletter_subscriber_status",
    ),

    # ============================================================
    # DYNAMIC GENERIC MODEL CRUD ROUTES
    # ============================================================
    path("<str:model_name>/", admin_views.custom_admin_model_list, name="custom_admin_model_list"),
    path("<str:model_name>/add/", admin_views.custom_admin_add, name="custom_admin_add"),
    path("<str:model_name>/<int:pk>/edit/", admin_views.custom_admin_edit, name="custom_admin_edit"),
    path("<str:model_name>/<int:pk>/delete/", admin_views.custom_admin_delete, name="custom_admin_delete"),
]