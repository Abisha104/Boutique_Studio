from decimal import Decimal
from django import forms
from django.contrib.auth.models import User
from .models import (
    Booking,
    ContactMessage,
    CustomerProfile,
    Feedback,
    Measurement,
    Order,
    StockItem,
    StockMovement,
)


class RegisterForm(forms.ModelForm):
    name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)

    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if CustomerProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomerProfile
        fields = ["phone", "address", "city", "state", "pincode", "profile_image"]


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = [
            "name",
            "bust",
            "waist",
            "hip",
            "shoulder",
            "sleeve_length",
            "blouse_length",
            "neck",
            "armhole",
            "front_neck",
            "back_neck",
            "notes",
        ]


class CheckoutForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Order
        fields = [
            "shipping_city",
            "shipping_state",
            "shipping_pincode",
            "payment_method",
            "notes",
        ]


class FeedbackForm(forms.ModelForm):
    title = forms.CharField(max_length=100, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Feedback
        fields = ["rating"]


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["service", "booking_date", "booking_time", "notes"]


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = [
            "item_name",
            "sku_code",
            "category",
            "quantity",
            "unit",
            "unit_price",
            "minimum_stock",
        ]


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "movement_type",
            "item",
            "quantity",
            "reason",
        ]