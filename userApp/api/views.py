from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from userApp.api.serializers import RegistrationSerializer, UserSerializer, AddressSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from userApp.models import Address

@api_view(['POST'])
def regisgration_view(request):
    """Registration API
    Fields accepted: name, email, username, role(petsitter|normalUser), phone_number, pan(opt), aadhar(opt), password, password2
    Rule: verified=false for petsitter; true for normalUser
    Auto-login: returns auth token and user data
    """
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        account = serializer.save()
        # Auto-login using created credentials
        user = authenticate(username=account.username, password=request.data.get('password'))
        if user is not None:
            login(request, user)
        token, _ = Token.objects.get_or_create(user=account)

        user_serializer = UserSerializer(account)
        response_data = {
            'token': token.key,
            **user_serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
         
        
@api_view(['POST'])
def logout_view(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_with_email(request):
    """Login using email + password. Returns token and user data."""
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=user_obj.username, password=password)
    if user is not None:
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        response_data = {
            'token': token.key,
            **serializer.data
        }
        return Response(response_data)
    else:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def user_addresses(request, user_id: int):
    """
    GET: return list of addresses for the user_id
    POST: create an address for the user_id from JSON body

    Expected JSON fields: address, city, state, zipcode, latitude, longitude, country
    """
    if request.method == 'GET':
        queryset = Address.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        data = request.data.copy()
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            addr = Address.objects.create(
                user_id=user_id,
                address=serializer.validated_data.get('address', ''),
                city=serializer.validated_data.get('city', ''),
                state=serializer.validated_data.get('state', ''),
                zipcode=serializer.validated_data.get('zipcode', ''),
                latitude=serializer.validated_data.get('latitude', None),
                longitude=serializer.validated_data.get('longitude', None),
                country=serializer.validated_data.get('country', ''),
            )
            return Response(AddressSerializer(addr).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)