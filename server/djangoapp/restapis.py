
import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    "backend_url", "http://localhost:3030"
).rstrip("/")

sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url", "http://localhost:5050/"
).rstrip("/") + "/"

def get_request(endpoint, **kwargs):
    try:
        response = requests.get(
            f"{backend_url}/{endpoint.lstrip('/')}",
            params=kwargs,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as error:
        print(f"GET request failed: {error}")
    return None

def analyze_review_sentiments(text):
    try:
        url = sentiment_analyzer_url + "analyze/" + quote(text, safe="")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as error:
        print(f"Sentiment analysis failed: {error}")
    return None

def post_review(data_dict):
    try:
        response = requests.post(
            f"{backend_url}/insert_review",
            json=data_dict,
            timeout=10,
        )
        if response.status_code in (200, 201):
            return response.json()
        print(f"POST review failed: HTTP {response.status_code}")
    except requests.RequestException as error:
        print(f"POST review failed: {error}")
    return None

import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

backend_url = os.getenv(
    "backend_url", "http://localhost:3030"
)
sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url", "http://localhost:5050/"
)


def get_request(endpoint, **kwargs):
    try:
        response = requests.get(
            backend_url + endpoint, params=kwargs
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        print(f"GET request failed: {e}")
    return None


def analyze_review_sentiments(text):
    try:
        request_url = sentiment_analyzer_url + "analyze/" + quote(text, safe="")
        response = requests.get(request_url)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        print(f"Sentiment analysis failed: {e}")
    return None


def post_review(data_dict):
    try:
        response = requests.post(
            backend_url + "/insert_review",
            json=data_dict
        )
        if response.status_code in (200, 201):
            return response.json()
    except requests.RequestException as e:
        print(f"POST request failed: {e}")
    return None
# Uncomment the imports below before you add the function code
# import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# def get_request(endpoint, **kwargs):
# Add code for get requests to back end

# def analyze_review_sentiments(text):
# request_url = sentiment_analyzer_url+"analyze/"+text
# Add code for retrieving sentiments

# def post_review(data_dict):
# Add code for posting review
