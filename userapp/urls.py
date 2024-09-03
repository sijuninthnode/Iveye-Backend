from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

from .views import (UserRegistrationView, UserProfileView, UserOnBoardingView, DeleteUserTopicsView, GetUserSpecificTopics,
                    UpdateUserProfileView, UserAddYourOwnLessonView, GetAllUserSpecificCustomLesson)


urlpatterns = [

    #REGISTRATION
    # To create an account for the user (Registration)
    path('create/account', UserRegistrationView.as_view(), name='user_registration'),

    # LOGIN
    # API to refresh the JWT token
    path('login/refresh-token', TokenRefreshView.as_view(), name='token_refresh'),
    # API to log in the user using simple-JWT
    path('login', TokenObtainPairView.as_view(), name='user_login'),


    # TOPICS
    # API to retrieve all the learning topics selected by the user 
    path('retrieve/specific-user-all-learning-topics', GetUserSpecificTopics.as_view(), name='user_specific_topic'),
    # API to delete a specific learning topic selected by the user
    path('delete/user-learning-topic/<topic_id>', DeleteUserTopicsView.as_view(), name='delete_user_topic'),
    # To update user details during onboarding, including profile image and gender
    path('user/onboarding-details', UserOnBoardingView.as_view(), name='user_onboarding'),

    #PROFILE
    # API to allow authenticated users to update their profile information
    path('update/user-profile', UpdateUserProfileView.as_view(), name='user_profile_updation'),
    # API to get the user's profile details
    path('user/profile/details', UserProfileView.as_view(), name='user_profile_details'),


    

    #CUSTOM USER LESSON
    # To create a custom lesson for the user
    path('user/add-custom-lesson', UserAddYourOwnLessonView.as_view(), name='user_add_custom_lesson'),
    # To delete a specific custom lesson created by the user
    path('user/delete-custom-lesson/<user_lesson_id>', UserAddYourOwnLessonView.as_view(), name='user_delete_custom_lesson'),
    # To get all custom lessons created by a specific user
    path('user/get-custom-lessons', GetAllUserSpecificCustomLesson.as_view(), name='get_custom_lessons_of_user'),
 

    #Above api checked and written in the Doc



]




