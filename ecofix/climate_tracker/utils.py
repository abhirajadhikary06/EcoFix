# climate_tracker/utils.py
import google.generativeai as genai
from google.cloud import aiplatform
from django.conf import settings  # To use Django settings for API keys
from .forms import UserActivityForm, GreenActionSimulatorForm

# Configure Gemini API
def configure_gemini():
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        raise ConnectionError(f"Failed to configure Gemini API: {e}")

model = configure_gemini()

def calculate_carbon_footprint(user_input):
    """
    Uses Google Gemini API to calculate carbon footprint based on user input.
    """
    try:
        prompt = f"Calculate the carbon footprint for the following activities: {user_input}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise ValueError(f"Error calculating carbon footprint: {e}")

    
def calculate_sustainability_score(user_activities):
    """
    Uses Google Gemini API to calculate the sustainability score based on user activities.
    """
    # Prepare input for Gemini API
    activity_summary = "\n".join([
        f"Transportation: {activity.transportation}, Diet: {activity.diet}, Energy Usage: {activity.energy_usage}"
        for activity in user_activities
    ])
    prompt = (
        f"Calculate a sustainability score (0-100) for the following activities:\n{activity_summary}\n"
        "Provide a detailed breakdown of the score and suggestions for improvement."
    )

    # Generate response using Gemini API
    response = model.generate_content(prompt)
    return response.text

