from rest_framework.response import Response
from rest_framework.views import APIView
from alarms.models import Alarm
from rest_framework import status, permissions
from alarms.serializers import AlarmSerializer


class AlarmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if Alarm.objects.filter(target_user=request.user, db_status=1):
            return Response({"unread": True}, status=status.HTTP_200_OK)
        else:
            return Response({"unread": False}, status=status.HTTP_200_OK)


class AlarmDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        usread_alarms = Alarm.objects.filter(target_user=request.user, db_status=1)
        all_alarms = Alarm.objects.all().order_by("-created_at")
        serializer_data = AlarmSerializer(all_alarms, many=True).data
        for a in usread_alarms:
            a.db_status = 2
            a.save()
        return Response(serializer_data, status=status.HTTP_200_OK)
