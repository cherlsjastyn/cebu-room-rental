from django.contrib import admin
from .models import Listing, Booking, Message

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'location', 'daily_price', 'monthly_price', 'is_available', 'owner', 'created_at']
    list_filter = ['property_type', 'location', 'is_available']
    search_fields = ['title', 'address', 'owner__username']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['listing', 'buyer', 'check_in_date', 'check_out_date', 'total_price', 'status']
    list_filter = ['status', 'booking_date']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'listing', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']