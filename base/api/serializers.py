from rest_framework.serializers import ModelSerializer
from base.models import Room

class RoomSerializer(ModelSerializer):
    '''pass'''
    class Meta:
        model = Room
        fields = '__all__'

