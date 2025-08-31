from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pets', views.PetViewSet, basename='pet')
router.register(r'booking-requests', views.BookingRequestViewSet, basename='booking-request')

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Petsitters
    path('petsitters/', views.PetSitterListView.as_view(), name='petsitter-list'),
    
    # Ads
    path('ads/', views.AdListView.as_view(), name='ad-list'),
    
    # Include router URLs
    path('', include(router.urls)),
]
