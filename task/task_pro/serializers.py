from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name', 'category', 'mobile_num', 'email', 'location', 'age', 'gender']
