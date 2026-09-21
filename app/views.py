from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone

from .models import (
    AboutSection,
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
    StockItem,
    StockMovement,
    WebsiteSettings,
    WhyChooseUs,
)


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def is_customer(user):
    return user.is_authenticated and not (user.is_staff or user.is_superuser)


customer_required = user_passes_test(is_customer, login_url="login")


def generate_order_number():
    while True:
        order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid4().hex[:4].upper()}"
        if not Order.objects.filter(order_number=order_number).exists():
            return order_number


def generate_invoice_number():
    while True:
        invoice_number = f"INV{timezone.now().strftime('%Y%m%d')}{uuid4().hex[:6].upper()}"
        if not Invoice.objects.filter(invoice_number=invoice_number).exists():
            return invoice_number


def get_progress_percentage(status):
    progress = {
        Order.OrderStatus.PENDING: 15,
        Order.OrderStatus.CONFIRMED: 30,
        Order.OrderStatus.PROCESSING: 50,
        Order.OrderStatus.STITCHING: 70,
        Order.OrderStatus.READY: 85,
        Order.OrderStatus.SHIPPED: 95,
        Order.OrderStatus.DELIVERED: 100,
        Order.OrderStatus.CANCELLED: 0,
    }
    return progress.get(status, 0)


# ============================================================
# STOREFRONT
# ============================================================

def home(request):
    featured_designs = Design.objects.filter(is_active=True, available=True, featured=True)[:6]
    if not featured_designs.exists():
        featured_designs = Design.objects.filter(is_active=True, available=True)[:6]

    services_list = Service.objects.filter(is_active=True)[:6]
    categories_list = Category.objects.filter(is_active=True)
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by("order")
    why_us = WhyChooseUs.objects.filter(is_active=True).order_by("order")[:4]

    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_count = request.user.cart.total_items
        except Cart.DoesNotExist:
            cart_count = 0

    return render(request, "app/index.html", {
        "featured_designs": featured_designs,
        "services": services_list,
        "categories": categories_list,
        "hero_slides": hero_slides,
        "why_us": why_us,
        "cart_count": cart_count,
    })


def about(request):
    about_sections = AboutSection.objects.filter(is_active=True).order_by("order")
    why_choose_us = WhyChooseUs.objects.filter(is_active=True).order_by("order")
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by("order")[:6]
    return render(request, "app/about.html", {
        "about_sections": about_sections,
        "why_choose_us": why_choose_us,
        "gallery_images": gallery_images,
    })


def how_it_works(request):
    faqs = FAQ.objects.filter(is_active=True).order_by("order")
    return render(request, "app/how-it-works.html", {"faqs": faqs})


def services(request):
    service_list = Service.objects.filter(is_active=True).order_by("name")
    return render(request, "app/services.html", {"services": service_list})


def designs(request):
    categories_list = Category.objects.filter(is_active=True).prefetch_related("designs")
    selected_category = request.GET.get("category", "").strip()
    search = request.GET.get("search", "").strip()
    selected_sort = request.GET.get("sort", "Newest")

    design_list = Design.objects.filter(is_active=True).select_related("category")

    if selected_category and selected_category != "All":
        design_list = design_list.filter(category__name__iexact=selected_category)

    if search:
        design_list = design_list.filter(
            Q(name__icontains=search) |
            Q(category__name__icontains=search) |
            Q(description__icontains=search) |
            Q(fabric__icontains=search) |
            Q(design_id__icontains=search)
        )

    if selected_sort == "PriceLow":
        design_list = design_list.order_by("price")
    elif selected_sort == "PriceHigh":
        design_list = design_list.order_by("-price")
    elif selected_sort == "Popular":
        design_list = design_list.order_by("-featured", "-rating", "-created_at")
    else:
        design_list = design_list.order_by("-created_at")

    favorite_ids = set()
    cart_count = 0
    if request.user.is_authenticated:
        favorite_ids = set(Favorite.objects.filter(user=request.user).values_list("design__id", flat=True))
        try:
            cart_count = request.user.cart.total_items
        except Cart.DoesNotExist:
            cart_count = 0

    return render(request, "app/designs.html", {
        "categories": categories_list,
        "designs": design_list,
        "selected_category": selected_category,
        "selected_sort": selected_sort,
        "search": search,
        "favorite_ids": favorite_ids,
        "cart_count": cart_count,
    })


