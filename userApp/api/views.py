from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ..models import UserProfile, Pet, BookingRequest, Ad
from .serializers import (
    UserSerializer, UserProfileSerializer, PetSerializer, 
    BookingRequestSerializer, AdSerializer, LoginSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)
        return Response({
            'token': token.key,
            'user': user_serializer.data
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile

class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own pets
        return Pet.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BookingRequestViewSet(viewsets.ModelViewSet):
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Users can see booking requests they made or received
        return BookingRequest.objects.filter(
            Q(pet_owner=user) | Q(petsitter=user)
        ).select_related('pet_owner', 'petsitter', 'pet')
    
    def perform_create(self, serializer):
        serializer.save(pet_owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        booking = self.get_object()
        if booking.petsitter != request.user:
            return Response(
                {"detail": "You do not have permission to accept this booking."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != 'pending':
            return Response(
                {"detail": f"Cannot accept a booking that is {booking.get_status_display()}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'accepted'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if booking.petsitter != request.user:
            return Response(
                {"detail": "You do not have permission to reject this booking."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != 'pending':
            return Response(
                {"detail": f"Cannot reject a booking that is {booking.get_status_display()}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'rejected'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

class PetSitterListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return all pet sitters with their profiles
        return User.objects.filter(
            role='petsitter',
            profile__is_available=True
        ).select_related('profile')

class AdListView(generics.ListAPIView):
    queryset = Ad.objects.filter(is_active=True)
    serializer_class = AdSerializer
    permission_classes = [permissions.AllowAny]
