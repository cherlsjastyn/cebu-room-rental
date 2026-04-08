# rentals/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Listing, Booking, Message
from .forms import ListingForm, BookingForm, MessageForm
from django.utils import timezone
from datetime import datetime

def home(request):
    # Get all available listings
    listings = Listing.objects.filter(is_available=True)[:6]  # Show 6 on homepage
    return render(request, 'rentals/home.html', {'listings': listings})

def listing_list(request):
    # Get all listings with filters
    listings = Listing.objects.filter(is_available=True)
    
    # Search and filters
    location = request.GET.get('location')
    property_type = request.GET.get('property_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    occupants = request.GET.get('occupants')
    
    if location and location != '':
        listings = listings.filter(location=location)
    if property_type and property_type != '':
        listings = listings.filter(property_type=property_type)
    if min_price:
        listings = listings.filter(price__gte=min_price)
    if max_price:
        listings = listings.filter(price__lte=max_price)
    if occupants:
        listings = listings.filter(max_occupants__gte=occupants)
    
    # Get all unique property types for filter dropdown
    property_types = Listing.PROPERTY_TYPES
    
    context = {
        'listings': listings,
        'property_types': property_types,
    }
    return render(request, 'rentals/listing_list.html', context)

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    
    # Check if user can book
    can_book = request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.user_type == 'buyer'
    
    # Handle booking form
    if request.method == 'POST' and 'book' in request.POST:
        if not can_book:
            messages.error(request, 'Only buyers can book rooms. Please register as a buyer.')
            return redirect('listing_detail', pk=pk)
        
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.listing = listing
            booking.buyer = request.user
            
            # Calculate total price (simple: price * number of days)
            days = (booking.check_out_date - booking.check_in_date).days
            booking.total_price = listing.price * days
            
            booking.save()
            messages.success(request, 'Booking request sent! The owner will confirm soon.')
            return redirect('my_bookings')
    else:
        form = BookingForm()
    
    # Handle message form
    if request.method == 'POST' and 'message' in request.POST:
        if request.user.is_authenticated:
            msg_form = MessageForm(request.POST)
            if msg_form.is_valid():
                message = msg_form.save(commit=False)
                message.listing = listing
                message.sender = request.user
                message.receiver = listing.owner
                message.save()
                messages.success(request, 'Message sent!')
                return redirect('listing_detail', pk=pk)
        else:
            messages.error(request, 'Please login to send messages.')
    
    msg_form = MessageForm()
    
    # Get messages for this listing (only show if user is owner or has messaged)
    messages_list = []
    if request.user.is_authenticated:
        messages_list = Message.objects.filter(listing=listing).filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).order_by('created_at')
    
    context = {
        'listing': listing,
        'form': form,
        'msg_form': msg_form,
        'messages': messages_list,
        'can_book': can_book,
    }
    return render(request, 'rentals/listing_detail.html', context)

@login_required
def create_listing(request):
    # Only tenants can create listings
    if request.user.profile.user_type != 'tenant':
        messages.error(request, 'Only tenants can create listings.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            messages.success(request, 'Your listing has been created!')
            return redirect('my_listings')
    else:
        form = ListingForm()
    
    return render(request, 'rentals/create_listing.html', {'form': form})

@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user)
    return render(request, 'rentals/my_listings.html', {'listings': listings})

@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated!')
            return redirect('my_listings')
    else:
        form = ListingForm(instance=listing)
    
    return render(request, 'rentals/edit_listing.html', {'form': form, 'listing': listing})

@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted!')
        return redirect('my_listings')
    return render(request, 'rentals/delete_listing.html', {'listing': listing})

@login_required
def my_bookings(request):
    if request.user.profile.user_type == 'buyer':
        # Bookings made by this user
        bookings = Booking.objects.filter(buyer=request.user).order_by('-booking_date')
    else:
        # Bookings for listings owned by this user
        bookings = Booking.objects.filter(listing__owner=request.user).order_by('-booking_date')
    
    return render(request, 'rentals/my_bookings.html', {'bookings': bookings})

@login_required
def update_booking_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk, listing__owner=request.user)
    status = request.POST.get('status')
    
    if status in ['confirmed', 'cancelled', 'completed']:
        booking.status = status
        booking.save()
        messages.success(request, f'Booking {status}!')
    
    return redirect('my_bookings')

@login_required
def messages_view(request):
    # Get all conversations for the user
    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(receiver=request.user)
    
    # Get unique conversation partners
    conversations = set()
    for msg in sent_messages:
        conversations.add((msg.receiver, msg.listing))
    for msg in received_messages:
        conversations.add((msg.sender, msg.listing))
    
    conversation_list = []
    for user, listing in conversations:
        conversation_list.append({
            'user': user,
            'listing': listing,
            'last_message': Message.objects.filter(
                Q(sender=request.user, receiver=user, listing=listing) |
                Q(sender=user, receiver=request.user, listing=listing)
            ).latest('created_at')
        })
    
    return render(request, 'rentals/messages.html', {'conversations': conversation_list})

@login_required
def conversation(request, user_id, listing_id):
    other_user = get_object_or_404(User, pk=user_id)
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # Get all messages between these users for this listing
    messages_list = Message.objects.filter(
        listing=listing
    ).filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')
    
    # Mark unread messages as read
    messages_list.filter(receiver=request.user, is_read=False).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.listing = listing
            message.sender = request.user
            message.receiver = other_user
            message.save()
            return redirect('conversation', user_id=other_user.id, listing_id=listing.id)
    else:
        form = MessageForm()
    
    context = {
        'messages': messages_list,
        'other_user': other_user,
        'listing': listing,
        'form': form,
    }
    return render(request, 'rentals/conversation.html', context)

def map_view(request):
    listings = Listing.objects.filter(is_available=True)
    return render(request, 'rentals/map.html', {'listings': listings})

def get_listings_json(request):
    listings = Listing.objects.filter(is_available=True).values(
        'id', 'title', 'latitude', 'longitude', 'price', 'property_type', 'location'
    )
    return JsonResponse(list(listings), safe=False)