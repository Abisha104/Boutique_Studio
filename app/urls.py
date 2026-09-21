from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    # PUBLIC STOREFRONT
    # ============================================================
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),

    # Designs & details
    path("designs/", views.designs, name="designs"),
    path("design-details/<str:design_id>/", views.design_details, name="design_details"),

    # ============================================================
    # CUSTOMER AUTH
    # ============================================================
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Password Reset
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url="/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/password-reset/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    # ============================================================
    # CUSTOMER PORTAL
    # ============================================================
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("customer/profile/", views.profile, name="profile"),
    path("customer/measurements/", views.measurements, name="measurements"),

    # Favorites
    path("customer/favorites/", views.favorites, name="favorites"),
    path("customer/favorites/toggle/<str:design_id>/", views.toggle_favorite, name="toggle_favorite"),

    # Cart
    path("cart/", views.cart, name="cart"),
    path("cart/add/<str:design_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),

    # Checkout & Orders
    path("checkout/", views.checkout, name="checkout"),
    path("order-confirmation/<str:order_number>/", views.order_confirmation, name="order_confirmation"),
    path("customer/orders/", views.orders, name="orders"),
    path(
        "customer/orders/cancel/<str:order_number>/",
        views.cancel_order,
        name="cancel_order",
    ),
    path("customer/tracking/", views.tracking, name="tracking"),
    path("customer/payments/", views.payments, name="payments"),
    path("customer/invoices/", views.invoices, name="invoices"),

    # Notifications
    path("customer/notifications/", views.notifications, name="notifications"),
    path("customer/notifications/read/<int:notification_id>/", views.mark_notification_read, name="mark_notification_read"),
    path("customer/notifications/read-all/", views.mark_all_notifications_read, name="mark_all_notifications_read"),

    # Feedback & Bookings
    path("customer/feedback/", views.feedback, name="feedback"),
    path("customer/bookings/", views.bookings, name="bookings"),
    path("customer/bookings/cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
]