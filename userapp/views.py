from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
import random

from .serializers import (UserDetailsSerializer, CustomTokenObtainPairSerializer)
from userapp.models import UserDetails



class UserRegistrationView(APIView):
    """
    This view handles user registration.

    Fields:
    - first_name: The first name of the user.
    - last_name: The last name of the user.
    - password: The user's password.
    - phone_number: The user's phone number.
    - email: The user's email address (should be unique).

    Functionality:
    - Validates that the required fields are provided and not left blank.
    - Checks if an account already exists with the provided email or phone number.
    - If validation passes, creates a new user account and returns a success message.
    - Returns appropriate error messages if validation fails or if an account already exists.
    """

    def post(self, request):
        # The required fields should not be blank and should be validated on the frontend as well.
        data = request.data
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')

        # Check if a user with the same email already exists
        if UserDetails.objects.filter(email=email).exists():
            return Response({'message': "An account already exists with this email id"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Check if a user with the same phone number already exists
        if UserDetails.objects.filter(phone_number=phone_number).exists():
            return Response({'message': "An account already exists with this phone number"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Serialize and validate the provided data
        serialized_data = UserDetailsSerializer(data=data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response({'message': "Account created successfully"},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'message': "Please check the entered details", "errors": serialized_data.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    This view is used for user authentication by obtaining a pair of JWT tokens (access and refresh).

    It leverages a custom serializer, `CustomTokenObtainPairSerializer`, to handle the token creation process.

    Methods:
    - POST: Authenticates the user with provided credentials and returns a pair of JWT tokens (access and refresh) if successful.
    """

    serializer_class = CustomTokenObtainPairSerializer


#Incomplete : email
class ForgotPasswordEmailRequestView(APIView):
    """
    This is used to check whether the user entered email exists
    and also  generate an OTP to the email.
    """
    
    def post(self, request):
        email = request.data.get('email')

        #Confirming that there is an account registred with entred email
        if UserDetails.objects.filter(email = email). exists():
            
            #activating the email smtp to generate the OTP
            #1.Storing the OTP as a Data in DB
            #2.UsingFirebase to generate OTP

            #1. Manual
            otp = random.randint(10001, 9999)
            UserDetails.objects.filter(email=email).update(otp=otp)
            #activating the SMTP by sending the OTP saved in the DB

            return Response({'message': 'OTP sent successfully to your email'}
                            , status=status.HTTP_200_OK)
        else :
            return Response({'message': 'Email does not exists. Enter a vaild email id.'}
                            , status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordEmailConfirmationView(APIView):  
    """
    This view is used to change the password if the OTP entered by the user is correct.
    Methods:
    - Post

    """

    def post(self, request):
        email = request.user.email
        new_password = request.data.get('new_password')
        try :
            user = UserDetails.objects.get(email=email,otp=otp)
            user.set_password(new_password)
            user.save()
            otp = random.randint(1001,9999)
            UserDetails.objects.filter(email=email).update(otp=otp)
            return Response({'message' : 'Password changed successfully'
                            },
                            status=status.HTTP_200_OK)
        except UserDetails.DoesNotExist:
            return Response({'message': 'In valid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Something when wrong'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    This view is used to retrieve the profile details of the currently logged-in user.

    Authentication:
    - Requires the user to be authenticated (IsAuthenticated).

    Methods:
    - GET: Fetches the profile details of the authenticated user. Returns a 200 OK status with the user's data if found.
    - If the user does not exist, returns a 404 Not Found status with an error message.
    """

    permission_classes = [IsAuthenticated] 

    def get(self, request):
        try:
            user_data = UserDetails.objects.get(id=request.user.id)
            serialized_data = UserDetailsSerializer(user_data)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except UserDetails.DoesNotExist:
            return Response({'message': 'User does not exist', 'error': 'User data not found'}
                            , status=status.HTTP_404_NOT_FOUND)

  


class UserLeariningTopicCreationView(APIView):
        
        def get(self, request):
            pass