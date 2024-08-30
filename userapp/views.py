from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
import random

from .serializers import (UserDetailsSerializer, CustomTokenObtainPairSerializer)
from userapp.models import UserDetails



class UserRegistration(APIView):
    """
    Used to register the user
    fields: first_name, Last_name, password, phone_number.
    """

    def post(self, request):

        #The required fields should not be blank and should check in the fronendend itself.
        data = request.data
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        if UserDetails.objects.filter(email = email). exists():
            return Response({'message' : "An account already exists with this email id"}
                            ,status=status.HTTP_400_BAD_REQUEST)
        if UserDetails.objects.filter(phone_number = phone_number). exists():
            return Response({'message' : "An account already exists with this Phone number"}
                            ,status=status.HTTP_201_CREATED)
        serialised_data = UserDetailsSerializer(data = data)
        if serialised_data.is_valid():
            serialised_data.save()
            return Response({'message' : "Account created successfully"}
                            ,status=status.HTTP_201_CREATED)
        else:
            return Response({'message' : "Please check the entered details", "error" : serialised_data.errors}
                            ,status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    This view is used for authication of the user.
    """

    serializer_class = CustomTokenObtainPairSerializer

#Incomplete : email
class ForgotPasswordEmailRequest(APIView):
    """
    This is used to check whether the user entered email exists
    and also  generate an OTP to the email.
    """
    
    def post(self, request):
        email = request.data.get('email')

        #Confirming that there is an account registred with entred email
        if UserDetails.objects.filter(emai = email). exists():
            
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


class ForgotPasswordEmailConfirmation(APIView):  
    """
    This view is used to change the password 
    if the OTP entered by the user is correct.
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
    This view is used to get profile details of the current logged in  user.
    """

    permission_classes = [IsAuthenticated] 

    def get(self, request):
        try:
            user_data = UserDetails.objects.get(id = request.user.id)
            serialized_data = UserDetailsSerializer(user_data)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except UserDetails.DoesNotExist:
            return Response({'message' : 'User does not exists','error' : serialized_data.errors }, status= status.HTTP_404_NOT_FOUND)
        
