from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from .models import UserAuthenticationRegistration  # Updated import to use UserAuthenticationRegistration
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    login_input = credentials.get('username')  # This is the form input (username or email)
    user = None
    email = None

    # Try to get user by username
    try:
        user = User.objects.get(username=login_input)
        email = user.email  # Assign the user's email
    except User.DoesNotExist:
        # Try to get user by email
        try:
            user = User.objects.get(email=login_input)
            email = login_input  # Assign the input email
        except User.DoesNotExist:
            user = None
            email = login_input  # Save the entered input as email if no user is found

    print(f"[DEBUG] Login Input: {login_input}")
    print(f"[DEBUG] User Found: {user}")
    print(f"[DEBUG] Email to Save: {email}")

    UserAuthenticationRegistration.objects.create(
        user=user,  # Save the user object (username if found)
        email=email,  # Save the email address or input
        action="Invalid username/email or password"
    )