def design_details(request, design_id):
    design = get_object_or_404(Design, design_id=design_id, is_active=True)
    is_favorite = False
    cart_count = 0

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, design=design).exists()
        try:
            cart_count = request.user.cart.total_items
        except Cart.DoesNotExist:
            cart_count = 0

    related_designs = Design.objects.filter(
        category=design.category,
        is_active=True
    ).exclude(id=design.id)[:4]

    return render(request, "app/design-details.html", {
        "design": design,
        "is_favorite": is_favorite,
        "related_designs": related_designs,
        "cart_count": cart_count,
    })


# ============================================================
# AUTHENTICATION
# ============================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect("custom_admin_dashboard" if request.user.is_staff else "customer_dashboard")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        errors = []
        if not name:
            errors.append("Full name is required.")
        if not phone:
            errors.append("Phone number is required.")
        if not email:
            errors.append("Email address is required.")
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if email and User.objects.filter(email__iexact=email).exists():
            errors.append("An account with this email already exists.")
        if phone and CustomerProfile.objects.filter(phone=phone).exists():
            errors.append("This phone number is already registered.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "app/register.html")

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=name
                )
                CustomerProfile.objects.create(user=user, phone=phone)
                Cart.objects.create(user=user)
                login(request, user)
                messages.success(request, f"Welcome to Shylu Threads, {name}!")
                return redirect("designs")
        except Exception:
            messages.error(request, "Failed to create account. Please try again.")
            return render(request, "app/register.html")

    return render(request, "app/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("custom_admin_dashboard" if request.user.is_staff else "customer_dashboard")

    next_url = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")
        remember = request.POST.get("remember_me") == "on"

        if not identifier or not password:
            messages.error(request, "Please enter your email/phone and password.")
            return render(request, "app/login.html", {"next_url": next_url})

        user = None
        try:
            user_obj = User.objects.get(email__iexact=identifier)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

        if user is None:
            try:
                profile = CustomerProfile.objects.get(phone=identifier)
                user = authenticate(request, username=profile.user.username, password=password)
            except CustomerProfile.DoesNotExist:
                pass

        if user is None or user.is_staff or user.is_superuser:
            messages.error(request, "Invalid login credentials.")
            return render(request, "app/login.html", {"next_url": next_url})

        if not user.is_active:
            messages.error(request, "Your account has been deactivated.")
            return render(request, "app/login.html", {"next_url": next_url})

        login(request, user)
        if remember:
            request.session.set_expiry(1209600)
        else:
            request.session.set_expiry(0)

        messages.success(request, f"Welcome back, {user.first_name or user.username}!")
        if url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect("customer_dashboard")

    return render(request, "app/login.html", {"next_url": next_url})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")


# ============================================================
# CUSTOMER PORTAL
# ============================================================

@customer_required
def customer_dashboard(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related("items__design")
    total_orders = orders.count()
    active_orders = orders.exclude(
        order_status__in=[Order.OrderStatus.DELIVERED, Order.OrderStatus.CANCELLED]
    ).count()
    completed_orders = orders.filter(order_status=Order.OrderStatus.DELIVERED).count()
    pending_payment_amount = sum(
        order.total_amount for order in orders.filter(payment_status=Order.PaymentStatus.PENDING)
    )
    recent_orders = orders[:5]
    favorites_count = Favorite.objects.filter(user=request.user).count()
    notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    cart = get_or_create_cart(request.user)

    return render(request, "customer/dashboard.html", {
        "customer": request.user,
        "total_orders": total_orders,
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "pending_payment": pending_payment_amount,
        "recent_orders": recent_orders,
        "favorites_count": favorites_count,
        "notifications_count": notifications_count,
        "cart_count": cart.total_items,
    })


@customer_required
def profile(request):
    customer_profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        if not name or not email:
            messages.error(request, "Name and Email are required.")
            return redirect("profile")

        request.user.first_name = name
        request.user.email = email
        request.user.save(update_fields=["first_name", "email"])

        customer_profile.phone = phone
        customer_profile.address = address
        customer_profile.city = city
        customer_profile.state = state
        customer_profile.pincode = pincode

        if request.FILES.get("profile_image"):
            customer_profile.profile_image = request.FILES["profile_image"]

        customer_profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "customer/profile.html", {
        "profile": customer_profile,
        "user": request.user,
    })


@customer_required
def measurements(request):
    measurement = Measurement.objects.filter(customer=request.user).order_by("-updated_at").first()

    if request.method == "POST":
        if measurement is None:
            measurement = Measurement(customer=request.user)

        measurement.name = request.POST.get("name", "My Measurements")

        def parse_decimal(field):
            val = request.POST.get(field, "").strip()
            try:
                return Decimal(val) if val else None
            except Exception:
                return None

        measurement.bust = parse_decimal("bust")
        measurement.waist = parse_decimal("waist")
        measurement.hip = parse_decimal("hips")
        measurement.shoulder = parse_decimal("shoulder")
        measurement.sleeve_length = parse_decimal("sleeve")
        measurement.blouse_length = parse_decimal("blouse_length")
        measurement.neck = parse_decimal("neck")
        measurement.armhole = parse_decimal("armhole")
        measurement.front_neck = parse_decimal("front_neck")
        measurement.back_neck = parse_decimal("back_neck")
        measurement.notes = request.POST.get("notes", "").strip()

        measurement.save()
        messages.success(request, "Measurements updated successfully.")
        return redirect("measurements")

    return render(request, "customer/measurements.html", {"measurement": measurement})


@customer_required
def favorites(request):
    favorite_list = Favorite.objects.filter(user=request.user).select_related("design__category")
    return render(request, "customer/favorites.html", {"favorites": favorite_list})


@customer_required
def toggle_favorite(request, design_id):
    design = get_object_or_404(Design, design_id=design_id)
    favorite = Favorite.objects.filter(user=request.user, design=design).first()

    if favorite:
        favorite.delete()
        is_fav = False
        msg = f"Removed '{design.name}' from favorites."
    else:
        Favorite.objects.create(user=request.user, design=design)
        is_fav = True
        msg = f"Added '{design.name}' to favorites!"

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success", "is_favorite": is_fav, "message": msg})

    messages.success(request, msg)
    return redirect(request.META.get("HTTP_REFERER", "designs"))


# ============================================================
# CART OPERATIONS (WITH AJAX & NO REDIRECT OPTION)
# ============================================================

@customer_required
def cart(request):
    user_cart = get_or_create_cart(request.user)
    items = user_cart.items.select_related("design__category")
    return render(request, "app/cart.html", {
        "cart": user_cart,
        "cart_items": items,
    })


@customer_required
def add_to_cart(request, design_id):
    design = get_object_or_404(Design, design_id=design_id, is_active=True)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if not design.is_in_stock:
        if is_ajax:
            return JsonResponse({"status": "error", "message": f"'{design.name}' is out of stock."}, status=400)
        messages.error(request, f"Sorry, '{design.name}' is currently out of stock.")
        return redirect("designs")

    # If clicked "Order Now / Buy Now", bypass regular cart addition
    if request.GET.get("buy_now") == "1":
        return redirect(f"/checkout/?buy_now=1&design_id={design.design_id}")

    user_cart = get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=user_cart,
        design=design,
        defaults={"quantity": 1, "price": design.price}
    )

    if not created:
        if item.quantity < design.stock_quantity:
            item.quantity += 1
            item.price = design.price
            item.save()
            msg = f"Updated quantity for '{design.name}'."
        else:
            msg = f"Only {design.stock_quantity} units available."
            if is_ajax:
                return JsonResponse({"status": "warning", "message": msg, "cart_count": user_cart.total_items})
            messages.warning(request, msg)
            return redirect(request.META.get("HTTP_REFERER", "designs"))
    else:
        msg = f"Added '{design.name}' to cart!"

    if is_ajax:
        return JsonResponse({
            "status": "success",
            "message": msg,
            "cart_count": user_cart.total_items
        })

    messages.success(request, msg)
    return redirect(request.META.get("HTTP_REFERER", "designs"))


