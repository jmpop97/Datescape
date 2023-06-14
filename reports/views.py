from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from users.models import User
from reports.models import ParentCategory, ChildCategory
from reports.serializers import (
    ReportUserSerializer,
    ReportArticleSerializer,
    ReportCommentSerializer,
)


# Create your views here.
class ReportView(APIView):
    """신고 접수
    input
        request_type:   "user" -유저
                        "article" - 게시글
                        "comment" - 댓글
        "report_id":    int - 행당 id값
    output
        해당 report DB에 저장
    """

    def report_user(self, request):
        """request_type:   "user" """
        serializer = ReportUserSerializer(data=request.data)
        print(request.user)
        if serializer.is_valid():
            serializer.save(reporter=request.user.id)
            status_is = status.HTTP_200_OK
            message_is = {"message": "저장완료"}
        else:
            status_is = status.HTTP_400_BAD_REQUEST
            message_is = serializer.errors
        return message_is, status_is

    def report_article(self, request):
        """request_type:   "article" """
        serializer = ReportArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user.id)
            status_is = status.HTTP_200_OK
            message_is = {"message": "저장완료"}
        else:
            status_is = status.HTTP_400_BAD_REQUEST
            message_is = serializer.errors
        return message_is, status_is

    def report_comment(self, request):
        """request_type:   "comment" """
        serializer = ReportCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user.id)
            status_is = status.HTTP_200_OK
            message_is = {"message": "저장완료"}
        else:
            status_is = status.HTTP_400_BAD_REQUEST
            message_is = serializer.errors
        return message_is, status_is

    def fail(self, request):
        """request_type:  errors"""
        status_is = status.HTTP_400_BAD_REQUEST
        message_is = {"message": "신고유형이 잘못되었습니다."}
        return message_is, status_is

    request_dic = {
        "user": report_user,
        "article": report_article,
        "comment": report_comment,
        "fail": fail,
    }

    def post(self, request):
        request_type = request.data.get("request_type")
        message_is, status_is = self.request_dic.get(
            request_type, self.request_dic["fail"]
        )(self, request)
        return Response(message_is, status=status_is)


class CategoryView(APIView):
    def search(self, id, count):
        """full category"""
        childs = ChildCategory.objects.filter(parent_category=id).order_by("riority")
        print(childs)

        list_id = []
        for child in childs:
            if child.down_list_num:
                if count != 1:
                    list_id += [self.search(child.down_list_num, count - 1)]
            list_id += child.category.name
        return list_id

    def get(self, requst):
        list_id = self.search(1, 5)
        print(list_id)
        return Response(list_id, status=status.HTTP_200_OK)
