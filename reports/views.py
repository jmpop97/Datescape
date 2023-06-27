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

    def post(self, request):
        """0:추가
        양수:수정
        [부모수정,자식수정]
        """
        if request.user.is_admin:
            request_datas = request.data.get("request_datas", [])
            for fix_parent, fix_child in request_datas:
                _obj, _ = CategoryName.objects.get_or_create(name=fix_parent[1])
                if int(fix_parent[0]) > 0:
                    fix_p = ParentCategory.objects.get(id=int(fix_parent[0]))
                else:
                    fix_p = ParentCategory()
                fix_p.name = _obj
                fix_p.save()
                not_del_cs = []
                for i, [fix_id, fix_string, fix_down] in enumerate(fix_child):
                    fix_id = int(fix_id)
                    _obj, _ = CategoryName.objects.get_or_create(name=fix_string)
                    if fix_id > 0:
                        fix_c = ChildCategory.objects.get(id=fix_id)
                    else:
                        fix_c = ChildCategory()
                    fix_c.parent_category = fix_p
                    fix_c.category = _obj
                    fix_c.down_list_num = fix_down
                    fix_c.riority = i
                    fix_c.save()
                    not_del_cs += [fix_c.id]
                ChildCategory.objects.filter(
                    parent_category=int(fix_parent[0])
                ).exclude(id__in=not_del_cs).delete()
            return Response({"message": "성공"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


class ChildCategoryView(APIView):
    def get(self, request):
        """["id",
        "parent_category",
        "category",
        "down_list_num"]"""
        request_type = request.GET.get("request_type", [])
        if request_type == "*":
            list = ChildCategory.objects.all()
        else:
            try:
                request_type = request_type.split(",")
                list = (
                    ChildCategory.objects.filter(parent_category__in=request_type)
                    .order_by("parent_category")
                    .order_by("riority")
                )

            except:
                return Response({"datas": [], "name": []}, status=status.HTTP_200_OK)

        parent_names = list.values_list("parent_category")
        child_names = list.values_list("category")
        names = {}
        for parent_name in parent_names:
            names[parent_name[0]] = parent_name[0]
        for child_name in child_names:
            names[child_name[0]] = child_name[0]
        name_list = CategoryName.objects.filter(id__in=names).values_list("id", "name")
        #     if parent_name in names:
        #         names[parent_name[0]] = names.id

        lists = list.values_list(
            "id",
            "parent_category",
            "category",
            "down_list_num",
        )
        return Response({"datas": lists, "name": name_list}, status=status.HTTP_200_OK)
