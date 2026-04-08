# rentals/models.py
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
    ]
    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    location = models.CharField(max_length=20, choices=LOCATIONS)
    address = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupants = models.IntegerField()
    
    # Amenities (simple text)
    amenities = models.TextField(blank=True, help_text="List amenities separated by commas")
    
    # Images
    image1 = models.ImageField(upload_to='listings/', blank=True, null=True)
    image2 = models.ImageField(upload_to='listings/', blank=True, null=True)
    image3 = models.ImageField(upload_to='listings/', blank=True, null=True)
    
    # Map coordinates (default to Cebu City center)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=10.3157)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=123.8854)
    
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