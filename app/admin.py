from django.contrib import admin
from .models import (
    Category,
    Design,
    Service,
    CustomerProfile,
    Measurement,
    Favorite,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    Invoice,
    Notification,
    Feedback,
    ContactMessage,
    Booking,
    WebsiteSettings,
    HeroSlide,
    BackgroundSection,
    WebsiteBanner,
    GalleryImage,
    AboutSection,
    WhyChooseUs,
    FAQ,
    SocialLink,
)


# ============================================================
# CATEGORY
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    list_editable = (
        "is_active",
    )


# ============================================================
# DESIGN
# ============================================================

@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):

    list_display = (
        "design_id",
        "name",
        "category",
        "price",
        "stock_quantity",
        "available",
        "is_active",
        "featured",
        "badge",
        "rating",
        "created_at",
    )

    list_filter = (
        "category",
        "available",
        "is_active",
        "featured",
        "badge",
        "created_at",
    )

    search_fields = (
        "design_id",
        "name",
        "description",
        "fabric",
        "color",
    )

    list_editable = (
        "price",
        "stock_quantity",
        "available",
        "is_active",
        "featured",
        "badge",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# SERVICE
# ============================================================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "price",
        "duration",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "duration",
    )

    list_editable = (
        "price",
        "duration",
        "is_active",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ============================================================
# CUSTOMER PROFILE
# ============================================================

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "phone",
        "city",
        "state",
        "pincode",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone",
        "city",
        "state",
        "pincode",
    )

    list_filter = (
        "state",
        "city",
        "created_at",
    )


# ============================================================
# MEASUREMENTS
# ============================================================

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):

    list_display = (
        "customer",
        "name",
        "is_default",
        "updated_at",
    )

    list_filter = (
        "is_default",
        "created_at",
    )

    search_fields = (
        "customer__username",
        "customer__email",
        "name",
        "notes",
    )


# ============================================================
# FAVORITES
# ============================================================

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "design",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "design__name",
        "design__design_id",
    )

    list_filter = (
        "created_at",
    )


# ============================================================
# CART
# ============================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "total_items",
        "subtotal",
        "shipping_charge",
        "total",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "total_items",
        "subtotal",
        "shipping_charge",
        "total",
        "created_at",
        "updated_at",
    )


# ============================================================
# CART ITEM
# ============================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "design",
        "quantity",
        "price",
        "subtotal",
        "created_at",
    )

    search_fields = (
        "cart__user__username",
        "cart__user__email",
        "design__name",
        "design__design_id",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )


# ============================================================
# ORDER
# ============================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "customer",
        "total_amount",
        "payment_method",
        "payment_status",
        "order_status",
        "created_at",
    )

    list_filter = (
        "order_status",
        "payment_status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "order_number",
        "customer__username",
        "customer__email",
        "shipping_name",
        "shipping_email",
        "shipping_phone",
        "shipping_city",
    )

    list_editable = (
        "payment_status",
        "order_status",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# ORDER ITEM
# ============================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "design",
        "quantity",
        "price",
        "subtotal",
        "measurement",
    )

    search_fields = (
        "order__order_number",
        "design__name",
        "design__design_id",
    )


# ============================================================
# PAYMENT
# ============================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "payment_method",
        "transaction_id",
        "amount",
        "status",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "paid_at",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "transaction_id",
        "order__customer__username",
        "order__customer__email",
    )

    list_editable = (
        "status",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ============================================================
# INVOICE
# ============================================================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "order",
        "subtotal",
        "shipping_charge",
        "total_amount",
        "issued_at",
    )

    search_fields = (
        "invoice_number",
        "order__order_number",
        "order__customer__username",
    )

    list_filter = (
        "issued_at",
    )


# ============================================================
# NOTIFICATION
# ============================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "title",
        "message",
    )

    list_editable = (
        "is_read",
    )


# ============================================================
# FEEDBACK
# ============================================================

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = (
        "customer",
        "order",
        "rating",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_approved",
        "created_at",
    )

    search_fields = (
        "customer__username",
        "customer__email",
        "comment",
    )

    list_editable = (
        "is_approved",
    )


# ============================================================
# CONTACT MESSAGE
# ============================================================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "phone",
        "subject",
        "is_resolved",
        "created_at",
    )

    list_filter = (
        "is_resolved",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
        "subject",
        "message",
    )

    list_editable = (
        "is_resolved",
    )


# ============================================================
# BOOKING
# ============================================================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "customer",
        "service",
        "booking_date",
        "booking_time",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "service",
        "booking_date",
        "created_at",
    )

    search_fields = (
        "customer__username",
        "customer__email",
        "service__name",
        "notes",
    )

    list_editable = (
        "status",
    )


# ============================================================
# WEBSITE SETTINGS
# ============================================================

@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):

    list_display = (
        "site_name",
        "tagline",
        "phone",
        "email",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "site_name",
        "tagline",
        "phone",
        "email",
        "address",
    )

    list_editable = (
        "is_active",
    )


# ============================================================
# HERO SLIDES
# ============================================================

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "subtitle",
        "description",
    )

    list_editable = (
        "order",
        "is_active",
    )

    ordering = (
        "order",
    )


# ============================================================
# BACKGROUND SECTIONS
# ============================================================

@admin.register(BackgroundSection)
class BackgroundSectionAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "section",
        "order",
        "overlay_opacity",
        "background_position",
        "background_size",
        "is_active",
    )

    list_filter = (
        "section",
        "is_active",
    )

    search_fields = (
        "name",
        "section",
    )

    list_editable = (
        "order",
        "overlay_opacity",
        "is_active",
    )


# ============================================================
# WEBSITE BANNERS
# ============================================================

@admin.register(WebsiteBanner)
class WebsiteBannerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "title",
        "order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "title",
        "subtitle",
        "description",
    )

    list_editable = (
        "order",
        "is_active",
    )


# ============================================================
# GALLERY
# ============================================================

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    list_editable = (
        "order",
        "is_active",
    )


# ============================================================
# ABOUT SECTION
# ============================================================

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "subtitle",
        "order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "subtitle",
        "content",
    )

    list_editable = (
        "order",
        "is_active",
    )


# ============================================================
# WHY CHOOSE US
# ============================================================

@admin.register(WhyChooseUs)
class WhyChooseUsAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    list_editable = (
        "order",
        "is_active",
    )


# ============================================================
# FAQ
# ============================================================

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):

    list_display = (
        "question",
        "order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "question",
        "answer",
    )

    list_editable = (
        "order",
        "is_active",
    )


# ============================================================
# SOCIAL LINKS
# ============================================================

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):

    list_display = (
        "platform",
        "label",
        "url",
        "order",
        "is_active",
    )

    list_filter = (
        "platform",
        "is_active",
    )

    search_fields = (
        "platform",
        "label",
        "url",
    )

    list_editable = (
        "order",
        "is_active",
    )