@customer_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            item.delete()
            messages.success(request, "Item removed from cart.")
        elif quantity > item.design.stock_quantity:
            item.quantity = item.design.stock_quantity
            item.save()
            messages.warning(request, f"Quantity adjusted to available stock ({item.design.stock_quantity}).")
        else:
            item.quantity = quantity
            item.price = item.design.price
            item.save()

    return redirect("cart")


@customer_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")


@customer_required
def clear_cart(request):
    user_cart = get_or_create_cart(request.user)
    user_cart.items.all().delete()
    messages.success(request, "Your cart has been cleared.")
    return redirect("cart")


# ============================================================
# CHECKOUT (HANDLES BOTH CART CHECKOUT & DIRECT BUY NOW)
# ============================================================

@customer_required
def checkout(request):
    is_buy_now = request.GET.get("buy_now") == "1" or request.POST.get("buy_now") == "1"
    buy_now_design_id = request.GET.get("design_id") or request.POST.get("design_id")

    items_to_checkout = []
    subtotal = Decimal("0.00")
    shipping = Decimal("0.00")

    if is_buy_now and buy_now_design_id:
        direct_design = get_object_or_404(Design, design_id=buy_now_design_id, is_active=True)
        if not direct_design.is_in_stock:
            messages.error(request, f"'{direct_design.name}' is out of stock.")
            return redirect("designs")

        items_to_checkout = [{
            "design": direct_design,
            "quantity": 1,
            "price": direct_design.price,
            "subtotal": direct_design.price,
        }]
        subtotal = direct_design.price
        shipping = Decimal("0.00") if subtotal >= Decimal("1000.00") else Decimal("50.00")
    else:
        user_cart = get_or_create_cart(request.user)
        cart_items = user_cart.items.select_related("design")
        if not cart_items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("cart")

        for ci in cart_items:
            items_to_checkout.append({
                "design": ci.design,
                "quantity": ci.quantity,
                "price": ci.price,
                "subtotal": ci.subtotal,
            })
        subtotal = user_cart.subtotal
        shipping = user_cart.shipping_charge

    total = subtotal + shipping

    profile_obj, _ = CustomerProfile.objects.get_or_create(user=request.user)
    cart_summary = {
        "subtotal": subtotal,
        "shipping_charge": shipping,
        "total": total,
    }
    checkout_context = {
        "checkout_items": items_to_checkout,
        "cart_items": items_to_checkout,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "cart": cart_summary,
        "is_buy_now": is_buy_now,
        "buy_now_design_id": buy_now_design_id,
        "profile": profile_obj,
    }

    if request.method == "POST":
        customer_name = request.POST.get("customerName", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        payment_method = request.POST.get("payment", Order.PaymentMethod.COD)

        if not all([customer_name, email, phone, address]):
            messages.error(request, "Please complete all required shipping fields.")
            return render(request, "app/checkout.html", checkout_context)

        if payment_method not in {
            Order.PaymentMethod.CARD,
            Order.PaymentMethod.UPI,
            Order.PaymentMethod.COD,
        }:
            messages.error(request, "Please select a valid payment method.")
            return render(request, "app/checkout.html", checkout_context)

        try:
            with transaction.atomic():
                # Verify stock & lock
                for item_data in items_to_checkout:
                    locked_design = Design.objects.select_for_update().get(id=item_data["design"].id)
                    if not locked_design.is_active or not locked_design.available:
                        raise ValueError(f"'{locked_design.name}' is no longer available.")
                    if locked_design.stock_quantity < item_data["quantity"]:
                        raise ValueError(f"Only {locked_design.stock_quantity} pcs remaining for '{locked_design.name}'.")

                order = Order.objects.create(
                    customer=request.user,
                    order_number=generate_order_number(),
                    subtotal=subtotal,
                    shipping_charge=shipping,
                    total_amount=total,
                    shipping_name=customer_name,
                    shipping_email=email,
                    shipping_phone=phone,
                    shipping_address=address,
                    shipping_city=city,
                    shipping_state=state,
                    shipping_pincode=pincode,
                    payment_method=payment_method,
                    payment_status=Order.PaymentStatus.PAID if payment_method in [Order.PaymentMethod.DEMO, Order.PaymentMethod.CARD, Order.PaymentMethod.UPI] else Order.PaymentStatus.PENDING,
                    order_status=Order.OrderStatus.CONFIRMED,
                )

                customer_measurement = Measurement.objects.filter(customer=request.user, is_default=True).first()

                # Deduct stock and write StockMovement log
                for item_data in items_to_checkout:
                    locked_design = Design.objects.select_for_update().get(id=item_data["design"].id)
                    locked_design.adjust_stock(-item_data["quantity"])

                    stock_item, _ = StockItem.objects.get_or_create(design=locked_design)
                    StockMovement.objects.create(
                        item=stock_item,
                        movement_type=StockMovement.STOCK_OUT,
                        quantity=item_data["quantity"],
                        reason=f"Customer Order #{order.order_number}",
                    )

                    OrderItem.objects.create(
                        order=order,
                        design=locked_design,
                        quantity=item_data["quantity"],
                        price=locked_design.price,
                        subtotal=locked_design.price * item_data["quantity"],
                        measurement=customer_measurement,
                    )

                # Payment & Invoice
                payment_status = Payment.Status.SUCCESS if order.payment_status == Order.PaymentStatus.PAID else Payment.Status.PENDING
                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=total,
                    status=payment_status,
                    transaction_id=f"TXN{uuid4().hex[:10].upper()}" if payment_status == Payment.Status.SUCCESS else None,
                    paid_at=timezone.now() if payment_status == Payment.Status.SUCCESS else None,
                )

                Invoice.objects.create(
                    order=order,
                    invoice_number=generate_invoice_number(),
                    subtotal=subtotal,
                    shipping_charge=shipping,
                    total_amount=total,
                )

                Notification.objects.create(
                    user=request.user,
                    title="Order Placed Successfully",
                    message=f"Your order #{order.order_number} for ₹{total} has been confirmed.",
                )

                # Clear cart ONLY if checked out from normal cart
                if not is_buy_now:
                    get_or_create_cart(request.user).items.all().delete()

            messages.success(request, f"Order {order.order_number} placed successfully!")
            return redirect("order_confirmation", order_number=order.order_number)

        except ValueError as err:
            messages.error(request, str(err))
            return render(request, "app/checkout.html", checkout_context)
        except Exception:
            messages.error(request, "Failed to place order. Please try again.")
            return render(request, "app/checkout.html", checkout_context)

    return render(request, "app/checkout.html", checkout_context)


