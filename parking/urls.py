from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    path('', views.register, name='register'),  # Set register.html as the default route
    path('home/', views.home, name='home'),

    # Dashboard page
    path('dashboard/', views.dashboard, name='dashboard'),

    # Slots list page
    path('slots/', views.slots, name='slots'),

    # Custom Login Page (parking/login.html inside templates/)
    path('accounts/login/', auth_views.LoginView.as_view(template_name='parking/login.html', redirect_authenticated_user=True), name='login'),  # Add redirect_authenticated_user=True

    # Logout
    path('logout/', views.logout_view, name='logout'),

    # User profile
    path('profile/', views.profile, name='profile'),

    # Book Slot - Original implementation with form
    path('book_slot/<int:slot_id>/', views.book_slot, name='book_slot'),
    
    # Book Slot - New direct reservation implementation
    path('book/', views.book_slot, name='book_slot_direct'),

    # Start and End Parking Session - NEW
    path('start-parking/<int:booking_id>/', views.start_parking, name='start_parking'),
    path('end-parking/<int:booking_id>/', views.end_parking, name='end_parking'),
    
    # Payment Routes - NEW
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment_page/<int:booking_id>/', views.payment_page, name='payment_page'),

    # Cancel Booking - Pass booking_id to cancel specific booking
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # Booking Details
    path('booking_detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),

    # Areas List (All areas)
    path('areas/', views.areas_view, name='areas_view'),

    # Search Area - Search for areas by name
    path('search_area/', views.search_area, name='search_area'),

    # Area Detail - Shows specific area details with subareas and slots
    path('area/<int:area_id>/', views.area_detail, name='area_detail'),

    # Subareas and Slots - List of all subareas with their parking slots
    path('subareas-and-slots/', views.subareas_and_slots, name='subareas_and_slots'),

    # Subarea Detail - Shows specific subarea details with parking slots
    path('subarea/<int:subarea_id>/', views.subarea_detail, name='subarea_detail'),

    # Contact Page - Form submission for user contact
    path('contact/', views.contact, name='contact'),

    # Feedback Page - Form submission for feedback
    path('feedback/', login_required(views.feedback), name='feedback'),

    # Booking Success - Page displayed after successful booking
    path('booking_success/', views.booking_success, name='booking_success'),
]