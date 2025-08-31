from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import UserProfile, Pet, BookingRequest, Ad

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'aadhar_number', 'role', 'password', 'profile')
        extra_kwargs = {
            'password': {'write_only': True},
            'aadhar_number': {'required': True}
        }
    
    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            return None
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            aadhar_number=validated_data['aadhar_number'],
            role=validated_data.get('role', 'normal'),
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'bio', 'rate_per_night', 
                 'rate_per_day', 'currency', 'is_available', 'latitude', 'longitude')
        extra_kwargs = {
            'rate_per_night': {'required': False},
            'rate_per_day': {'required': False},
            'currency': {'required': False},
        }

class PetSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Pet
        fields = ('id', 'name', 'pet_type', 'breed', 'age', 'weight', 
                 'special_instructions', 'image', 'created_at', 'owner')
        read_only_fields = ('created_at',)
        extra_kwargs = {
            'image': {'required': False}
        }
    
    def create(self, validated_data):
        # Set the owner to the current user
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class BookingRequestSerializer(serializers.ModelSerializer):
    pet_owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    petsitter = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='petsitter'))
    pet = serializers.PrimaryKeyRelatedField(queryset=Pet.objects.all())
    
    class Meta:
        model = BookingRequest
        fields = ('id', 'pet_owner', 'petsitter', 'pet', 'start_date', 'end_date', 
                 'status', 'created_at', 'updated_at')
        read_only_fields = ('status', 'created_at', 'updated_at')
    
    def validate(self, data):
        # Ensure end date is after start date
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        
        # Ensure the pet belongs to the user making the request
        if self.context['request'].method == 'POST':
            pet_owner = self.context['request'].user
            if data['pet'].owner != pet_owner:
                raise serializers.ValidationError("You can only book your own pets.")
            
            # Check for overlapping bookings for the same pet
            overlapping = BookingRequest.objects.filter(
                pet=data['pet'],
                start_date__lte=data['end_date'],
                end_date__gte=data['start_date'],
                status__in=['pending', 'accepted']
            ).exists()
            
            if overlapping:
                raise serializers.ValidationError("This pet already has a booking for the selected dates.")
        
        return data

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('id', 'title', 'description', 'image', 'link', 'is_active', 'created_at')
        read_only_fields = ('created_at',)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