@customer_required
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    return render(request, "customer/order-confirmation.html", {"order": order})


@customer_required
def orders(request):
    order_list = Order.objects.filter(customer=request.user).prefetch_related("items__design").order_by("-created_at")
    return render(request, "customer/orders.html", {"orders": order_list})


@customer_required
def cancel_order(request, order_number):
    if request.method != "POST":
        messages.error(request, "Please use the cancel button to cancel an order.")
        return redirect("orders")

    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    if order.order_status in [Order.OrderStatus.PENDING, Order.OrderStatus.CONFIRMED]:
        with transaction.atomic():
            for item in order.items.select_related("design").all():
                item.design.adjust_stock(item.quantity)
                stock_item, _ = StockItem.objects.get_or_create(design=item.design)
                StockMovement.objects.create(
                    item=stock_item,
                    movement_type=StockMovement.STOCK_IN,
                    quantity=item.quantity,
                    reason=f"Order Cancelled #{order.order_number}",
                )
            order.order_status = Order.OrderStatus.CANCELLED
            order.save(update_fields=["order_status", "updated_at"])

        Notification.objects.create(
            user=request.user,
            title="Order Cancelled",
            message=f"Your order #{order.order_number} has been cancelled and stock has been restored.",
        )
        messages.success(request, f"Order {order.order_number} has been cancelled.")
    else:
        messages.error(request, "This order cannot be cancelled at its current stage.")
    return redirect("orders")


