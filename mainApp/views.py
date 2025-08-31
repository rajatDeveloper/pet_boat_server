from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from mainApp.models import PET_CHOICES, Service, SitterService, Ad, Pet, Order
from userApp.models import Address
from datetime import datetime


@api_view(['GET'])
def get_pet_list(request):
    """Return available pet choices as list of {key, label}."""
    pets = [{"key": key, "label": label} for key, label in PET_CHOICES]
    return Response(pets)


@api_view(['GET'])
def get_services_by_pet(request, pet: str):
    """Return list of services for given pet key (e.g., dog, cat)."""
    valid_keys = {k for k, _ in PET_CHOICES}
    if pet not in valid_keys:
        return Response({"error": "Invalid pet"}, status=status.HTTP_400_BAD_REQUEST)

    services = Service.objects.filter(pet=pet).order_by('name')
    data = [
        {
            "id": s.id,
            "name": s.name,
            "pet": s.pet,
            "pet_label": dict(PET_CHOICES).get(s.pet, s.pet),
            "description": s.description,
            "image_url": (s.image.url if s.image else None),
        }
        for s in services
    ]
    return Response(data)

# New: list all services
@api_view(['GET'])
def get_all_services(request):
    services = Service.objects.all().order_by('name')
    data = [
        {
            "id": s.id,
            "name": s.name,
            "pet": s.pet,
            "pet_label": dict(PET_CHOICES).get(s.pet, s.pet),
            "description": s.description,
            "image_url": (s.image.url if s.image else None),
        }
        for s in services
    ]
    return Response(data)

# Create your views here.


# --------- SitterService APIs ---------

def _address_to_dict(addr: Address):
    return {
        "id": addr.id,
        "address": addr.address,
        "city": addr.city,
        "state": addr.state,
        "zipcode": addr.zipcode,
        "latitude": addr.latitude,
        "longitude": addr.longitude,
        "country": addr.country,
    }


def _service_to_dict(svc: Service):
    return {
        "id": svc.id,
        "name": svc.name,
        "pet": svc.pet,
        "pet_label": dict(PET_CHOICES).get(svc.pet, svc.pet),
        "description": svc.description,
        "image_url": (svc.image.url if svc.image else None),
    }


def _user_to_dict(user: User):
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
    profile = getattr(user, "profile", None)
    if profile:
        data["profile"] = {
            "name": profile.name,
            "role": profile.role,
            "phone_number": profile.phone_number,
            "verified": profile.verified,
        }
    return data


def _sitter_service_to_dict(ss: SitterService):
    return {
        "id": ss.id,
        "rate": float(ss.rate),
        "created_at": ss.created_at,
        "updated_at": ss.updated_at,
        "user": _user_to_dict(ss.user),
        "service": _service_to_dict(ss.service),
        "address": _address_to_dict(ss.address),
    }


