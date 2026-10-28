
import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .restapis import (
    get_request,
    analyze_review_sentiments,
    post_review,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("userName")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse(
            {"userName": username, "status": "Invalid credentials"},
            status=401,
        )

    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})


@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("userName")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=409)

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=data.get("firstName", ""),
        last_name=data.get("lastName", ""),
        email=data.get("email", ""),
    )

    return JsonResponse(
        {"userName": user.username, "status": "Registered"},
        status=201,
    )


def logout_request(request):
    logout(request)
    return JsonResponse({"status": "Logged out"})


def get_dealerships(request, state="all"):
    dealers = get_request(f"fetchDealers/{state}")

    if dealers is None:
        return JsonResponse({"error": "Could not fetch dealerships"}, status=502)

    return JsonResponse(dealers, safe=False)


def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f"fetchReviews/dealer/{dealer_id}")

    if reviews is None:
        return JsonResponse({"error": "Could not fetch reviews"}, status=502)

    return JsonResponse(reviews, safe=False)


def get_dealer_details(request, dealer_id):
    dealer = get_request(f"fetchDealer/{dealer_id}")

    if dealer is None:
        return JsonResponse({"error": "Could not fetch dealership"}, status=502)

    return JsonResponse(dealer)


@csrf_exempt
def add_review(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    required_fields = [
        "name",
        "dealership",
        "review",
        "purchase",
        "purchase_date",
        "car_make",
        "car_model",
        "car_year",
    ]

    missing = [field for field in required_fields if field not in data]
    if missing:
        return JsonResponse(
            {"error": "Missing required fields", "fields": missing},
            status=400,
        )

    sentiment = analyze_review_sentiments(data["review"])
    if sentiment is not None:
        logger.info("Review sentiment analysis completed")

    result = post_review(data)

    if result is None:
        return JsonResponse({"error": "Could not save review"}, status=502)

    return JsonResponse(result, status=201)
x
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
import json
import logging

from .restapis import (
    get_request,
    analyze_review_sentiments,
    post_review,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                "userName": username,
                "status": "Authenticated",
            })

        return JsonResponse({
            "userName": username,
            "status": "Invalid credentials",
        }, status=401)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")
        first_name = data.get("firstName", "")
        last_name = data.get("lastName", "")
        email = data.get("email", "")

        if not username or not password:
            return JsonResponse(
                {"error": "Username and password are required"},
                status=400,
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"error": "Username already exists"},
                status=409,
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        return JsonResponse(
            {"userName": user.username, "status": "Registered"},
            status=201,
        )
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def logout_request(request):
    logout(request)
    return JsonResponse({"status": "Logged out"})


def get_dealerships(request, state="all"):
    dealers = get_request(f"fetchDealers/{state}")
    if dealers is None:
        return JsonResponse(
            {"error": "Could not fetch dealerships"}, status=502
        )
    return JsonResponse(dealers, safe=False)


def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f"fetchReviews/dealer/{dealer_id}")
    if reviews is None:
        return JsonResponse(
            {"error": "Could not fetch reviews"}, status=502
        )
    return JsonResponse(reviews, safe=False)


def get_dealer_details(request, dealer_id):
    dealer = get_request(f"fetchDealer/{dealer_id}")
    if dealer is None:
        return JsonResponse(
            {"error": "Dealership not found"}, status=404
        )
    return JsonResponse(dealer, safe=False)


@csrf_exempt
def add_review(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    review_text = data.get("review", "")
    if review_text:
        sentiment = analyze_review_sentiments(review_text)
        if sentiment is not None:
            data["sentiment"] = sentiment

    result = post_review(data)
    if result is None:
        return JsonResponse(
            {"error": "Could not save review"}, status=502
        )

    return JsonResponse(result, status=201)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
import json
import logging

from .restapis import (
    get_request,
    analyze_review_sentiments,
    post_review,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                "userName": username,
                "status": "Authenticated",
            })

        return JsonResponse({
            "userName": username,
            "status": "Invalid credentials",
        }, status=401)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("userName")
        password = data.get("password")
        first_name = data.get("firstName", "")
        last_name = data.get("lastName", "")
        email = data.get("email", "")

        if not username or not password:
            return JsonResponse(
                {"error": "Username and password are required"},
                status=400,
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"error": "Username already exists"},
                status=409,
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        return JsonResponse(
            {"userName": user.username, "status": "Registered"},
            status=201,
        )
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def logout_request(request):
    logout(request)
    return JsonResponse({"status": "Logged out"})


def get_dealerships(request, state="all"):
    dealers = get_request(f"fetchDealers/{state}")
    if dealers is None:
        return JsonResponse(
            {"error": "Could not fetch dealerships"}, status=502
        )
    return JsonResponse(dealers, safe=False)


def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f"fetchReviews/dealer/{dealer_id}")
    if reviews is None:
        return JsonResponse(
            {"error": "Could not fetch reviews"}, status=502
        )
    return JsonResponse(reviews, safe=False)


def get_dealer_details(request, dealer_id):
    dealer = get_request(f"fetchDealer/{dealer_id}")
    if dealer is None:
        return JsonResponse(
            {"error": "Dealership not found"}, status=404
        )
    return JsonResponse(dealer, safe=False)


@csrf_exempt
def add_review(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    review_text = data.get("review", "")
    if review_text:
        sentiment = analyze_review_sentiments(review_text)
        if sentiment is not None:
            data["sentiment"] = sentiment

    result = post_review(data)
    if result is None:
        return JsonResponse(
            {"error": "Could not save review"}, status=502
        )

    return JsonResponse(result, status=201)
# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
# from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...
