from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models import Count, Avg
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta
import json
import math
import logging

from .models import Area, SubArea, ParkingSlot, Booking, Feedback
from .forms import UserRegistrationForm, BookingForm, ContactForm, FeedbackForm
from .models import LoginRegisterLog, UserAuthenticationRegistration

logger = logging.getLogger(__name__)

# -------------------------------
# Home view to display available areas and slots
# -------------------------------
def home(request):
    search_query = request.GET.get('search_query', '')

    if search_query:
        areas = Area.objects.filter(name__icontains=search_query).prefetch_related('subareas__parkingslots')
    else:
        areas = Area.objects.prefetch_related('subareas__parkingslots')

    if not areas.exists():
        messages.error(request, "No areas available.")
        return render(request, 'parking/home.html', {'areas': [], 'search_query': search_query, 'user': request.user})

    return render(request, 'parking/home.html', {'areas': areas, 'search_query': search_query, 'user': request.user})

def slots(request):
    parking_slots = ParkingSlot.objects.all()
    return render(request, 'parking/slots.html', {'parking_slots': parking_slots})

# -------------------------------
# Register view for user registration
# -------------------------------
@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            LoginRegisterLog.objects.create(user=user, action='register')
            login(request, user)  # Automatically log in the user after registration
            messages.success(request, "Registration successful!")
            return redirect('home')  # Redirect to home.html after successful registration
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'parking/register.html', {'form': form})

# -------------------------------
# Login view for user authentication
# -------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home.html after successful login
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    # Render login.html for GET requests
    return render(request, 'parking/login.html')

# -------------------------------
# Logout view
# -------------------------------
def logout_view(request):
    if request.user.is_authenticated:
        try:
            logger.debug(f"Creating log for user {request.user.username} with action 'logout'.")
            LoginRegisterLog.objects.create(user=request.user, action='logout')
            logger.debug(f"Log successfully created for user {request.user.username} with action 'logout'.")
        except Exception as e:
            logger.error(f"Error creating logout log: {str(e)}")
    
    logout(request)
    return redirect('parking:login')

# -------------------------------
# Dashboard view for logged-in users
# -------------------------------
@login_required
def dashboard(request):
    current_time = timezone.now()

    # Update booking statuses based on current time
    Booking.objects.filter(status='reserved', expiry_time__lt=current_time).update(status='completed')

    # Get all user's bookings
    user_bookings = Booking.objects.filter(user=request.user).order_by('-reservation_time')

    # Get available parking slots for new bookings
    available_slots = ParkingSlot.objects.filter(is_available=True)

    # Get all areas and their subareas
    areas = Area.objects.prefetch_related('subareas__parkingslots').all()

    # Check if user has unpaid bookings
    has_unpaid_bookings = Booking.objects.filter(
        user=request.user,
        status='completed',
        paid=False
    ).exists()

    context = {
        'user_bookings': user_bookings,
        'areas': areas,
        'bookings': user_bookings,
        'available_slots': available_slots,
        'has_unpaid_bookings': has_unpaid_bookings,
        'current_time': current_time,
        'user': request.user,
    }
    return render(request, 'parking/dashboard.html', context)

# -------------------------------
# Slot booking view
# -------------------------------
@login_required
def book_slot(request, slot_id=None):
    """Reserve a parking slot"""
    if slot_id:
        # Fetch the slot details
        slot = get_object_or_404(ParkingSlot, id=slot_id)

        if request.method == 'POST':
            form = BookingForm(request.POST, parking_slot=slot)

            if form.is_valid():
                booking = form.save(commit=False)
                booking.user = request.user
                booking.parking_slot = slot
                booking.status = 'reserved'  # Set status to reserved
                booking.reservation_time = timezone.now()  # Set the current time as reservation time
                booking.expiry_time = booking.reservation_time + timedelta(minutes=15)  # Grace period starts from reservation time

                try:
                    booking.clean()  # Validate slot availability
                    booking.save()

                    # Mark the slot as unavailable
                    slot.is_available = False
                    slot.save()

                    messages.success(request, f"Booking successful! Reserved at {booking.reservation_time}. Your grace period ends at {booking.expiry_time}.")
                    return redirect('parking:booking_success')  # Redirect to booking_success.html
                except ValidationError as e:
                    form.add_error(None, e)

            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = BookingForm()

        return render(request, 'parking/book_slot.html', {'form': form, 'slot': slot})

    # If no slot_id is provided, redirect to the search results page
    messages.error(request, "Invalid slot selection.")
    return redirect('parking:search_results')

