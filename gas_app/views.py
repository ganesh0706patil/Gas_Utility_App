from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Booking, StatusTracking, CustomerSupport, BookingStatus, TrackingStatus

def home(request):
    return render(request, 'gas_app/home.html')

@login_required
def profile(request):
    return render(request, "profile.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')  
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'gas_app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('login')

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use!")
            return redirect('register')

        # Create User with First and Last Name
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password1, 
            first_name=first_name, 
            last_name=last_name
        )
        user.save()

        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'gas_app/register.html')

@login_required
def booking(request):
    if request.method == "POST":
        service_type = request.POST.get('service_type')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')

        if not service_type or not address or not contact_number:
            messages.error(request, "All fields are required.")
            return redirect('booking')

        booking = Booking.objects.create(
            user=request.user,
            service_type=service_type,
            address=address,
            contact_number=contact_number,
            status=BookingStatus.PENDING  # Default status
        )

        tracking_entry, created = StatusTracking.objects.get_or_create(
            booking=booking,
            defaults={
                'status': TrackingStatus.REQUESTED,
                'progress': "Booking request received."
            }
        )

        # Show booking confirmation
        messages.success(request, f"Booking successful! Your Booking ID is {booking.id}")
        return redirect('status')

    return render(request, 'gas_app/booking.html')

@login_required
def status(request):
    """Retrieve and display the user's bookings with status tracking."""
    user_bookings = Booking.objects.filter(user=request.user)

    if not user_bookings.exists():
        messages.info(request, "You have no bookings yet.")
        return render(request, 'gas_app/status.html', {'bookings': []})

    # Fetch status tracking information for each booking
    tracking_entries = StatusTracking.objects.filter(booking__in=user_bookings)
    tracking_info = {tracking.booking.id: tracking for tracking in tracking_entries}

    return render(request, 'gas_app/status.html', {
        'bookings': user_bookings,
        'tracking_info': tracking_info
    })

@login_required
def booking_detail(request, booking_id):
    """View a specific booking's details."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    tracking = StatusTracking.objects.filter(booking=booking).first()

    return render(request, 'gas_app/booking_detail.html', {
        'booking': booking,
        'tracking': tracking
    })

@login_required
def support(request):
    """Allows users to submit support requests and view previous ones."""
    if request.method == "POST":
        issue = request.POST.get('issue')

        if not issue:
            messages.error(request, "Issue description cannot be empty!")
            return redirect('support')

        # Save the support request
        support_ticket = CustomerSupport.objects.create(user=request.user, issue=issue)
        support_ticket.save()
        messages.success(request, "Support request submitted successfully!")
        return redirect('support')

    # Fetch previous support requests
    user_support_tickets = CustomerSupport.objects.filter(user=request.user)

    return render(request, 'gas_app/support.html', {'support_tickets': user_support_tickets})
