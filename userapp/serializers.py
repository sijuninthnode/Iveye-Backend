from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from userapp.models import UserDetails


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """To include the email in the token 
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        if user.email:
            token['email'] = user.email
        return token


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = '__all__'
        # exclude = ['password']

    def create(self, validated_data):
        return UserDetails.objects.create_user(**validated_data)