@customer_required
def tracking(request):
    order_list = Order.objects.filter(customer=request.user).order_by("-created_at")
    tracking_data = [
        {"order": order, "progress": get_progress_percentage(order.order_status)}
        for order in order_list
    ]
    return render(request, "customer/tracking.html", {"tracking_orders": tracking_data})


@customer_required
def payments(request):
    payment_list = Payment.objects.filter(order__customer=request.user).select_related("order").order_by("-created_at")
    successful_count = payment_list.filter(status=Payment.Status.SUCCESS).count()
    pending_count = payment_list.filter(status=Payment.Status.PENDING).count()
    total_paid = payment_list.filter(status=Payment.Status.SUCCESS).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    return render(request, "customer/payments.html", {
        "payments": payment_list,
        "payment_count": payment_list.count(),
        "successful_count": successful_count,
        "pending_count": pending_count,
        "total_paid": total_paid,
    })


@customer_required
def invoices(request):
    invoice_list = Invoice.objects.filter(order__customer=request.user).select_related("order").order_by("-issued_at")
    return render(request, "customer/invoices.html", {"invoices": invoice_list})


# ============================================================
# NOTIFICATIONS, FEEDBACK, BOOKINGS & CONTACT
# ============================================================

@customer_required
def notifications(request):
    notification_list = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "customer/notifications.html", {"notifications": notification_list})