# -------------------------------
# Start parking session
# -------------------------------
@login_required
def start_parking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    current_time = timezone.now()

    if booking.status == 'reserved' and current_time <= booking.expiry_time:
        booking.status = 'active'
        booking.start_time = current_time
        booking.save()
        messages.success(request, "Parking session started successfully.")
    else:
        messages.error(request, "Your booking has expired or is invalid.")

    return redirect('parking:dashboard')

# -------------------------------
# End parking session
# -------------------------------
@login_required
def end_parking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status == 'active':
        booking.end_time = timezone.now()
        duration = (booking.end_time - booking.start_time).total_seconds() / 3600
        duration_hours = math.ceil(duration)
        rate_per_hour = 20
        booking.amount = duration_hours * rate_per_hour
        booking.status = 'completed'
        booking.save()
        return redirect('parking:payment_page', booking_id=booking.id)
    
    messages.error(request, "Invalid booking status.")
    return redirect('parking:dashboard')

# -------------------------------
# Payment success handler
# -------------------------------
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        booking_id = request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)
        booking.paid = True
        booking.save()
        booking.parking_slot.is_available = True
        booking.parking_slot.save()
        messages.success(request, "Payment successful. Thank you for using our parking service!")
        return render(request, 'parking/payment_success.html')
    
    return HttpResponseBadRequest()

# -------------------------------
# Payment page view
# -------------------------------
@login_required
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    context = {
        'booking': booking,
    }
    return render(request, 'parking/payment_page.html', context)

# -------------------------------
# Booking success view
# -------------------------------
def booking_success(request):
    return render(request, 'parking/booking_success.html')

# -------------------------------
# Cancel booking view
# -------------------------------
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    slot = booking.parking_slot
    slot.is_available = True
    slot.save()
    booking.delete()
    messages.success(request, "Your booking has been cancelled.")
    return redirect('parking:dashboard')

# -------------------------------
# Booking detail view
# -------------------------------
@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'parking/booking_detail.html', {'booking': booking})

# -------------------------------
# Areas View
# -------------------------------
def areas_view(request):
    areas = Area.objects.all()
    return render(request, 'parking/areas.html', {'areas': areas})

# -------------------------------
# Search Area View
# -------------------------------
def search_area(request):
    query = request.GET.get('q', '')
    areas = Area.objects.filter(name__icontains=query) if query else Area.objects.all()
    subareas = SubArea.objects.filter(area__in=areas).prefetch_related('parkingslots')

    # Fetch booked slots using the is_available field
    booked_slots = ParkingSlot.objects.filter(is_available=False)
    booked_slot_ids = json.dumps(list(booked_slots.values_list('id', flat=True)), cls=DjangoJSONEncoder)

    return render(request, 'parking/search_results.html', {
        'areas': areas,
        'subareas': subareas,
        'query': query,
        'booked_slots': booked_slot_ids  # Pass booked slots to the template as JSON
    })

# -------------------------------
# SubArea and Slots View
# -------------------------------
def subareas_and_slots(request):
    subareas = SubArea.objects.prefetch_related('parkingslots').all()
    return render(request, 'parking/subareas_and_slots.html', {'subareas': subareas})

# -------------------------------
# SubArea detail view
# -------------------------------
def subarea_detail(request, subarea_id):
    subarea = get_object_or_404(SubArea, id=subarea_id)
    slots = ParkingSlot.objects.filter(sub_area=subarea)
    return render(request, 'parking/subarea_detail.html', {'subarea': subarea, 'slots': slots})

