from django import forms
from .models import Listing, Booking, Message

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'property_type', 'location', 'address',
            'daily_price', 'monthly_price', 'max_occupants', 'amenities', 
            'image1', 'image2', 'image3', 'is_available'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amenities': forms.Textarea(attrs={'rows': 2, 'placeholder': 'WiFi, Aircon, Parking, etc.'}),
            'address': forms.TextInput(attrs={'placeholder': 'Complete street address'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'number_of_guests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
            'number_of_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message here...'}),
        }