from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import F, Sum
from django.utils import timezone


# ============================================================
# CATEGORY
# ============================================================

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return self.email


# ============================================================
# DESIGN (PRODUCT)
# ============================================================

class Design(models.Model):
    BADGE_CHOICES = [
        ("", "No Badge"),
        ("new", "New Arrival"),
        ("premium", "Premium"),
        ("bestseller", "Bestseller"),
        ("trending", "Trending"),
        ("popular", "Popular"),
        ("signature", "Signature"),
        ("luxury", "Luxury"),
        ("special", "Special"),
        ("bridal", "Bridal"),
        ("couture", "Couture"),
    ]

    design_id = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="designs"
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    image = models.ImageField(upload_to="designs/", blank=True, null=True)
    fabric = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    badge = models.CharField(
        max_length=30,
        choices=BADGE_CHOICES,
        blank=True,
        default=""
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("5.0")),
        ]
    )
    review_count = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    stock_quantity = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Design"
        verbose_name_plural = "Designs"

    def __str__(self):
        return f"{self.design_id} - {self.name}"

    @property
    def is_in_stock(self):
        return self.available and self.is_active and self.stock_quantity > 0

    def adjust_stock(self, quantity_change):
        """Atomically adjusts stock quantity and updates availability flag."""
        new_quantity = self.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"Insufficient stock for {self.name}. Requested: {abs(quantity_change)}, Available: {self.stock_quantity}")
        self.stock_quantity = new_quantity
        if self.stock_quantity == 0:
            self.available = False
        elif self.stock_quantity > 0 and not self.available:
            self.available = True
        self.save(update_fields=["stock_quantity", "available", "updated_at"])


# ============================================================
# SERVICE
# ============================================================

class Service(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name


# ============================================================
# CUSTOMER PROFILE
# ============================================================

class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# ============================================================
# MEASUREMENTS
# ============================================================

class Measurement(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="measurements"
    )
    name = models.CharField(max_length=100, default="My Measurements")
    bust = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    waist = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    hip = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    shoulder = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    sleeve_length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    blouse_length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    neck = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    armhole = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    front_neck = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    back_neck = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Measurement"
        verbose_name_plural = "Measurements"

    def __str__(self):
        return f"{self.customer} - {self.name}"


# ============================================================
# FAVORITES
# ============================================================

class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    design = models.ForeignKey(
        Design,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "design"],
                name="unique_user_design_favorite"
            )
        ]
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"

    def __str__(self):
        return f"{self.user} - {self.design.name}"


# ============================================================
# CART & CART ITEM
# ============================================================

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart - {self.user}"

    @property
    def total_items(self):
        result = self.items.aggregate(total=Sum("quantity"))
        return result["total"] or 0

    @property
    def subtotal(self):
        result = self.items.aggregate(
            total=Sum(F("quantity") * F("price"))
        )
        return result["total"] or Decimal("0.00")

    @property
    def shipping_charge(self):
        if self.subtotal == Decimal("0.00") or self.subtotal >= Decimal("1000.00"):
            return Decimal("0.00")
        return Decimal("50.00")

    @property
    def total(self):
        return self.subtotal + self.shipping_charge


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    design = models.ForeignKey(
        Design,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "design"],
                name="unique_cart_design"
            )
        ]
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def save(self, *args, **kwargs):
        if (self.price is None or self.price == Decimal("0.00")) and self.design:
            self.price = self.design.price
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.design.name} x {self.quantity}"


