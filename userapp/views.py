from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
import random

from .serializers import (UserDetailsSerializer, CustomTokenObtainPairSerializer, UserLearningTopicSerializer,
                           UserCreatedLessonsSerializer)
from userapp.models import (UserDetails, UserLearningTopic, UserCreatedLessons)



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

    permission_classes = [AllowAny]

    def post(self, request):
        # The required fields should not be blank and should be validated on the frontend as well.
        print('In the registration View ')
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
            return Response({'message': 'In valid OTP'}
                            , status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Something when wrong'}
                            , status=status.HTTP_400_BAD_REQUEST)


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


class UserOnBoardingView(APIView):
    """
    This view handles user onboarding by updating user details, including
    their profile image and gender, and saving selected learning topics.

    Methods:
    - POST: Updates user details and saves the selected topics.
    """

    def post(self, request):
        email = request.user.email
        topics = request.data.get('topics')
        image = request.FILES.get('profile_image')
        gender = request.data.get('gender')
        
        # Validate 'topics' to be a list
        if not isinstance(topics, list):
            return Response({'message': 'Invalid topics format, expected a list.'}
                            , status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserDetails.objects.get(email= email)
            if image:
                user.profile_image = image
            if gender:
                user.gender = gender
            user.save()
            for topic in topics:
                UserLearningTopic.objects.create(user = user, topic = topic)
            return Response({'message' : 'Your onboarding has been completed successfully.'}
                        , status=status.HTTP_200_OK)
        except UserDetails.DoesNotExist:
            return Response({'message': 'User data not found',}
                        , status=status.HTTP_404_NOT_FOUND)


class GetUserSpecificTopics(APIView):
    """
    This view retrieves the all the topics selected by the authenticated user.

    Authentication:
    - Requires the user to be authenticated (IsAuthenticated).

    Method:
    - GET: Fetches the topics selected by the user based on their email.
           Returns a success response with the serialized data if found.
           Returns an error response if no topics are found for the user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.user.email
        try:
            data =UserLearningTopic.objects.filter(user__email = email)
            serialized_data = UserLearningTopicSerializer(data, many = True)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except UserLearningTopic.DoesNotExist:
            return Response({"message": "No topics found for the user"}
                            , status=status.HTTP_404_NOT_FOUND)


class DeleteUserTopicsView(APIView):
    """
    This view allows a user to delete a topic they choosed to learn.

    Authentication:
    - Requires the user to be authenticated (IsAuthenticated).
    
    Method:
    - PATCH: Deletes the topic with the given `topic_id` if it exists.
             Returns a success message if the topic is deleted.
             Returns an error message if the topic does not exist.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, topic_id):
        try:
            topic = UserLearningTopic.objects.get(id=topic_id)
            topic.delete()
            return Response({'message': 'Topic deleted successfully'}
                            , status=status.HTTP_200_OK)
        except UserLearningTopic.DoesNotExist:
            return Response({"message": "Action can't be completed"}
                            , status=status.HTTP_400_BAD_REQUEST)


class UpdateUserProfileView(APIView):
    """
    This view allows an authenticated user to update their profile information.

    Authentication:
    - Requires the user to be authenticated (IsAuthenticated).

    Method:
    - PATCH: Updates the user's profile with the provided data.
             Returns a success message if the profile is updated.
             Returns an error message if the update fails due to invalid data.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        email = request.user.email
        try:
            user = UserDetails.objects.get(email=email)
            serializer = UserDetailsSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()  
                return Response({'message': 'Your profile was updated successfully'}
                                , status=status.HTTP_200_OK)
            return Response({"message": "Profile update failed", 'errors': serializer.errors}
                            , status=status.HTTP_400_BAD_REQUEST)
        except UserDetails.DoesNotExist:
            return Response({"message": "User not found"}
                            , status=status.HTTP_404_NOT_FOUND)
        

class UserAddYourOwnLessonView(APIView):
    """
    This view allows a user to create, add, and delete custom lessons.

    Authentication:
    - Requires the user to be authenticated (IsAuthenticated).

    Methods:
    - POST: 
        - Description: Creates a new custom lesson for the authenticated user.
        - Request Data: 
            - `lesson_name` (str): The name of the lesson the user wants to create.
        - Responses:
            - 201 Created: Returns a success message if the lesson is successfully created.
            - 404 Not Found: Returns an error message if the user is not found.

    - DELETE: 
        - Description: Deletes a custom lesson created by the user.
        - Path Parameter: 
            - `user_lesson_id` (int): The ID of the lesson to be deleted.
        - Responses:
            - 200 OK: Returns a success message if the lesson is successfully deleted.
            - 400 Bad Request: Returns an error message if the lesson is not found or the deletion cannot be completed.
    """
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.user.email
        lesson = request.data.get('lesson_name')
        try:
            user = UserDetails.objects.get(email=email)
            UserCreatedLessons.objects.create(user= user, lesson_name=lesson)
            return Response({'message': 'Your custom lesson added successfully'}
                                , status=status.HTTP_201_CREATED)
        except UserDetails.DoesNotExist:
            return Response({"message": "User not found"}
                            , status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, user_lesson_id):
        try:
            UserCreatedLessons.objects.get(id = user_lesson_id).delete()
            return Response({'message': 'Your custom lesson deleted successfully'}
                                , status=status.HTTP_200_OK)
        except UserCreatedLessons.DoesNotExist: 
            return Response({"message": "Action can't be completed"}
                            , status=status.HTTP_400_BAD_REQUEST)

        
class GetAllUserSpecificCustomLesson(APIView):
    """
    This view retrieves all custom lessons created by the authenticated user.

    Authentication:
    - Requires the user to be authenticated (IsAuthenticated).

    Methods:
    - GET: Fetches and returns a list of all custom lessons created by the user.
           Returns a 404 error if the user is not found.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.user.email
        try:
            data =UserCreatedLessons.objects.filter(user__email = email)
            serializer = UserCreatedLessonsSerializer(data, many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserCreatedLessons.DoesNotExist:
            return Response({"message": "User not found"}
                            , status=status.HTTP_404_NOT_FOUND)
        

         
        




