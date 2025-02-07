import googlemaps
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, UserActivityForm, GreenActionSimulatorForm, ObservationForm, CustomAuthenticationForm
from .utils import calculate_carbon_footprint, calculate_sustainability_score
from .models import UserActivity, UserProfile, SustainabilityScore, EnvironmentalObservation

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

# Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('home')  # Redirect to homepage
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to homepage
        else:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

# Home View (Protected by @login_required)
@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')

# Carbon Footprint Tracker View
@login_required
def track_carbon_footprint(request):
    if request.method == 'POST':
        form = UserActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()

            # Calculate carbon footprint
            user_input = f"Transportation: {activity.transportation}, Diet: {activity.diet}, Energy Usage: {activity.energy_usage}"
            try:
                footprint = calculate_carbon_footprint(user_input)
            except ValueError as e:
                return render(request, 'error.html', {'message': str(e)})
            
            return render(request, 'carbon_result.html', {'footprint': footprint})
    else:
        form = UserActivityForm()
    return render(request, 'track_carbon.html', {'form': form})


@login_required
def calculate_sustainability(request):
    """
    View to calculate the user's sustainability score using Gemini API.
    """
    user_activities = UserActivity.objects.filter(user=request.user)
    result = calculate_sustainability_score(user_activities)

    return render(request, 'sustainability_score.html', {'result': result})


@login_required
def submit_observation(request):
    if request.method == 'POST':
        form = ObservationForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the location from the form
            location = form.cleaned_data['location']

            # Use Google Maps Geocoding API to get latitude and longitude
            geocode_result = gmaps.geocode(location)
            if not geocode_result:
                return render(request, 'error.html', {'message': 'Invalid location. Please enter a valid address.'})

            # Extract latitude and longitude
            latitude = geocode_result[0]['geometry']['location']['lat']
            longitude = geocode_result[0]['geometry']['location']['lng']

            # Save the observation
            observation = form.save(commit=False)
            observation.user = request.user
            observation.latitude = latitude
            observation.longitude = longitude
            observation.save()

            return redirect('map_view')
    else:
        form = ObservationForm()
    return render(request, 'submit_observation.html', {'form': form})

@login_required
def map_view(request):
    observations = EnvironmentalObservation.objects.all()
    # Serialize observations to JSON
    observations_json = serialize('json', observations, fields=('latitude', 'longitude', 'observation_type'))
    return render(request, 'map.html', {'observations': observations_json})

@login_required
def all_observations(request):
    """
    Displays a paginated list of all environmental observations submitted by users.
    Supports filtering by observation type.
    """
    # Fetch all observations
    observations = EnvironmentalObservation.objects.all().order_by('-timestamp')

    # Optional: Filter by observation type
    observation_type = request.GET.get('type', None)
    if observation_type:
        observations = observations.filter(observation_type=observation_type)

    # Paginate the results (10 observations per page)
    paginator = Paginator(observations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'all_observations.html', {'page_obj': page_obj})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')