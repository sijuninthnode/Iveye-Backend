from django.contrib import admin

from .models import UserDetails, UserLearningTopic

admin.site.register(UserDetails)
admin.site.register(UserLearningTopic)