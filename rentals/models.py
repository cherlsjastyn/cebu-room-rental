from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Listing(models.Model):
    # Property types
    PROPERTY_TYPES = [
        ('boarding', 'Boarding House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condominium'),
        ('dorm', 'Dormitory'),
        ('airbnb', 'Airbnb'),
    ]
    
    LOCATIONS = [
        ('cebu_city', 'Cebu City'),
        ('lapulapu', 'Lapu-Lapu City'),
        ('mandaue', 'Mandaue City'),
        ('talisay', 'Talisay City'),
        ('naga', 'Naga City'),
        ('carcar', 'Carcar City'),
        ('toledo', 'Toledo City'),
    ]
    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    location = models.CharField(max_length=20, choices=LOCATIONS)
    address = models.CharField(max_length=500)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_occupants = models.IntegerField()
    
    # Amenities (simple text)
    amenities = models.TextField(blank=True, help_text="List amenities separated by commas")
    
    # Images - LOCAL STORAGE (saved in media/listings/ folder)
    image1 = models.ImageField(upload_to='listings/', blank=True, null=True)
    image2 = models.ImageField(upload_to='listings/', blank=True, null=True)
    image3 = models.ImageField(upload_to='listings/', blank=True, null=True)
    
    # Owner
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def get_amenities_list(self):
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []
    
    def get_lowest_price(self):
        if self.daily_price and self.monthly_price:
            return min(self.daily_price, self.monthly_price)
        elif self.daily_price:
            return self.daily_price
        elif self.monthly_price:
            return self.monthly_price
        return 0
    
    def get_price_unit(self):
        if self.daily_price and self.monthly_price:
            return "lowest"
        elif self.daily_price:
            return "night"
        elif self.monthly_price:
            return "month"
        return ""

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking for {self.listing.title} by {self.buyer.username}"

class Message(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

# ========== NEW: REVIEW SYSTEM MODELS ==========

class ListingReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['listing', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} rated {self.listing.title}: {self.rating} stars"

class WebsiteFeedback(models.Model):
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} rated: {self.rating} stars on {self.created_at.date()}"