from rest_framework import serializers
from .models import Label

class LableSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'