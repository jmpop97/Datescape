from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from users.models import User
from reports.models import ParentCategory, ChildCategory, CategoryName
from reports.serializers import (
    ReportUserSerializer,
    ReportArticleSerializer,
    ReportCommentSerializer,
    ChildCategorySerializer,
)


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

    request_dic = {
        "user": ReportUserSerializer,
        "article": ReportArticleSerializer,
        "comment": ReportCommentSerializer,
    }

    def post(self, request):
        request_type = request.data.get("request_type", "")
        print(request_type)
        try:
            serializer = self.request_dic[request_type](data=request.data)
            if serializer:
                if serializer.is_valid():
                    serializer.save(reporter=request.user.id)
                    status_is = status.HTTP_200_OK
                    message_is = {"message": "저장완료"}
                else:
                    status_is = status.HTTP_400_BAD_REQUEST
                    message_is = serializer.errors
                return Response(message_is, status=status_is)

        except:
            return Response(
                {"message": "신고유형이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST
            )


class CategoryView(APIView):
    def search(self, id, name, count):
        """full category"""
        childs = ChildCategory.objects.filter(parent_category=id).order_by("riority")

        list_id = []
        for child in childs:
            if child.down_list_num:
                if count != 1:
                    list_id += [
                        self.search(child.down_list_num, child.category.name, count - 1)
                    ]
            else:
                list_id += [[child.id, child.category.name]]
        return [id, name, list_id]

    def get(self, requst):
        request_id = requst.GET.get("id", 5)
        limits = requst.GET.get("limits", 5)
        try:
            main = ParentCategory.objects.get(id=request_id)
            list_id = self.search(request_id, str(main.name), limits)
            return Response(list_id, status=status.HTTP_200_OK)
        except:
            return Response({"message": "fail"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, requst):
        """0:추가
        양수:수정
        [부모삭제목록,자식삭제목록,부모수정,자식수정]
        """
        request_datas = requst.data.get("request_datas", [])
        for del_ps, del_cs, fix_parent, fix_child in request_datas:
            ParentCategory.objects.filter(id__in=del_ps).delete()
            ChildCategory.objects.filter(id__in=del_cs).delete()

            for fix_id, fix_string in fix_parent:
                _obj, _ = CategoryName.objects.get_or_create(name=fix_string)
                if fix_id > 0:
                    fix_p = ParentCategory.objects.get(id=fix_id)
                else:
                    fix_p = ParentCategory()
                fix_p.name = _obj
                fix_p.save()
            for i, [fix_id, fix_string] in enumerate(fix_child):
                _obj, _ = CategoryName.objects.get_or_create(name=fix_string)
                if fix_id > 0:
                    fix_c = ChildCategory.objects.get(id=fix_id)
                else:
                    fix_c = ChildCategory()
                fix_c.parent_category = fix_p
                fix_c.category = _obj
                fix_c.riority = i
                fix_c.save()

            return Response({"message": "성공"}, status=status.HTTP_200_OK)


class ChildCategoryView(APIView):
    def get(self, request):
        request_type = request.data.get("request_type", [])
        if request_type:
            list = ChildCategory.objects.filter(
                parent_category__in=request_type
            ).order_by("riority")
        else:
            list = ChildCategory.objects.all()
        lists = ChildCategorySerializer(list, many=True)
        return Response(lists.data, status=status.HTTP_200_OK)

    def post(self, request):
        match_data = request.data.get("match_data", [])
        for parent_id, fix_id in match_data:
            fix_c = ChildCategory.objects.get(id=fix_id)
            fix_c.down_list_num = parent_id
            fix_c.save()
        return Response({"message": "good"}, status=status.HTTP_200_OK)
