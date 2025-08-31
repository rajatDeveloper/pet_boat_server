# Pet Boat Server API Documentation

A Django REST API for a pet sitting service platform connecting pet owners with pet sitters.

## Setup

1. Install dependencies:
```bash
pip install django djangorestframework django-cors-headers pillow django-filter
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create superuser (optional):
```bash
python manage.py createsuperuser
```

4. Start server:
```bash
python manage.py runserver
```

## Base URL
```
http://127.0.0.1:8000
```

---

# API Endpoints

## User Management (`/api/user/`)

### Authentication

#### Register User
- **POST** `/api/user/register/`
- **Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "role": "normalUser",
  "phone_number": "1234567890"
}
```

#### Login with Email
- **POST** `/api/user/login-email/`
- **Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```
- **Response:**
```json
{
  "token": "auth_token_here",
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

### Address Management

#### Create Address
- **POST** `/api/user/users/<user_id>/addresses/`
- **Body:**
```json
{
  "address": "221B Baker Street",
  "city": "London",
  "state": "London",
  "zipcode": "NW1 6XE",
  "latitude": 51.52377,
  "longitude": -0.15856,
  "country": "UK"
}
```

#### List User Addresses
- **GET** `/api/user/users/<user_id>/addresses/`

---

## Main App (`/api/main/`)

### Pet Types & Services

#### Get Pet Types
- **GET** `/api/main/pets/`
- **Response:**
```json
[
  {"key": "cat", "label": "Cat"},
  {"key": "dog", "label": "Dog"},
  {"key": "bird", "label": "Bird"},
  {"key": "fish", "label": "Fish"},
  {"key": "rabbit", "label": "Rabbit"},
  {"key": "other", "label": "Other"}
]
```

#### Get All Services
- **GET** `/api/main/services/`

#### Get Services by Pet Type
- **GET** `/api/main/pets/<pet_type>/services/`
- **Example:** `/api/main/pets/dog/services/`

### Sitter Services

#### Create Sitter Service
- **POST** `/api/main/sitter-services/`
- **Body:**
```json
{
  "user_id": 5,
  "service_id": 2,
  "address_id": 7,
  "rate": 499.99
}
```

#### List Sitter Services for User
- **GET** `/api/main/users/<user_id>/sitter-services/`

#### Get Sitter Service Details
- **GET** `/api/main/sitter-services/<sitter_service_id>/`

### Pet Management

#### Create Pet
- **POST** `/api/main/pets/create/`
- **Content-Type:** `multipart/form-data`
- **Body:**
```
user_id: 2
name: "Buddy"
pet: "dog"
breed: "Golden Retriever"
age: 3
bio: "Friendly and energetic"
important_info: "Allergic to chicken"
image: [file upload]
```

#### List User's Pets
- **GET** `/api/main/users/<user_id>/pets/`

### Order Management

#### Create Order
- **POST** `/api/main/orders/`
- **Body:**
```json
{
  "normal_user_id": 2,
  "petsitter_user_id": 5,
  "service_model_id": 3,
  "pet_id": 7,
  "user_address_id": 1,
  "quantity": 2,
  "start_datetime": "2025-09-01T10:00:00"
}
```

#### List Orders for User
- **GET** `/api/main/users/<user_id>/orders/`
- Returns orders where user is either customer or petsitter

#### Approve Order (Petsitter)
- **PATCH** `/api/main/orders/<order_id>/approve/`

#### Complete Order (Customer)
- **PATCH** `/api/main/orders/<order_id>/complete/`

#### Send Message to Petsitter
- **PATCH** `/api/main/orders/<order_id>/message-to-petsitter/`
- **Body:**
```json
{
  "message": "My dog is very friendly!"
}
```

#### Send Message to User
- **PATCH** `/api/main/orders/<order_id>/message-to-user/`
- **Body:**
```json
{
  "message": "I'll take great care of your pet!"
}
```

#### Add Review & Rating
- **PATCH** `/api/main/orders/<order_id>/review/`
- **Body:**
```json
{
  "user_id": 2,
  "review": "Great service! Very professional and caring",
  "rating": 5
}
```
- **Note:** Rating is optional (1-5 scale). Review text is required.

### Advertisements

#### Get All Ads
- **GET** `/api/main/ads/`
- **Response:**
```json
[
  {
    "id": 1,
    "punch_line": "Best Pet Care Service!",
    "url": "https://example.com",
    "image_url": "/media/ads/ad1.jpg",
    "created_at": "2025-08-31T10:00:00Z"
  }
]
```

---

# Data Models

## User Roles
- `normalUser`: Pet owners who book services
- `petsitter`: Service providers who offer pet care

## Order Status
- `pending`: Default status when order is created
- `approved`: Petsitter has accepted the order
- `completed`: Service has been completed
- `cancelled`: Order was cancelled

## Pet Types
- `cat`, `dog`, `bird`, `fish`, `rabbit`, `other`

---

# Response Format

All API responses follow this structure:

**Success Response:**
```json
{
  "data": "response_data_here"
}
```

**Error Response:**
```json
{
  "error": "Error message here"
}
```

---

# Authentication

Most endpoints require authentication using Token-based authentication:

**Header:**
```
Authorization: Token your_auth_token_here
```

---

# Admin Interface

Access the Django admin at `/admin/` to manage:
- Users and User Profiles
- Services (with image upload)
- Sitter Services
- Pets (with image upload)
- Orders (with status tracking, ratings, and reviews)
- Addresses
- Ads (with image upload)

---

# File Uploads

The API supports image uploads for:
- **Services**: `/media/services/`
- **Pets**: `/media/pets/`
- **Ads**: `/media/ads/`

Images are served at `/media/<folder>/<filename>`

---

# Example Workflow

1. **User Registration:**
   - Normal user registers: `POST /api/user/register/`
   - Petsitter registers: `POST /api/user/register/` (with role: "petsitter")

2. **Setup:**
   - User adds address: `POST /api/user/users/<id>/addresses/`
   - Normal user adds pets: `POST /api/main/pets/create/`
   - Petsitter creates services: `POST /api/main/sitter-services/`

3. **Booking:**
   - Normal user creates order: `POST /api/main/orders/`
   - Petsitter approves: `PATCH /api/main/orders/<id>/approve/`
   - Service completion: `PATCH /api/main/orders/<id>/complete/`
   - Reviews: `PATCH /api/main/orders/<id>/review/`

4. **Communication:**
   - Messages between users: `PATCH /api/main/orders/<id>/message-to-*`

---

# Error Codes

- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Authentication required
- `404`: Not Found - Resource doesn't exist
- `500`: Internal Server Error

---

# Notes

- All datetime fields use ISO format: `YYYY-MM-DDTHH:MM:SS`
- File uploads use `multipart/form-data`
- JSON requests use `application/json`
- All responses include expanded related object details
- Order final_rate is auto-calculated: `service_rate × quantity`
- Rating system: 1-5 stars for both users and petsitters
- User addresses are required for order creation and service delivery
