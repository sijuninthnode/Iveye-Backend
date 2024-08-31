from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

from .views import (UserRegistrationView, UserProfileView)


urlpatterns = [
    
    #LOGIN
    # Api to login the user through simple-JWT
    path('login/', TokenObtainPairView.as_view(), name='user_login'),
    #Api to get the refresh token
    path('login/refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),

    #To create an accont for the user ie Registration
    path('create/account/', UserRegistrationView.as_view(), name='user_registration'),
    #To get the user profile details
    path('user/profile/details/', UserProfileView.as_view(), name='user_profile_details'),

#Above api checked and written in the Doc
]




