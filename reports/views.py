from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from users.models import User
from reports.serializers import ReportUserSerializer,ReportArticleSerializer,ReportCommentSerializer

# Create your views here.
class ReportView(APIView):
    '''신고 접수'''

    def report_user(self, request):
        serializer = ReportUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=1)
            print("save")
            status_is=status.HTTP_200_OK
            message_is={"message": "저장완료"}
        else:
            status_is=status.HTTP_400_BAD_REQUEST
            message_is=serializer.errors
        return message_is,status_is
    
    def report_article(self, request):
        serializer = ReportArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=1)
            print("save")
            status_is=status.HTTP_200_OK
            message_is={"message": "저장완료"}
        else:
            status_is=status.HTTP_400_BAD_REQUEST
            message_is=serializer.errors
        return message_is,status_is
    
    def report_comment(self, request):
        serializer = ReportCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=1)
            print("save")
            status_is=status.HTTP_200_OK
            message_is={"message": "저장완료"}
        else:
            status_is=status.HTTP_400_BAD_REQUEST
            message_is=serializer.errors
        return message_is,status_is
    
    def fail(self, request):
        status_is=status.HTTP_400_BAD_REQUEST
        message_is={"message": "신고유형이 잘못되었습니다."}
        return message_is,status_is
    
    request_dic={"user":report_user,
                 "article":report_article,
                 "comment":report_comment,
                 "fail":fail,
                 }


    def post(self, request):
        request_type=request.data.get('request_type')
        message_is,status_is=self.request_dic.get(request_type,self.request_dic["fail"])(self, request)
        return Response(message_is, status=status_is)
