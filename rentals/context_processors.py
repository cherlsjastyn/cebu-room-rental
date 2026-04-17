# rentals/context_processors.py
from django.db.models import Q
from .models import Booking, Message

def notification_counts(request):
    """Add notification counts to all templates"""
    context = {
        'booking_notification_count': 0,
        'message_notification_count': 0,
    }
    
    if request.user.is_authenticated:
        # Count unread messages for the user (receiver only)
        message_count = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
        context['message_notification_count'] = message_count
        
        # Count pending booking requests (for property owners)
        if hasattr(request.user, 'profile') and request.user.profile.user_type == 'tenant':
            booking_count = Booking.objects.filter(
                listing__owner=request.user,
                status='pending'
            ).count()
            context['booking_notification_count'] = booking_count
    
    return context