# -------------------------------
# Area detail view
# -------------------------------
def area_detail(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    subareas = SubArea.objects.filter(area=area).prefetch_related('parkingslots')
    return render(request, 'parking/search_results.html', {
        'area': area,
        'subareas': subareas,
        'slots': ParkingSlot.objects.filter(sub_area__in=subareas),
    })

# -------------------------------
# Contact view
# -------------------------------
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect('parking:home')
    else:
        form = ContactForm()
    return render(request, 'parking/contact.html', {'form': form})

# -------------------------------
# Feedback view
# -------------------------------
@login_required
def feedback(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        goal_achievement = request.POST.get('goal_achievement')
        reason = request.POST.get('reason')
        issue = request.POST.get('issue')
        suggestions = request.POST.get('suggestions')
        
        if not rating:
            messages.error(request, "Please provide a rating.")
            return render(request, 'parking/feedback.html')
        
        feedback = Feedback(
            rating=rating,
            comments=comments,
            goal_achievement=goal_achievement,
            reason=reason,
            issue=issue,
            suggestions=suggestions
        )
        
        if request.user.is_authenticated:
            feedback.user = request.user
            
        feedback.save()
        messages.success(request, "Thank you for your feedback!")
        return redirect('parking:home')
    
    return render(request, 'parking/feedback.html')

# -------------------------------
# Feedback Dashboard (Admin)
# -------------------------------
@staff_member_required
def feedback_dashboard(request):
    period = request.GET.get('period', 'all')
    feedback_queryset = Feedback.objects.all()
    now = timezone.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
        feedback_queryset = feedback_queryset.filter(submitted_on__gte=start_date)
    elif period == 'month':
        start_date = now - timedelta(days=30)
        feedback_queryset = feedback_queryset.filter(submitted_on__gte=start_date)
    elif period == 'year':
        start_date = now - timedelta(days=365)
        feedback_queryset = feedback_queryset.filter(submitted_on__gte=start_date)
    
    total_feedback = feedback_queryset.count()
    avg_rating = feedback_queryset.aggregate(Avg('rating'))['rating__avg'] or 0
    goal_achievement = feedback_queryset.values('goal_achievement').annotate(
        count=Count('id')).order_by('-count')
    reason_breakdown = feedback_queryset.values('reason').annotate(
        count=Count('id')).order_by('-count')
    issue_breakdown = feedback_queryset.values('issue').annotate(
        count=Count('id')).order_by('-count')
    
    goal_data = []
    for item in goal_achievement:
        if item['goal_achievement']:
            goal_data.append({
                'label': item['goal_achievement'],
                'value': item['count']
            })
    
    reason_data = []
    for item in reason_breakdown:
        if item['reason']:
            reason_data.append({
                'label': item['reason'],
                'value': item['count']
            })
    
    issue_data = []
    for item in issue_breakdown:
        if item['issue']:
            issue_data.append({
                'label': item['issue'],
                'value': item['count']
            })
    
    recent_feedback = feedback_queryset.order_by('-submitted_on')[:10]
    
    context = {
        'total_feedback': total_feedback,
        'avg_rating': round(avg_rating, 1),
        'period': period,
        'goal_data_json': json.dumps(goal_data),
        'reason_data_json': json.dumps(reason_data),
        'issue_data_json': json.dumps(issue_data),
        'recent_feedback': recent_feedback,
    }
    
    return render(request, 'admin/feedback_dashboard.html', context)

# -------------------------------
# User Profile View
# -------------------------------
@login_required
def profile(request):
    user = request.user
    user_bookings = Booking.objects.filter(user=user).order_by('-start_time')

    context = {
        'user': user,
        'user_bookings': user_bookings,
    }
    return render(request, 'parking/profile.html', context)

# -------------------------------
# Utilities
# -------------------------------
@login_required
def expire_bookings():
    expired_bookings = Booking.objects.filter(status='reserved', expiry_time__lt=timezone.now())
    for booking in expired_bookings:
        booking.status = 'completed'
        booking.save()
    return True

@login_required
def clear_all_bookings(request):
    Booking.objects.all().delete()
    ParkingSlot.objects.update(is_available=True)
    messages.success(request, "All bookings have been cleared and all slots are now available.")
    return redirect('parking:dashboard')