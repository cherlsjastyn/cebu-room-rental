from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('listings/', views.listing_list, name='listing_list'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('create/', views.create_listing, name='create_listing'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('edit/<int:pk>/', views.edit_listing, name='edit_listing'),
    path('delete/<int:pk>/', views.delete_listing, name='delete_listing'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('update-booking/<int:pk>/', views.update_booking_status, name='update_booking_status'),
    path('messages/', views.messages_view, name='messages'),
    path('conversation/<int:user_id>/<int:listing_id>/', views.conversation, name='conversation'),
    path('map/', views.map_view, name='map'),
    path('get-listings-json/', views.get_listings_json, name='get_listings_json'),
    path('api/listings/', views.get_listings_json, name='api_listings'),
    # NEW: Review System URLs
    path('review/listing/<int:pk>/', views.add_listing_review, name='add_listing_review'),
    path('review/delete/<int:pk>/', views.delete_listing_review, name='delete_listing_review'),
    path('feedback/', views.website_feedback, name='website_feedback'),
]