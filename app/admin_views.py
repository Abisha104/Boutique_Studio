from decimal import Decimal
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.forms import modelform_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods
from django.db.models.deletion import ProtectedError

from .models import (
    AboutSection,
    BackgroundSection,
    Booking,
    Cart,
    CartItem,
    Category,
    ContactMessage,
    CustomerProfile,
    Design,
    FAQ,
    Favorite,
    Feedback,
    GalleryImage,
    HeroSlide,
    Invoice,
    Measurement,
    Notification,
    NewsletterSubscriber,
    Order,
    OrderItem,
    Payment,
    Service,
    SocialLink,
    StockItem,
    StockMovement,
    WebsiteBanner,
    WebsiteSettings,
    WhyChooseUs,
)

ADMIN_MODELS = {
    "categories": Category,
    "designs": Design,
    "services": Service,
    "customers": CustomerProfile,
    "measurements": Measurement,
    "favorites": Favorite,
    "carts": Cart,
    "cart-items": CartItem,
    "orders": Order,
    "order-items": OrderItem,
    "payments": Payment,
    "invoices": Invoice,
    "notifications": Notification,
    "newsletter-subscribers": NewsletterSubscriber,
    "feedback": Feedback,
    "contact-messages": ContactMessage,
    "bookings": Booking,
    "website-settings": WebsiteSettings,
    "hero-slides": HeroSlide,
    "background-sections": BackgroundSection,
    "website-banners": WebsiteBanner,
    "gallery": GalleryImage,
    "about-sections": AboutSection,
    "why-choose-us": WhyChooseUs,
    "faqs": FAQ,
    "social-links": SocialLink,
    "stock-movements": StockMovement,
}

ADMIN_GROUPS = [
    {
        "title": "SHOP",
        "items": [
            ("categories", "Categories", "bi-tags"),
            ("designs", "Designs", "bi-grid-1x2-fill"),
            ("services", "Services", "bi-scissors"),
        ],
    },
    {
        "title": "CUSTOMERS",
        "items": [
            ("customers", "Customers", "bi-people"),
            ("measurements", "Measurements", "bi-rulers"),
            ("favorites", "Favorites", "bi-heart"),
            ("carts", "Carts", "bi-cart3"),
        ],
    },
    {
        "title": "ORDERS",
        "items": [
            ("orders", "Orders", "bi-bag-check"),
            ("order-items", "Order Items", "bi-list-check"),
            ("payments", "Payments", "bi-credit-card"),
            ("invoices", "Invoices", "bi-receipt"),
        ],
    },
    {
        "title": "CUSTOMER ACTIVITY",
        "items": [
            ("notifications", "Notifications", "bi-bell"),
            ("feedback", "Feedback", "bi-chat-left-heart"),
            ("contact-messages", "Messages", "bi-envelope"),
            ("bookings", "Bookings", "bi-calendar-check"),
        ],
    },
    {
        "title": "MARKETING",
        "items": [
            ("newsletter-subscribers", "Newsletter Subscribers", "bi-envelope-paper"),
        ],
    },
    {
        "title": "WEBSITE",
        "items": [
            ("website-settings", "Website Settings", "bi-gear"),
            ("hero-slides", "Hero Slides", "bi-images"),
            ("background-sections", "Backgrounds", "bi-image"),
            ("website-banners", "Banners", "bi-card-image"),
            ("gallery", "Gallery", "bi-camera"),
            ("about-sections", "About Sections", "bi-info-circle"),
            ("why-choose-us", "Why Choose Us", "bi-stars"),
            ("faqs", "FAQs", "bi-question-circle"),
            ("social-links", "Social Links", "bi-share"),
        ],
    },
    {
        "title": "INVENTORY",
        "items": [
            ("inventory", "Inventory Overview", "bi-box-seam"),
            ("stock-movements", "Stock Movements", "bi-arrow-left-right"),
        ],
    },
]


def is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

staff_required = user_passes_test(is_staff, login_url="custom_admin_login")