@api_view(["POST"])
def create_sitter_service(request):
    """Create a SitterService. Body: user_id, service_id, address_id, rate"""
    user_id = request.data.get("user_id")
    service_id = request.data.get("service_id")
    address_id = request.data.get("address_id")
    rate = request.data.get("rate")

    if not all([user_id, service_id, address_id, rate]):
        return Response({"error": "user_id, service_id, address_id, and rate are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
        service = Service.objects.get(id=service_id)
        address = Address.objects.get(id=address_id)
    except (User.DoesNotExist, Service.DoesNotExist, Address.DoesNotExist):
        return Response({"error": "Invalid user_id/service_id/address_id"}, status=status.HTTP_400_BAD_REQUEST)

    # Optional: ensure address belongs to the same user
    if address.user_id != user.id:
        return Response({"error": "address_id does not belong to user_id"}, status=status.HTTP_400_BAD_REQUEST)

    # Optional: ensure user is petsitter
    profile = getattr(user, "profile", None)
    if profile and profile.role != "petsitter":
        return Response({"error": "user must be a petsitter"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rate_val = float(rate)
    except (TypeError, ValueError):
        return Response({"error": "rate must be a number"}, status=status.HTTP_400_BAD_REQUEST)

    ss = SitterService.objects.create(user=user, service=service, address=address, rate=rate_val)
    return Response(_sitter_service_to_dict(ss), status=status.HTTP_201_CREATED)


@api_view(["GET"])
def list_sitter_services_for_user(request, user_id: int):
    """List sitter services for a given user_id with expanded details."""
    services = SitterService.objects.filter(user_id=user_id).select_related("user", "service", "address")
    data = [_sitter_service_to_dict(ss) for ss in services]
    return Response(data)


@api_view(["GET"])
def sitter_service_detail(request, sitter_service_id: int):
    try:
        ss = SitterService.objects.select_related("user", "service", "address").get(id=sitter_service_id)
    except SitterService.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(_sitter_service_to_dict(ss))


# --------- Ad APIs ---------

@api_view(["GET"])
def get_all_ads(request):
    """Return all ads with image_url, punch_line, and url."""
    ads = Ad.objects.all().order_by('-created_at')
    data = [
        {
            "id": ad.id,
            "punch_line": ad.punch_line,
            "url": ad.url,
            "image_url": (ad.image.url if ad.image else None),
            "created_at": ad.created_at,
        }
        for ad in ads
    ]
    return Response(data)


# --------- Pet APIs ---------

@api_view(["POST"])
def create_pet(request):
    """Create a Pet. Body: user_id, name, pet, breed, age, bio, important_info (image via form-data)"""
    user_id = request.data.get("user_id")
    name = request.data.get("name")
    pet_type = request.data.get("pet")
    breed = request.data.get("breed", "")
    age = request.data.get("age")
    bio = request.data.get("bio", "")
    important_info = request.data.get("important_info", "")
    image = request.FILES.get("image")

    if not all([user_id, name, pet_type]):
        return Response({"error": "user_id, name, and pet are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate pet choice
    valid_pets = {k for k, _ in PET_CHOICES}
    if pet_type not in valid_pets:
        return Response({"error": f"Invalid pet type. Valid choices: {list(valid_pets)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Optional: ensure user is normalUser
    profile = getattr(user, "profile", None)
    if profile and profile.role != "normalUser":
        return Response({"error": "Only normal users can create pets"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate age if provided
    if age:
        try:
            age = int(age)
            if age < 0:
                return Response({"error": "Age must be positive"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({"error": "Age must be a number"}, status=status.HTTP_400_BAD_REQUEST)

    pet_obj = Pet.objects.create(
        user=user,
        name=name,
        pet=pet_type,
        breed=breed,
        age=age,
        bio=bio,
        important_info=important_info,
        image=image
    )
    
    return Response(_pet_to_dict(pet_obj), status=status.HTTP_201_CREATED)


@api_view(["GET"])
def list_pets_for_user(request, user_id: int):
    """List all pets for a given user_id."""
    pets = Pet.objects.filter(user_id=user_id).order_by('name')
    data = [_pet_to_dict(pet) for pet in pets]
    return Response(data)


def _pet_to_dict(pet: Pet):
    return {
        "id": pet.id,
        "name": pet.name,
        "pet": pet.pet,
        "pet_label": dict(PET_CHOICES).get(pet.pet, pet.pet),
        "breed": pet.breed,
        "age": pet.age,
        "bio": pet.bio,
        "important_info": pet.important_info,
        "image_url": (pet.image.url if pet.image else None),
        "created_at": pet.created_at,
        "updated_at": pet.updated_at,
        "user": {
            "id": pet.user.id,
            "username": pet.user.username,
            "email": pet.user.email,
        }
    }


# --------- Order APIs ---------

def _address_to_dict(address):
    """Helper function to convert Address object to dict"""
    return {
        "id": address.id,
        "address": address.address,
        "city": address.city,
        "state": address.state,
        "zipcode": address.zipcode,
        "latitude": address.latitude,
        "longitude": address.longitude,
        "country": address.country,
        "created_at": address.created_at,
        "updated_at": address.updated_at,
    }

def _order_to_dict(order: Order):
    return {
        "id": order.id,
        "quantity": order.quantity,
        "final_rate": float(order.final_rate),
        "start_datetime": order.start_datetime,
        "status": order.status,
        "msg_for_user": order.msg_for_user,
        "msg_for_petsitter": order.msg_for_petsitter,
        "rating_for_petsitter": order.rating_for_petsitter,
        "rating_review_for_petsitter": order.rating_review_for_petsitter,
        "rating_for_user": order.rating_for_user,
        "rating_review_for_user": order.rating_review_for_user,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "normal_user": _user_to_dict(order.normal_user),
        "petsitter_user": _user_to_dict(order.petsitter_user),
        "service_model": _sitter_service_to_dict(order.service_model),
        "pet": _pet_to_dict(order.pet) if order.pet else None,
        "user_address": _address_to_dict(order.user_address) if order.user_address else None,
    }


@api_view(["POST"])
def create_order(request):
    """Create order. Body: normal_user_id, petsitter_user_id, service_model_id, pet_id, user_address_id, quantity, start_datetime"""
    normal_user_id = request.data.get("normal_user_id")
    petsitter_user_id = request.data.get("petsitter_user_id")
    service_model_id = request.data.get("service_model_id")
    pet_id = request.data.get("pet_id")
    user_address_id = request.data.get("user_address_id")
    quantity = request.data.get("quantity", 1)
    start_datetime = request.data.get("start_datetime")

    if not all([normal_user_id, petsitter_user_id, service_model_id, pet_id, user_address_id, start_datetime]):
        return Response({"error": "normal_user_id, petsitter_user_id, service_model_id, pet_id, user_address_id, start_datetime are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        normal_user = User.objects.get(id=normal_user_id)
        petsitter_user = User.objects.get(id=petsitter_user_id)
        service_model = SitterService.objects.get(id=service_model_id)
        pet = Pet.objects.get(id=pet_id)
        user_address = Address.objects.get(id=user_address_id)
    except (User.DoesNotExist, SitterService.DoesNotExist, Pet.DoesNotExist, Address.DoesNotExist):
        return Response({"error": "Invalid user, service_model, pet, or address ID"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response({"error": "Quantity must be positive"}, status=status.HTTP_400_BAD_REQUEST)
    except (TypeError, ValueError):
        return Response({"error": "Quantity must be a number"}, status=status.HTTP_400_BAD_REQUEST)

    # Parse start_datetime (ISO format expected)
    try:
        start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
    except ValueError:
        return Response({"error": "Invalid start_datetime format. Use ISO format"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate user roles
    normal_profile = getattr(normal_user, "profile", None)
    petsitter_profile = getattr(petsitter_user, "profile", None)
    
    if normal_profile and normal_profile.role != "normalUser":
        return Response({"error": "normal_user_id must be a normal user"}, status=status.HTTP_400_BAD_REQUEST)
    
    if petsitter_profile and petsitter_profile.role != "petsitter":
        return Response({"error": "petsitter_user_id must be a petsitter"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate pet belongs to normal_user
    if pet.user_id != normal_user.id:
        return Response({"error": "pet_id must belong to normal_user_id"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate address belongs to normal_user
    if user_address.user_id != normal_user.id:
        return Response({"error": "user_address_id must belong to normal_user_id"}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        normal_user=normal_user,
        petsitter_user=petsitter_user,
        service_model=service_model,
        pet=pet,
        user_address=user_address,
        quantity=quantity,
        start_datetime=start_dt
    )
    
    return Response(_order_to_dict(order), status=status.HTTP_201_CREATED)


@api_view(["GET"])
def list_orders_for_user(request, user_id: int):
    """List orders for user_id (as normal user OR petsitter)"""
    from django.db import models
    orders = Order.objects.filter(
        models.Q(normal_user_id=user_id) | models.Q(petsitter_user_id=user_id)
    ).select_related("normal_user", "petsitter_user", "service_model__user", "service_model__service", "service_model__address").order_by('-created_at')
    
    data = [_order_to_dict(order) for order in orders]
    return Response(data)


@api_view(["PATCH"])
def approve_order(request, order_id: int):
    """Petsitter approves order (changes status to approved)"""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    order.status = "approved"
    order.save()
    return Response(_order_to_dict(order))


@api_view(["PATCH"])
def complete_order(request, order_id: int):
    """User marks order as completed"""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    order.status = "completed"
    order.save()
    return Response(_order_to_dict(order))


@api_view(["PATCH"])
def send_message_to_petsitter(request, order_id: int):
    """User sends message to petsitter"""
    message = request.data.get("message")
    if not message:
        return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    order.msg_for_petsitter = message
    order.save()
    return Response(_order_to_dict(order))


@api_view(["PATCH"])
def send_message_to_user(request, order_id: int):
    """Petsitter sends message to user"""
    message = request.data.get("message")
    if not message:
        return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    order.msg_for_user = message
    order.save()
    return Response(_order_to_dict(order))


@api_view(["PATCH"])
def add_review(request, order_id: int):
    """Add review. Body: user_id, review, rating (1-5). Updates order based on user type"""
    user_id = request.data.get("user_id")
    review = request.data.get("review")
    rating = request.data.get("rating")
    
    if not all([user_id, review]):
        return Response({"error": "user_id and review are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate rating if provided
    if rating is not None:
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({"error": "Rating must be a number"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
        user = User.objects.get(id=user_id)
    except (Order.DoesNotExist, User.DoesNotExist):
        return Response({"error": "Order or user not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Determine if user is normal user or petsitter in this order
    if user.id == order.normal_user.id:
        # Normal user reviewing petsitter
        order.rating_review_for_petsitter = review
        if rating is not None:
            order.rating_for_petsitter = rating
    elif user.id == order.petsitter_user.id:
        # Petsitter reviewing normal user
        order.rating_review_for_user = review
        if rating is not None:
            order.rating_for_user = rating
    else:
        return Response({"error": "User not part of this order"}, status=status.HTTP_400_BAD_REQUEST)
    
    order.save()
    return Response(_order_to_dict(order))
