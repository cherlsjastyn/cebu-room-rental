from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Listing, Booking, Message
from .forms import ListingForm, BookingForm, MessageForm
from datetime import datetime, date
from decimal import Decimal

def home(request):
    listings = Listing.objects.filter(is_available=True)[:6]
    return render(request, 'rentals/home.html', {'listings': listings})

def listing_list(request):
    listings = Listing.objects.filter(is_available=True)
    
    location = request.GET.get('location')
    property_type = request.GET.get('property_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    occupants = request.GET.get('occupants')
    
    if location and location != '':
        listings = listings.filter(location=location)
    if property_type and property_type != '':
        listings = listings.filter(property_type=property_type)
    if occupants and occupants.isdigit():
        listings = listings.filter(max_occupants__gte=int(occupants))
    
    # FIXED: Filter by daily_price OR monthly_price instead of price
    if min_price and min_price.isdigit():
        min_val = float(min_price)
        listings = listings.filter(
            Q(daily_price__gte=min_val) | Q(monthly_price__gte=min_val)
        )
    if max_price and max_price.isdigit():
        max_val = float(max_price)
        listings = listings.filter(
            Q(daily_price__lte=max_val) | Q(monthly_price__lte=max_val)
        )
    
    context = {
        'listings': listings,
        'property_types': Listing.PROPERTY_TYPES,
        'locations': Listing.LOCATIONS,
    }
    return render(request, 'rentals/listing_list.html', context)

def listing_detail(request, pk):
    from decimal import Decimal
    
    listing = get_object_or_404(Listing, pk=pk)
    can_book = request.user.is_authenticated and request.user != listing.owner
    
    # Handle booking form submission
    if request.method == 'POST' and 'book' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to book a room.')
            return redirect('login')
        
        if request.user == listing.owner:
            messages.error(request, 'You cannot book your own listing.')
            return redirect('listing_detail', pk=pk)
        
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.listing = listing
            booking.buyer = request.user
            
            days = (booking.check_out_date - booking.check_in_date).days
            if days <= 0:
                days = 1
            
            if listing.daily_price:
                booking.total_price = listing.daily_price * Decimal(days)
            elif listing.monthly_price:
                booking.total_price = listing.monthly_price * (Decimal(days) / Decimal(30))
            else:
                booking.total_price = Decimal(0)
            
            booking.save()
            messages.success(request, 'Booking request sent! The owner will confirm soon.')
            return redirect('my_bookings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()
    
    # Handle message submission - FIXED
    if request.method == 'POST':
        if 'message' in request.POST:
            message_text = request.POST.get('message', '').strip()
            
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to send messages.')
                return redirect('login')
            
            if message_text:
                message = Message.objects.create(
                    listing=listing,
                    sender=request.user,
                    receiver=listing.owner,
                    message=message_text,
                    is_read=False
                )
                messages.success(request, 'Message sent to the host!')
                return redirect('listing_detail', pk=pk)
            else:
                messages.error(request, 'Message cannot be empty.')
    
    msg_form = MessageForm()
    
    # Get conversation messages
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
    if hasattr(request.user, 'profile') and request.user.profile.user_type != 'tenant':
        messages.error(request, 'Only tenants can create listings. Please update your profile.')
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
    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'buyer':
        bookings = Booking.objects.filter(buyer=request.user).order_by('-booking_date')
    else:
        bookings = Booking.objects.filter(listing__owner=request.user).order_by('-booking_date')
    
    return render(request, 'rentals/my_bookings.html', {'bookings': bookings})

@login_required
def update_booking_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    is_owner = request.user == booking.listing.owner
    is_buyer = request.user == booking.buyer
    
    if not is_owner and not is_buyer:
        messages.error(request, 'You are not authorized to update this booking.')
        return redirect('my_bookings')
    
    status = request.POST.get('status')
    
    if is_owner and status in ['confirmed', 'cancelled', 'completed']:
        booking.status = status
        booking.save()
        messages.success(request, f'Booking {status}!')
    elif is_buyer and status == 'cancelled' and booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Your booking has been cancelled.')
    else:
        messages.error(request, 'You cannot perform this action.')
    
    return redirect('my_bookings')

@login_required
def messages_view(request):
    conversations = {}
    
    all_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')
    
    for msg in all_messages:
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        key = f"{other_user.id}_{msg.listing.id}"
        
        if key not in conversations:
            conversations[key] = {
                'user': other_user,
                'listing': msg.listing,
                'last_message': msg
            }
    
    return render(request, 'rentals/messages.html', {'conversations': list(conversations.values())})

@login_required
def conversation(request, user_id, listing_id):
    other_user = get_object_or_404(User, pk=user_id)
    listing = get_object_or_404(Listing, pk=listing_id)
    
    messages_list = Message.objects.filter(
        listing=listing
    ).filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')
    
    messages_list.filter(receiver=request.user, is_read=False).update(is_read=True)
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            Message.objects.create(
                listing=listing,
                sender=request.user,
                receiver=other_user,
                message=message_text,
                is_read=False
            )
            return redirect('conversation', user_id=other_user.id, listing_id=listing.id)
    
    context = {
        'messages': messages_list,
        'other_user': other_user,
        'listing': listing,
        'form': MessageForm(),
    }
    return render(request, 'rentals/conversation.html', context)

def map_view(request):
    listings = Listing.objects.filter(is_available=True)
    return render(request, 'rentals/map.html', {'listings': listings})

def get_listings_json(request):
    listings = Listing.objects.filter(is_available=True).values(
        'id', 'title', 'daily_price', 'monthly_price', 'property_type', 'location'
    )
    return JsonResponse(list(listings), safe=False)