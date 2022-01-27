from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from rest_framework.decorators import api_view
from rest_framework.response import Response

from base.models import Room
from .serializers import RoomSerializer

@api_view(['GET'])
def getRoutes(request):
    '''pass'''
    routes = [
        'GET /api/home',
        'GET /api/rooms',
        'GET /api/room/:id',
    ]

    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    '''pass'''
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    print(serializer)

    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
    '''pass'''
    try:
        room = Room.objects.get(id=pk)
        serializer = RoomSerializer(room, many=False)

        return Response(serializer.data)

    except ObjectDoesNotExist:
        return Response(['ObjectDoesNotExist',])
    except MultipleObjectsReturned:
        return Response(['MultipleObjectsReturned', ])
