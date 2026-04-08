# rentals/forms.py
from django import forms
from .models import Listing, Booking, Message
from django.contrib.auth.models import User

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'property_type', 'location', 
                  'address', 'price', 'max_occupants', 'amenities', 
                  'image1', 'image2', 'image3', 'latitude', 'longitude']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amenities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'WiFi, Aircon, Parking, etc.'}),
            'address': forms.TextInput(attrs={'placeholder': 'Full address in Cebu City or Lapu-Lapu City'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'number_of_guests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out and check_in >= check_out:
            raise forms.ValidationError("Check-out date must be after check-in date")
        return cleaned_data

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        }