@customer_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect("notifications")


@customer_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications")


@customer_required
def feedback(request):
    feedback_list = Feedback.objects.filter(customer=request.user).order_by("-created_at")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        comment = request.POST.get("message", "").strip()
        rating_value = request.POST.get("rating", "5")

        try:
            rating = int(rating_value)
        except ValueError:
            rating = 5
        rating = max(1, min(rating, 5))

        if not title or not comment:
            messages.error(request, "Please fill in your feedback title and comment.")
            return redirect("feedback")

        Feedback.objects.create(
            customer=request.user,
            rating=rating,
            comment=f"{title}: {comment}",
            is_approved=True,
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect("feedback")

    return render(request, "customer/feedback.html", {"feedback": feedback_list})


@customer_required
def bookings(request):
    booking_list = Booking.objects.filter(customer=request.user).select_related("service").order_by("-booking_date")
    return render(request, "customer/bookings.html", {"bookings": booking_list})


@customer_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if booking.status not in [Booking.Status.COMPLETED, Booking.Status.CANCELLED]:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, "Booking cancelled successfully.")
    return redirect("bookings")


def newsletter_subscribe(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed."}, status=405)

    email = request.POST.get("newsletter_email", "").strip().lower()
    if not email:
        return JsonResponse({"status": "error", "message": "Please enter your email address."}, status=400)

    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"status": "error", "message": "Please enter a valid email address."}, status=400)

    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={"is_active": True},
    )
    if not created and not subscriber.is_active:
        subscriber.is_active = True
        subscriber.save(update_fields=["is_active", "updated_at"])

    message = "You are subscribed to our newsletter!" if created else "You are already subscribed."
    return JsonResponse({"status": "success", "message": message})


def contact(request):
    service_list = Service.objects.filter(is_active=True)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        service_id = request.POST.get("service", "")
        preferred_date = request.POST.get("preferredDate", "")
        message = request.POST.get("message", "").strip()

        if not all([name, email, phone, message]):
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "All required fields must be filled."}, status=400)
            messages.error(request, "Please fill all required fields.")
            return redirect("contact")

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject or "Tailoring Consultation",
            message=message,
        )

        if service_id and preferred_date and request.user.is_authenticated:
            try:
                service = Service.objects.get(id=service_id, is_active=True)
                b_date = datetime.strptime(preferred_date, "%Y-%m-%d").date()
                Booking.objects.create(
                    customer=request.user,
                    service=service,
                    booking_date=b_date,
                    booking_time=datetime.strptime("10:00", "%H:%M").time(),
                    notes=message,
                )
            except Exception:
                pass

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Your enquiry has been submitted successfully!"})

        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")

    return render(request, "app/contact.html", {"services": service_list})