# ============================================================
# ORDER & ORDER ITEM
# ============================================================

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROCESSING = "PROCESSING", "Processing"
        STITCHING = "STITCHING", "Stitching"
        READY = "READY", "Ready"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    class PaymentMethod(models.TextChoices):
        COD = "COD", "Cash on Delivery"
        CARD = "CARD", "Credit / Debit Card"
        UPI = "UPI", "UPI / QR Code"
        DEMO = "DEMO", "Demo Payment"
        RAZORPAY = "RAZORPAY", "Razorpay"
        STRIPE = "STRIPE", "Stripe"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )
    order_number = models.CharField(max_length=30, unique=True, db_index=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    shipping_name = models.CharField(max_length=150)
    shipping_email = models.EmailField()
    shipping_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_pincode = models.CharField(max_length=10, blank=True)

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.order_number

    @property
    def item_count(self):
        result = self.items.aggregate(total=Sum("quantity"))
        return result["total"] or 0

    def cancel_order(self):
        """Restores stock for all items atomically when an order is cancelled."""
        if self.order_status == self.OrderStatus.CANCELLED:
            return False
        with transaction.atomic():
            for item in self.items.select_related("design").all():
                item.design.adjust_stock(item.quantity)
            self.order_status = self.OrderStatus.CANCELLED
            if self.payment_status == self.PaymentStatus.PAID:
                self.payment_status = self.PaymentStatus.REFUNDED
            self.save(update_fields=["order_status", "payment_status", "updated_at"])
        return True


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    design = models.ForeignKey(
        Design,
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    measurement = models.ForeignKey(
        Measurement,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="order_items"
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.order_number} - {self.design.name} x {self.quantity}"


# ============================================================
# PAYMENT & INVOICE
# ============================================================

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )
    payment_method = models.CharField(max_length=30)
    transaction_id = models.CharField(max_length=150, blank=True, null=True, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def mark_success(self, transaction_id=None):
        self.status = self.Status.SUCCESS
        self.paid_at = timezone.now()
        if transaction_id:
            self.transaction_id = transaction_id
        self.save(update_fields=["status", "paid_at", "transaction_id", "updated_at"])
        self.order.payment_status = Order.PaymentStatus.PAID
        self.order.save(update_fields=["payment_status", "updated_at"])

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class Invoice(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="invoice"
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    @property
    def is_paid(self):
        return self.order.payment_status == Order.PaymentStatus.PAID

    def __str__(self):
        return self.invoice_number


# ============================================================
# NOTIFICATION, FEEDBACK, MESSAGES & BOOKINGS
# ============================================================

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.user} - {self.title}"


class Feedback(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="feedback"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def __str__(self):
        return f"{self.customer} - {self.rating}/5"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="bookings"
    )
    booking_date = models.DateField()
    booking_time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-booking_date", "-booking_time"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"{self.customer} - {self.service.name} - {self.booking_date}"


# ============================================================
# CMS / WEBSITE CONTENT MODELS
# ============================================================

class WebsiteSettings(models.Model):
    site_name = models.CharField(max_length=150, default="Shylu Threads")
    tagline = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to="website/logo/", blank=True, null=True)
    favicon = models.ImageField(upload_to="website/favicon/", blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    footer_text = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    whatsapp_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Settings"
        verbose_name_plural = "Website Settings"

    def __str__(self):
        return self.site_name


class HeroSlide(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="website/hero/")
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=500, blank=True)
    secondary_button_text = models.CharField(max_length=100, blank=True)
    secondary_button_url = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"

    def __str__(self):
        return self.title


class BackgroundSection(models.Model):
    SECTION_CHOICES = [
        ("home", "Home"),
        ("about", "About"),
        ("collection", "Collection"),
        ("services", "Services"),
        ("booking", "Booking"),
        ("contact", "Contact"),
        ("footer", "Footer"),
        ("custom", "Custom"),
    ]

    name = models.CharField(max_length=150)
    section = models.CharField(max_length=30, choices=SECTION_CHOICES)
    background_image = models.ImageField(upload_to="website/backgrounds/")
    overlay_opacity = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.30"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))]
    )
    background_position = models.CharField(max_length=100, default="center")
    background_size = models.CharField(max_length=100, default="cover")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["section", "order", "-created_at"]
        verbose_name = "Background Section"
        verbose_name_plural = "Background Sections"

    def __str__(self):
        return f"{self.name} - {self.section}"


class WebsiteBanner(models.Model):
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="website/banners/")
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Website Banner"
        verbose_name_plural = "Website Banners"

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="website/gallery/")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return self.title or f"Gallery Image {self.pk}"


class AboutSection(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="website/about/", blank=True, null=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "About Section"
        verbose_name_plural = "About Sections"

    def __str__(self):
        return self.title


class WhyChooseUs(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="website/features/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Why Choose Us"
        verbose_name_plural = "Why Choose Us"

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class SocialLink(models.Model):
    PLATFORM_CHOICES = [
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("youtube", "YouTube"),
        ("whatsapp", "WhatsApp"),
        ("twitter", "Twitter / X"),
        ("pinterest", "Pinterest"),
        ("linkedin", "LinkedIn"),
        ("custom", "Custom"),
    ]

    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    label = models.CharField(max_length=100, blank=True)
    url = models.URLField()
    icon = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "platform"]
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"

    def __str__(self):
        return self.label or self.get_platform_display()


# ============================================================
# INVENTORY: STOCK ITEMS & MOVEMENTS
# ============================================================
# ============================================================
# INVENTORY: STOCK ITEMS & MOVEMENTS
# ============================================================
class StockItem(models.Model):
    design = models.OneToOneField(
        Design,
        on_delete=models.CASCADE,
        related_name="inventory",
        null=True,
        blank=True
    )
    minimum_stock = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Stock Item"
        verbose_name_plural = "Stock Items"

    def __str__(self):
        if self.design:
            return f"{self.design.design_id} - {self.design.name} - {self.quantity} pcs"
        return f"Stock Item #{self.id}"

    @property
    def item_name(self):
        return self.design.name if self.design else f"Item #{self.id}"

    @property
    def quantity(self):
        return self.design.stock_quantity if self.design else 0

    @property
    def unit(self):
        return "pcs"

    @property
    def is_out_of_stock(self):
        return self.quantity <= 0

    @property
    def is_low_stock(self):
        return 0 < self.quantity <= self.minimum_stock

class StockMovement(models.Model):
    STOCK_IN = "IN"
    STOCK_OUT = "OUT"

    MOVEMENT_CHOICES = [
        (STOCK_IN, "Stock In"),
        (STOCK_OUT, "Stock Out"),
    ]

    movement_type = models.CharField(
        max_length=5,
        choices=MOVEMENT_CHOICES
    )

    item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        related_name="movements"
    )

    quantity = models.PositiveIntegerField()

    reason = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"

    def __str__(self):
        return (
            f"{self.get_movement_type_display()} - "
            f"{self.quantity} pcs - "
            f"{self.item.design.design_id}"
        )