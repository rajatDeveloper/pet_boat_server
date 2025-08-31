from django.contrib.auth.models import User
from rest_framework import serializers
from userApp.models import UserProfile, Address


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'name', 'email', 'username', 'role', 'phone_number',
            'pan', 'aadhar', 'verified'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=("petsitter", "normalUser"), required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    pan = serializers.CharField(required=False, allow_blank=True)
    aadhar = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'name', 'role', 'phone_number', 'pan', 'aadhar'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self, **kwargs):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'message': 'Passwords Must Match'})
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'message': 'Email Already Exists'})

        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )
        account.set_password(password)
        account.save()

        # Set profile fields
        profile: UserProfile = account.profile
        profile.name = self.validated_data.get('name', '')
        profile.role = self.validated_data.get('role', 'normalUser')
        profile.phone_number = self.validated_data.get('phone_number', '')
        profile.pan = self.validated_data.get('pan', '')
        profile.aadhar = self.validated_data.get('aadhar', '')
        # verified rule
        profile.verified = False if profile.role == 'petsitter' else True
        profile.save()

        return account


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'address', 'city', 'state', 'zipcode',
            'latitude', 'longitude', 'country', 'created_at', 'updated_at'
        ]
        
        
        
        
    
    
    
        
        
        
    
    