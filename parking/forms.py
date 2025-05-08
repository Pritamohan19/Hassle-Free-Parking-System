# forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Booking, ParkingSlot, Area, SubArea, Contact, Feedback

# Replace User with the custom user model
User = get_user_model()

# User Registration Form
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)  # Add password confirmation field
    email = forms.EmailField(required=True)  # Ensure the email field is required

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Explicitly set username and email fields to ensure correct mapping
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password


# Improved Booking Form with built-in validation
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['vehicle_type', 'vehicle_number', 'start_time', 'end_time']

        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'vehicle_type': forms.Select(choices=[
                ('2-wheeler', '2-Wheeler'),
                ('4-wheeler', '4-Wheeler')
            ]),
        }
        
    def __init__(self, *args, parking_slot=None, **kwargs):
        self.parking_slot = parking_slot  # Store the parking_slot
        super().__init__(*args, **kwargs)
        if self.parking_slot:
            self.instance.parking_slot = self.parking_slot
        # Set initial values for start_time and end_time if they're not provided
        if not self.initial.get('start_time'):
            self.initial['start_time'] = timezone.now() + timedelta(hours=2)
        if not self.initial.get('end_time'):
            self.initial['end_time'] = timezone.now() + timedelta(hours=3)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Ensure parking_slot is set
        if not self.instance.parking_slot:
            raise forms.ValidationError("Parking slot must be specified.")

        # Custom validation for start_time and end_time
        if start_time and end_time:
            # Ensure that the booking is at least 2 hours in advance
            if start_time < timezone.now() + timedelta(hours=2):
                raise forms.ValidationError("You must book at least 2 hours in advance.")

            # Ensure the end_time is after the start_time
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time.")

            # Check for conflicting bookings
            conflicting_booking = Booking.objects.filter(
                parking_slot=self.instance.parking_slot,
                end_time__gt=start_time,
                start_time__lt=end_time
            ).exists()
            if conflicting_booking:
                raise forms.ValidationError("The selected parking slot is already booked during this time.")

        return cleaned_data


# Form for Sub-Area (Ensure proper ForeignKey relationship with Area)
class SubAreaForm(forms.ModelForm):
    class Meta:
        model = SubArea
        fields = ['area', 'name', 'description']

    area = forms.ModelChoiceField(
        queryset=Area.objects.all(),
        empty_label="Select an Area",
        help_text="Please select an area to assign the sub-area."
    )


# Slot Form for parking slot creation
class SlotForm(forms.ModelForm):
    class Meta:
        model = ParkingSlot
        fields = ['sub_area', 'slot_number', 'is_available']
        
    sub_area = forms.ModelChoiceField(queryset=SubArea.objects.all(), empty_label="Choose Sub-Area")

    def clean_slot_number(self):
        slot_number = self.cleaned_data.get('slot_number')
        sub_area = self.cleaned_data.get('sub_area')
        if ParkingSlot.objects.filter(sub_area=sub_area, slot_number=slot_number).exists():
            raise forms.ValidationError(f"Slot number {slot_number} already exists in this sub-area.")
        return slot_number


# Contact Form
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']


# Feedback Form
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = [
            'rating', 
            'comments', 
            'goal_achievement', 
            'reason', 
            'issue', 
            'suggestions'
        ]
        widgets = {
            'rating': forms.NumberInput(attrs={'min': '1', 'max': '5', 'required': True}),
            'comments': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comments here...'}),
            'suggestions': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your suggestions here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make rating the only required field
        self.fields['rating'].required = True
        self.fields['comments'].required = False
        self.fields['goal_achievement'].required = False
        self.fields['reason'].required = False
        self.fields['issue'].required = False
        self.fields['suggestions'].required = False