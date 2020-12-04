import rest_framework
from rest_framework import generics, status as rest_framework_status
from rest_framework.views import APIView
from rest_framework.response import Response


from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room


class RoomView(generics.ListAPIView):
    """Path : /api/room"""

    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class CreateRoomView(APIView):
    """Path : /api/create-room"""

    serializer_class = CreateRoomSerializer

    def post(self, request: rest_framework.request.Request, format=None) -> Response:
        """
        Create new room or update existing one
        """

        if not self.request.session.exists(self.request.session.session_key):
            print("Create new session key")

            # User has no active session
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            # If required fields are presented in json and valid

            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key

            queryset = Room.objects.filter(host=host)

            if queryset.exists():
                # Room already exists
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip

                # save updated
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])

            else:

                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                room.save()

            jsonified_room: rest_framework.utils.serializer_helpers.ReturnDict = RoomSerializer(room).data

            # Return response with serialized Room object
            return Response(jsonified_room, status=rest_framework_status.HTTP_200_OK)

        # invalid data were provided
        return Response("Bad data. Very-very bad.", status=rest_framework_status.HTTP_400_BAD_REQUEST)
