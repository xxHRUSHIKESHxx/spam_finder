from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import User, Contact
from .serializers import UserSerializer, ContactSerializer , MarkAsSpamSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    """
    print(request.data)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # Hashing the password 
        password = make_password(serializer.validated_data['password'])
        serializer.validated_data['password'] = password

        # Saveing the user instance
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken:
    """
    Obtain authentication token.
    """
    @staticmethod
    def get_token(user):
        # Get or create token for user
        token, created = Token.objects.get_or_create(user=user)
        return token.key


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticateing user using username and password.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    # Checking if both username and password are provided
    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticateing user
    user = authenticate(request, username=username, password=password)
    user_id = user.id

    print("user after authenticatiaon" , user_id)
    # If authentication was successful
    if user is not None:
        # User is authenticated
        # Obtaining authentication token using CustomAuthToken class
        token = CustomAuthToken.get_token(user)
        return Response({'token': token , 'user_id':user_id })
    else:
        # Authentication failed
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def contact_list_create(request):
    """
    Listing or createing contacts for the authenticated user.
    """
    print("user from contact creation", request.user)
    
    if request.method == 'GET':
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        phone_number = request.data.get('phone_number')
        
        # Checking if contact already exists for the user
        if Contact.objects.filter(user=request.user, phone_number=phone_number).exists():
            return Response({'error': 'Contact already exists if you want to modify somthing then go the contact_details api end point.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ContactSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def contact_detail(request, pk):
    """
    Retrieve, update, or deleteing a contact.
    """
    try:
        print('request obkect ' , pk , request.user)
        contact = Contact.objects.get(pk=pk, user=request.user)
        print("contact" , contact)
    except Contact.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ContactSerializer(contact, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contact_detail_public(request, pk):
    """
    Retrieveing public details of a contact.
    """
    try:
        contact = Contact.objects.get(pk=pk)
    except Contact.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ContactSerializer(contact, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_by_name(request, name):
    """
    Searching contacts by name.
    """
    contacts = Contact.objects.filter(name__icontains=name)
    serializer = ContactSerializer(contacts, many=True ,  context={'request': request})
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_by_phone_number(request, phone_number):
    """
    Searching contacts by phone number.
    """
    # Checking if there's a user with the given phone number
    user_with_phone = User.objects.filter(phone_number=phone_number).first()
    
    if user_with_phone:
        # If a user exists with the given phone number, return their username
        response_data = {'name': user_with_phone.username}
        
        # Retrieve contacts associated with the phone number
        contacts = Contact.objects.filter(phone_number=phone_number)
        serializer = ContactSerializer(contacts, many=True, context={'request': request})
        
        # Serialize contacts data
        serialized_data = serializer.data
        
        # Modifying response data to include only name and spam likelihood
        response_data['spam_rating'] = [{'spam_likelihood': serialized_data[0]['spam_likelihood']}]
        
        return Response(response_data)
    else:
        # If no user exists with the given phone number, retrieve contacts from the Contact table
        contacts = Contact.objects.filter(phone_number=phone_number)
        serializer = ContactSerializer(contacts, many=True, context={'request': request})
        serialized_data = serializer.data
        return Response(serialized_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_spam(request):
    """
    Mark a number as spam.
    """
    phone_number = request.data.get('phone_number')

    # Check if the phone number is provided
    if not phone_number:
        return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Mark the provided number as spam
    contact_data = {
        'phone_number': phone_number,
        'is_spam': True,
        'user': request.user.id  # Assuming the user is authenticated
    }

    # Pass the user_id explicitly to the serializer
    serializer = MarkAsSpamSerializer(data=contact_data, context={'user_id': request.user.id})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