def custom_admin_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect("custom_admin_dashboard")

    next_url = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                if url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)
                return redirect("custom_admin_dashboard")
            messages.error(request, "Invalid administrator credentials.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "custom_admin/login.html", {"form": form, "next_url": next_url})


@staff_required
def custom_admin_logout(request):
    logout(request)
    messages.success(request, "Administrator logged out.")
    return redirect("custom_admin_login")


@staff_required
def custom_admin_dashboard(request):
    counts = {key: model.objects.count() for key, model in ADMIN_MODELS.items()}

    context = {
        "counts": counts,
        "total_categories": Category.objects.count(),
        "total_designs": Design.objects.count(),
        "total_services": Service.objects.count(),
        "total_customers": CustomerProfile.objects.count(),
        "total_orders": Order.objects.count(),
        "total_bookings": Booking.objects.count(),
        "total_messages": ContactMessage.objects.count(),
        "total_feedback": Feedback.objects.count(),
        "total_payments": Payment.objects.count(),
        "recent_orders": Order.objects.select_related("customer").order_by("-created_at")[:6],
        "recent_bookings": Booking.objects.select_related("customer", "service").order_by("-created_at")[:5],
        "admin_groups": ADMIN_GROUPS,
    }
    return render(request, "custom_admin/dashboard.html", context)


@staff_required
def custom_admin_model_list(request, model_name):
    model = ADMIN_MODELS.get(model_name)
    if not model:
        messages.error(request, "Invalid admin section.")
        return redirect("custom_admin_dashboard")

    objects = model.objects.all()

    search = request.GET.get("q", "").strip()
    if search:
        search_fields = [
            field.name
            for field in model._meta.fields
            if field.get_internal_type() in ["CharField", "TextField", "EmailField", "URLField"]
        ]
        if search_fields:
            query = Q()
            for field_name in search_fields:
                query |= Q(**{f"{field_name}__icontains": search})
            objects = objects.filter(query)

    fields = [
        field for field in model._meta.fields
        if field.name not in ["id", "created_at", "updated_at"]
    ]

    list_context = {
        "model": model,
        "model_name": model_name,
        "objects": objects,
        "fields": fields,
        "search": search,
        "admin_groups": ADMIN_GROUPS,
        "verbose_name_plural": model._meta.verbose_name_plural,
        "verbose_name": model._meta.verbose_name,
    }
    if model_name == "newsletter-subscribers":
        latest = model.objects.order_by("-updated_at").values("updated_at").first()
        list_context.update({
            "total_count": model.objects.count(),
            "latest_updated_at": latest["updated_at"] if latest else None,
        })
    return render(request, "custom_admin/model_list.html", list_context)


def build_form(model):
    FormClass = modelform_factory(model, fields="__all__")

    class CustomBootstrapForm(FormClass):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.update({"class": "form-check-input"})
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({"class": "form-select"})
                else:
                    field.widget.attrs.update({"class": "form-control"})

    return CustomBootstrapForm


@staff_required
def custom_admin_add(request, model_name):
    model = ADMIN_MODELS.get(model_name)
    if not model:
        return redirect("custom_admin_dashboard")

    FormClass = build_form(model)

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            # Ensure a StockItem is created automatically when a Design is added
            if model_name == "designs":
                StockItem.objects.get_or_create(design=instance)
            messages.success(request, f"{model._meta.verbose_name.title()} added successfully.")
            return redirect("custom_admin_model_list", model_name=model_name)
    else:
        form = FormClass()

    return render(request, "custom_admin/form.html", {
        "model": model,
        "model_name": model_name,
        "form": form,
        "action": "Add",
        "verbose_name": model._meta.verbose_name,
        "verbose_name_plural": model._meta.verbose_name_plural,
        "admin_groups": ADMIN_GROUPS,
    })


@staff_required
def custom_admin_edit(request, model_name, pk):
    model = ADMIN_MODELS.get(model_name)
    if not model:
        return redirect("custom_admin_dashboard")

    instance = get_object_or_404(model, pk=pk)
    FormClass = build_form(model)

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            should_cancel = (
                model_name == "orders"
                and "order_status" in form.changed_data
                and form.cleaned_data.get("order_status") == Order.OrderStatus.CANCELLED
            )
            with transaction.atomic():
                if should_cancel:
                    instance.cancel_order()
                    # cancel_order updates payment/order status and stock. Keep
                    # those values when the generic form saves other edits.
                    form.instance.order_status = instance.order_status
                    form.instance.payment_status = instance.payment_status
                form.save()
            messages.success(request, f"{model._meta.verbose_name.title()} updated successfully.")
            return redirect("custom_admin_model_list", model_name=model_name)
    else:
        form = FormClass(instance=instance)

    return render(request, "custom_admin/form.html", {
        "form": form,
        "model": model,
        "model_name": model_name,
        "action": "Edit",
        "object": instance,
        "verbose_name": model._meta.verbose_name,
        "verbose_name_plural": model._meta.verbose_name_plural,
        "admin_groups": ADMIN_GROUPS,
    })


@staff_required
def custom_admin_delete(request, model_name, pk):
    model = ADMIN_MODELS.get(model_name)
    if not model:
        messages.error(request, "Invalid admin section.")
        return redirect("custom_admin_dashboard")

    instance = get_object_or_404(model, pk=pk)

    if request.method == "POST":
        if model_name == "designs":
            linked_order_items = OrderItem.objects.filter(design=instance).exists()
            if linked_order_items:
                messages.warning(
                    request,
                    "This design cannot be deleted because it is already used in existing orders. You can deactivate it instead."
                )
                return redirect("custom_admin_model_list", model_name=model_name)

        if model_name == "categories":
            linked_designs = Design.objects.filter(category=instance).exists()
            if linked_designs:
                messages.warning(
                    request,
                    "This category cannot be deleted because designs are currently linked to it. Please remove or update those designs first."
                )
                return redirect("custom_admin_model_list", model_name=model_name)

        try:
            instance.delete()
            messages.success(request, f"{model._meta.verbose_name.title()} deleted successfully.")
        except ProtectedError:
            messages.error(
                request,
                f"This {model._meta.verbose_name} cannot be deleted because it is being used by other records."
            )

        return redirect("custom_admin_model_list", model_name=model_name)

    return render(
        request,
        "custom_admin/confirm_delete.html",
        {
            "object": instance,
            "model": model,
            "model_name": model_name,
            "admin_groups": ADMIN_GROUPS,
        }
    )


# ============================================================
# INVENTORY CONTROLS & AUTO-SYNC
# ============================================================

def ensure_stock_items():
    """Ensures every existing design has an associated StockItem record."""
    for design in Design.objects.all():
        StockItem.objects.get_or_create(design=design)


@staff_required
def custom_admin_inventory(request):
    ensure_stock_items()
    items = StockItem.objects.select_related("design", "design__category").all().order_by("design__name")
    
    total_items = items.count()
    total_quantity = Design.objects.aggregate(total=Sum("stock_quantity"))["total"] or 0
    low_stock_count = sum(1 for item in items if item.is_low_stock)
    out_of_stock_count = sum(1 for item in items if item.is_out_of_stock)

    return render(request, "custom_admin/inventory.html", {
        "items": items,
        "total_items": total_items,
        "total_quantity": total_quantity,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "admin_groups": ADMIN_GROUPS,
    })


@staff_required
def api_get_designs_by_category(request):
    """AJAX helper: returns designs belonging to a selected category."""
    category_id = request.GET.get("category_id")
    designs_qs = Design.objects.filter(is_active=True)
    if category_id:
        designs_qs = designs_qs.filter(category_id=category_id)

    data = [
        {
            "id": d.id,
            "design_id": d.design_id,
            "name": d.name,
            "stock_quantity": d.stock_quantity,
        }
        for d in designs_qs
    ]
    return JsonResponse({"designs": data})


@staff_required
def api_newsletter_subscriber_status(request):
    latest = NewsletterSubscriber.objects.order_by("-updated_at").values("updated_at").first()
    response = JsonResponse({
        "count": NewsletterSubscriber.objects.count(),
        "latest_updated_at": latest["updated_at"].isoformat() if latest else None,
    })
    response["Cache-Control"] = "no-store"
    return response


@staff_required
@require_http_methods(["GET", "POST"])
def custom_admin_stock_in(request):
    ensure_stock_items()
    categories = Category.objects.filter(is_active=True)
    designs = Design.objects.filter(is_active=True).select_related("category")

    if request.method == "POST":
        design_id_val = request.POST.get("design_id", "").strip()
        design_pk = request.POST.get("design")
        quantity = request.POST.get("quantity")
        reason = request.POST.get("reason", "").strip()

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid quantity.")
            return redirect("custom_admin_stock_in")

        if quantity <= 0:
            messages.error(request, "Quantity must be greater than 0.")
            return redirect("custom_admin_stock_in")

        target_design = None
        if design_id_val:
            target_design = Design.objects.filter(design_id__iexact=design_id_val).first()
        elif design_pk:
            target_design = Design.objects.filter(pk=design_pk).first()

        if not target_design:
            messages.error(request, "Design not found. Check category selection or Design ID.")
            return redirect("custom_admin_stock_in")

        with transaction.atomic():
            target_design = Design.objects.select_for_update().get(pk=target_design.pk)
            stock_item, _ = StockItem.objects.get_or_create(design=target_design)
            target_design.adjust_stock(quantity)
            StockMovement.objects.create(
                item=stock_item,
                movement_type=StockMovement.STOCK_IN,
                quantity=quantity,
                reason=reason or "Admin Manual Stock-In",
            )

        messages.success(request, f"Added {quantity} pcs to '{target_design.name}' ({target_design.design_id}).")
        return redirect("custom_admin_inventory")

    return render(request, "custom_admin/inventory_stock_in.html", {
        "categories": categories,
        "designs": designs,
        "admin_groups": ADMIN_GROUPS,
    })


@staff_required
@require_http_methods(["GET", "POST"])
def custom_admin_stock_out(request):
    ensure_stock_items()
    categories = Category.objects.filter(is_active=True)
    designs = Design.objects.filter(is_active=True).select_related("category")

    if request.method == "POST":
        design_id_val = request.POST.get("design_id", "").strip()
        design_pk = request.POST.get("design")
        quantity = request.POST.get("quantity")
        reason = request.POST.get("reason", "").strip()

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid quantity.")
            return redirect("custom_admin_stock_out")

        if quantity <= 0:
            messages.error(request, "Quantity must be greater than 0.")
            return redirect("custom_admin_stock_out")

        target_design = None
        if design_id_val:
            target_design = Design.objects.filter(design_id__iexact=design_id_val).first()
        elif design_pk:
            target_design = Design.objects.filter(pk=design_pk).first()

        if not target_design:
            messages.error(request, "Design not found. Check category selection or Design ID.")
            return redirect("custom_admin_stock_out")

        with transaction.atomic():
            target_design = Design.objects.select_for_update().get(pk=target_design.pk)
            stock_item, _ = StockItem.objects.get_or_create(design=target_design)
            if quantity > target_design.stock_quantity:
                messages.error(request, f"Cannot remove {quantity} pcs. Available stock is only {target_design.stock_quantity} pcs.")
                return redirect("custom_admin_stock_out")
            target_design.adjust_stock(-quantity)
            StockMovement.objects.create(
                item=stock_item,
                movement_type=StockMovement.STOCK_OUT,
                quantity=quantity,
                reason=reason or "Admin Manual Stock-Out",
            )

        messages.success(request, f"Removed {quantity} pcs from '{target_design.name}' ({target_design.design_id}).")
        return redirect("custom_admin_inventory")

    return render(request, "custom_admin/inventory_stock_out.html", {
        "categories": categories,
        "designs": designs,
        "admin_groups": ADMIN_GROUPS,
    })


@staff_required
def custom_admin_stock_history(request):
    movements = StockMovement.objects.select_related("item__design").order_by("-created_at")
    movement_type = request.GET.get("movement_type", "").strip().upper()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    if movement_type in {StockMovement.STOCK_IN, StockMovement.STOCK_OUT}:
        movements = movements.filter(movement_type=movement_type)

    parsed_from = parse_date(date_from) if date_from else None
    parsed_to = parse_date(date_to) if date_to else None
    if parsed_from:
        movements = movements.filter(created_at__date__gte=parsed_from)
    if parsed_to:
        movements = movements.filter(created_at__date__lte=parsed_to)
    if not parsed_from and not parsed_to:
        movements = movements.filter(created_at__date=timezone.localdate())

    movement_totals = movements.values("movement_type").annotate(total=Sum("quantity"))
    totals = {
        row["movement_type"]: row["total"]
        for row in movement_totals
    }

    return render(request, "custom_admin/inventory_stock_history.html", {
        "movements": movements,
        "stock_in_total": totals.get(StockMovement.STOCK_IN, 0),
        "stock_out_total": totals.get(StockMovement.STOCK_OUT, 0),
        "movement_count": movements.count(),
        "movement_type": movement_type,
        "date_from": date_from,
        "date_to": date_to,
        "admin_groups": ADMIN_GROUPS,
    })