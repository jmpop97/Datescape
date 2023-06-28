from pprint import pprint
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from articles.serializers import (
    ArticleSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    MapSearchSerializer,
    BookMarkSerializer,
    ReplySerializer,
    TagSerializer,
)
from articles.models import (
    Article,
    ArticleImage,
    Tag,
    TagList,
    Comment,
    CommentLike,
    MapDataBase,
    WeeklyTags,
    BookMark,
    Reply,
)
from alarms.models import Alarm
from dsproject import settings
from django.db.models import Q
from haversine import haversine, Unit
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .pagination import PaginationHandler


import json
import requests
import time
import random
from apscheduler.schedulers.background import BackgroundScheduler
from rest_framework.throttling import UserRateThrottle

REST_API_KEY = settings.REST_API
NAVER_MAPS_API_GW_API_KEY_ID = settings.NAVER_MAPS_API_ID
NAVER_MAPS_API_GW_API_KEY = settings.NAVER_MAPS_API_KEY


# 10초당 3번시 벤
class limit10Throttle(UserRateThrottle):
    def __init__(self):
        pass

    def allow_request(self, request, view):
        if request.method == "POST":
            self.rate = self.get_rate()
            self.num_requests = 3
            self.duration = 10
            # overriding
            if self.rate is None:
                return True
            self.key = self.get_cache_key(request, view)
            if self.key is None:
                return True

            self.history = self.cache.get(self.key, [])
            self.now = self.timer()

            # Drop any requests from the history which have now passed the
            # throttle duration
            while self.history and self.history[-1] <= self.now - self.duration:
                self.history.pop()
            if len(self.history) >= self.num_requests:
                request.user.is_active = False
                request.user.save()
                return self.throttle_failure()
            return self.throttle_success()
        return True


# 초당 4번시 벤
class limit1Throttle(UserRateThrottle):
    def __init__(self):
        pass

    def allow_request(self, request, view):
        if request.method == "POST":
            self.rate = self.get_rate()
            self.num_requests, self.duration = self.parse_rate(self.rate)
            self.num_requests = 4
            self.duration = 1
            # overriding
            if self.rate is None:
                return True
            self.key = self.get_cache_key(request, view)
            if self.key is None:
                return True

            self.history = self.cache.get(self.key, [])
            self.now = self.timer()

            # Drop any requests from the history which have now passed the
            # throttle duration
            while self.history and self.history[-1] <= self.now - self.duration:
                self.history.pop()
            if len(self.history) >= self.num_requests:
                request.user.is_active = False
                request.user.save()
                return self.throttle_failure()
            return self.throttle_success()
        return True


# 최대 초당 1번만 받음
class TestThrottle(UserRateThrottle):
    def __init__(self):
        pass

    def allow_request(self, request, view):
        if request.method == "POST":
            self.rate = self.get_rate()
            self.num_requests, self.duration = self.parse_rate(self.rate)
            self.num_requests = 1
            self.duration = 1
            # overriding
            if self.rate is None:
                return True
            self.key = self.get_cache_key(request, view)
            if self.key is None:
                return True

            self.history = self.cache.get(self.key, [])
            self.now = self.timer()

            # Drop any requests from the history which have now passed the
            # throttle duration
            while self.history and self.history[-1] <= self.now - self.duration:
                self.history.pop()
            if len(self.history) >= self.num_requests:
                request.user.is_active = True
                request.user.save()
                print(request.user)
                print(len(self.history))
                return self.throttle_failure()
            return self.throttle_success()
        return True


class CommonPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 1000


class UserArticleView(APIView):
    """
    유저 마이페이지 - 작성한 게시글 보기
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        articles = Article.objects.filter(user=request.user, db_status=1).order_by(
            "-created_at"
        )
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleView(APIView, PaginationHandler):
    """
    네이버지도 api사용
    게시글 작성
    """

    throttle_classes = [TestThrottle, limit1Throttle, limit10Throttle]

    pagination_class = CommonPagination

    def get(self, request):
        score = request.GET.get("score")
        try:
            score_range = score.split(",")
        except:
            pass
        queryset = Article.objects.filter(db_status=1).order_by("-created_at")
        if score:
            queryset = queryset.filter(
                score__range=[int(score_range[0]), int(score_range[1])]
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(
                ArticleSerializer(page, many=True).data
            )
        else:
            serializer = ArticleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # 검색할 지번 또는 도로명 주소
        query = request.data.get("query")

        # 네이버 지도 API로부터 검색 결과 가져오기
        headers = {
            "X-NCP-APIGW-API-KEY-ID": NAVER_MAPS_API_GW_API_KEY_ID,
            "X-NCP-APIGW-API-KEY": NAVER_MAPS_API_GW_API_KEY,
        }
        params = {"query": query}
        search_url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
        response = requests.get(search_url, headers=headers, params=params)
        result = response.json()
        # 검색 결과에서 주소 정보 추출
        address = result["addresses"][0]
        address_info = {
            "road_address": address["roadAddress"],
            "jibun_address": address["jibunAddress"],
            "coordinate_x": address["x"],
            "coordinate_y": address["y"],
        }

        # 게시글 정보
        title = request.data.get("title")
        content = request.data.get("content")
        score = request.data.get("score")
        main_image = request.data.get("main_image")

        # MapSearch 모델 저장
        serializer = MapSearchSerializer(data=address_info)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer_id = MapDataBase.objects.get(
                    road_address=address["roadAddress"]
                ).id
            except:
                serializer.save()
                serializer_id = serializer.data["id"]
        # 게시글 저장
        article_serializer = ArticleSerializer(
            data={
                "title": title,
                "content": content,
                "score": score,
                "location": serializer_id,
                "main_image": main_image,
            },
            context={"images": request.data.getlist("images")},
        )
        if article_serializer.is_valid():
            article = article_serializer.save(user=request.user)
            tags = request.data.get("tags", "").split("$%#&#^)!()")
            while True:
                try:
                    tags.remove("")
                except:
                    break
            for tag in tags:
                tag_obj, _ = Tag.objects.get_or_create(tag=tag)
                article.tags.add(tag_obj)
            return Response(article.id, status=status.HTTP_200_OK)
        else:
            return Response(
                article_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class ArticleDetailView(APIView):
    """
    delete에서도 언급하겠지만 db_status 값이 1인 게시글들만 출력되게 작업했습니다.
    """

    def get(self, request, article_id):
        article = Article.objects.filter(id=article_id, db_status=1).first()
        if article:
            # db_status가 1인 게시글이 있는 경우
            serializer = ArticleSerializer(article)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # db_status가 2인 게시글이 없는 경우
            return Response("삭제된 글입니다.", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, article_id):
        """
        게시글 수정부분입니다.
        location 값이 int로 들어가는데 실제로 수정할 땐 주소로 수정 가능하게 해야 합니다.
        """
        # 작성자만 수정 가능하게!
        article = get_object_or_404(Article, id=article_id)

        remove_ids = request.data.get("images_rm")
        if remove_ids:
            ids_list = remove_ids.split(",")
        else:
            ids_list = []

        if request.user == article.user:
            if "images" in request.data:
                serializer = ArticleSerializer(
                    article,
                    data=request.data,
                    context={"images": request.data.getlist("images")},
                )
            else:
                serializer = ArticleSerializer(article, data=request.data)

            if serializer.is_valid():
                # 제목 / 내용 / 평점 저장
                serializer.save()

                # 이미지 저장
                images_data = serializer.context.get("images", None)
                if images_data:
                    for image_data in images_data:
                        ArticleImage.objects.create(article=article, image=image_data)

                # 이미지 삭제
                if ids_list != None:
                    for id in ids_list:
                        k = ArticleImage.objects.get(id=id)
                        k.delete()

                # 지도 저장
                if "query" in request.data:
                    # 검색할 지번 또는 도로명 주소
                    query = request.data.get("query")
                    # 네이버 지도 API로부터 검색 결과 가져오기
                    headers = {
                        "X-NCP-APIGW-API-KEY-ID": NAVER_MAPS_API_GW_API_KEY_ID,
                        "X-NCP-APIGW-API-KEY": NAVER_MAPS_API_GW_API_KEY,
                    }
                    params = {"query": query}
                    search_url = (
                        "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
                    )
                    response = requests.get(search_url, headers=headers, params=params)
                    result = response.json()
                    # 검색 결과에서 주소 정보 추출
                    address = result["addresses"][0]
                    address_info = {
                        "road_address": address["roadAddress"],
                        "jibun_address": address["jibunAddress"],
                        "coordinate_x": address["x"],
                        "coordinate_y": address["y"],
                    }
                    serializer = MapSearchSerializer(data=address_info)
                    if serializer.is_valid(raise_exception=True):
                        try:
                            serializer_id = MapDataBase.objects.get(
                                road_address=address["roadAddress"]
                            ).id
                        except:
                            serializer.save()
                            serializer_id = serializer.data["id"]
                        for_update_article = Article.objects.get(id=article_id)
                        update_mapdata = get_object_or_404(
                            MapDataBase, id=serializer_id
                        )
                        for_update_article.location = update_mapdata
                        for_update_article.save()

                # 태그 저장
                if "tags" in request.data:
                    tags = request.data.get("tags").split("$%#&#^)!()")
                    saved_tags = TagList.objects.filter(article=article)
                    for a in saved_tags:
                        a.delete()
                    for i, tag in enumerate(tags):
                        if i == 0:
                            pass
                        else:
                            tag_obj, _ = Tag.objects.get_or_create(tag=tag)
                            article.tags.add(tag_obj)

                save_article = get_object_or_404(Article, id=article_id)
                save_serializer = ArticleSerializer(save_article)
                return Response(save_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_id):
        """
        게시글을 삭제합니다.
        db_status 값을 1에서 2로 수정해 줌으로써 get 요청받는 부분에서 표시가 되지 않게 적용해 주었습니다.
        """
        article = get_object_or_404(Article, id=article_id, db_status=1)
        # 작성자만 삭제 가능하게!
        if request.user == article.user:
            article.db_status = 2
            article.save()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)


class LocationListView(APIView):
    """
    사용자 위치를 기반으로 반경 2km에 있는 데이터를 불러옵니다.

    input: 쿼리=latitude&longitude
    ouput: 장소들과 그 장소에 달린 게시물들

    """

    def get(self, request):
        lat = float(self.request.query_params.get("lat", ""))
        lon = float(self.request.query_params.get("lon", ""))
        dist = float(self.request.query_params.get("dist", ""))
        position = (lat, lon)
        # 필터 조건
        q = Q()
        q.add(
            Q(
                coordinate_y__range=(
                    lat - 0.01 * dist,
                    lat + 0.01 * dist,
                )
            )
            | Q(
                coordinate_x__range=(
                    lon - 0.015 * dist,
                    lon + 0.015 * dist,
                )
            ),
            q.AND,
        )
        q.add(Q(db_status=1), q.AND)
        # 필터링
        near_articles = MapDataBase.objects.filter(q)
        # 내 위치와 필터링된 객체 사이의 거리가 2km 이하인 것만 가져오기
        test = [
            na
            for na in near_articles
            if (na.article_set.filter(db_status=1).count() != 0)
            and (haversine(position, (na.coordinate_y, na.coordinate_x))) <= dist
        ]
        serializer = MapSearchSerializer(test, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleSearchView(generics.ListAPIView):
    """
    아티클/태그 검색한 후 해당하는 아티클을 반환합니다.

    input: 쿼리=option&search
    ouput: 검색어가 포함된 게시물들

    """

    serializer_class = ArticleSerializer

    def get_queryset(self):
        search = self.request.query_params.get("search")
        option = self.request.query_params.get("option")
        queryset_list = []
        # 글 검색
        if option == "article" or option == "all":
            queryset = Article.objects.filter(db_status=1)
            if search is not None:
                queryset = (
                    queryset.filter(
                        Q(title__icontains=search) | Q(content__icontains=search)
                    )
                    .distinct()
                    .order_by("-created_at")
                )
                for a in queryset:
                    queryset_list.append(a)
        # 태그 검색
        if option == "tag" or option == "all":
            queryset = Tag.objects.filter(Q(db_status=1) & Q(tag__icontains=search))
            if search is not None:
                for a in queryset:
                    taglist = a.taglist_set.all().order_by("-created_at")
                    for b in taglist:
                        if b.article.db_status == 1:
                            queryset_list.append(b.article)
        # 지역 검색
        if option == "location" or option == "all":
            search_list = search.split(" ")
            location_list = []
            queryset = MapDataBase.objects.filter(db_status=1)
            if search is not None:
                for location in search_list:
                    queryset = (
                        queryset.filter(
                            Q(jibun_address__icontains=location)
                            | Q(road_address__icontains=location)
                        )
                        .distinct()
                        .order_by("-created_at")
                    )
                    for loc in queryset:
                        location_list.append(loc)
                for a in list(dict.fromkeys(location_list)):
                    article_list = a.article_set.filter(db_status=1).order_by(
                        "-created_at"
                    )
                    for b in article_list:
                        queryset_list.append(b)
        # 중복 검색 값 제거
        result = []
        for i in queryset_list:
            if i not in result:
                result.append(i)
        return result


class LocationArticlesView(generics.ListAPIView):
    """
    장소 별로 리뷰를 받아오기 위한 view입니다.

    input: 쿼리=location_id
    output: 쿼리로 받아온 장소에 달린 게시물들

    """

    serializer_class = ArticleSerializer

    def get_queryset(self):
        location = self.request.query_params.get("location")
        queryset = Article.objects.filter(
            Q(db_status=1) & Q(location_id=location)
        ).order_by("-created_at")
        return queryset


class CommentView(APIView):
    """
    댓글 작성 / 수정 / 삭제

    게시글에 대한 댓글의 작성 / 수정 / 삭제 요청을 처리합니다.
    설명~~~~~~
    로그인 권한이 요구됩니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, article_id):
        """
        게시글에 대한 댓글 조회 요청을 처리합니다.

        input: 로그인 상태, 게시글 id
        output: 요청 처리에 따라 status 값을 반환
        """
        article = get_object_or_404(Article, id=article_id, db_status=1)
        comments = Comment.objects.filter(article=article, db_status=1).order_by(
            "-created_at"
        )
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_id):
        """
        게시글에 대한 댓글 작성 요청을 처리합니다.

        내용 or 이모티콘 중 1가지 이상 작성 필요
        input: 로그인 상태, 댓글 내용, 사용 이모티콘, 게시글 id
        output: 요청 처리에 따라 status 값을 반환
        """
        article = get_object_or_404(Article, id=article_id, db_status=1)
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(writer=request.user, article=article)
            # 알림 생성
            if request.user != article.user:  # 댓글 작성자와 게시글 주인이 다를때만 알림 생성
                Alarm.objects.create(
                    target_user=article.user,
                    type="comment",
                    type_id=serializer.data["id"],
                )
            return Response(
                CommentSerializer(Comment.objects.get(id=serializer.data["id"])).data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, article_id):
        """
        댓글 수정 요청을 처리합니다.

        request.data에 comment_id값을 같이 받아옵니다.
        input: 로그인 상태, 수정하고자 하는 댓글 id, 내용, 사용 이모티콘
        output: 요청 처리에 따라 status 값을 반환
        """
        comment_id = request.data["comment_id"]
        article = get_object_or_404(Article, id=article_id, db_status=1)
        comment = get_object_or_404(
            Comment, id=comment_id, article=article, db_status=1
        )
        if request.user == comment.writer:
            serializer = CommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    CommentSerializer(
                        Comment.objects.get(id=serializer.data["id"])
                    ).data,
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

    def delete(self, request, article_id):
        """
        댓글 삭제 요청을 처리합니다.

        request.data에 comment_id값을 같이 받아옵니다.
        input: 로그인 권한, 게시글 id
        output: 요청 처리에 따라 status 값을 반환
        """
        comment_id = request.data["comment_id"]
        article = get_object_or_404(Article, id=article_id, db_status=1)
        comment = get_object_or_404(
            Comment, id=comment_id, article=article, db_status=1
        )

        if request.user == comment.writer:
            comment.db_status = 2
            comment.save()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)


class CommentLikeView(APIView):
    """
    댓글 좋아요

    댓글에 대한 좋아요 요청을 처리합니다.
    댓글과 유저모델을 참조하는 CommentLike객체를 생성합니다.
    로그인 권한이 요구됩니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        댓글에 대한 좋아요 요청을 처리합니다.

        input: 로그인 상태, 댓글 id
        output: 요청 처리에 따라 status 값을 반환
        """
        comment_id = request.data["comment_id"]
        comment = get_object_or_404(Comment, id=comment_id, db_status=1)
        user = request.user

        if CommentLike.objects.filter(comment=comment, likers=user):
            CommentLike.objects.filter(comment=comment, likers=user).delete()
            comment_likes = len(CommentLike.objects.filter(comment=comment))
            return Response(
                {"message": "좋아요 취소!", "comment_likes": comment_likes},
                status=status.HTTP_200_OK,
            )
        else:
            CommentLike.objects.create(likers=user, comment=comment)
            comment_likes = len(CommentLike.objects.filter(comment=comment))
            return Response(
                {"message": "좋아요!", "comment_likes": comment_likes},
                status=status.HTTP_200_OK,
            )


class UserCommentView(APIView):
    """
    유저 마이페이지 - 작성한 댓글 보기
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """작성한 댓글 가져오기"""
        comments = Comment.objects.filter(writer=request.user, db_status=1).order_by(
            "-created_at"
        )
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleRandomView(generics.ListAPIView):
    """
    여러개의 게시물을 무작위로 반환합니다.
    태그를 무작위로 하나 선택하여 그 태그가 달린 게시물들을 반환합니다.

    input: 쿼리=option
    ouput: 무작위 게시물들

    """

    serializer_class = ArticleSerializer

    def get_queryset(self):
        # 게시물 임의 선택
        if self.request.query_params.get("option") == "article":
            return random_article
        # 임의의 태그 선택
        elif self.request.query_params.get("option") == "tag":
            weekly_tags = WeeklyTags.objects.all()
            tag = weekly_tags[0]
            articles = tag.tag.article_set.filter(db_status=1).order_by("-created_at")
            if articles.count() == 0:
                get_weekly_tags()
                weekly_tags = WeeklyTags.objects.all()
                tag = weekly_tags[0]
                articles = tag.tag.article_set.filter(db_status=1).order_by(
                    "-created_at"
                )
            return articles


def get_random_article():
    global random_article
    try:
        queryset = Article.objects.filter(db_status=1)
        random_article = random.sample(list(queryset), k=5)
    except:
        random_article = Article.objects.filter(db_status=1)


get_random_article()

scheduler = BackgroundScheduler()

scheduler.add_job(get_random_article, "cron", hour=0, id="rand_1")


def get_weekly_tags():
    weekly_tags = WeeklyTags.objects.all()
    queryset = Tag.objects.filter(Q(db_status=1))
    try:
        if weekly_tags.count() == 7:
            weekly_tags[0].delete()
            random_tags = random.choice(list(queryset))
            WeeklyTags.objects.create(tag=random_tags)
        elif weekly_tags.count() < 7:
            for i in range(7 - weekly_tags.count()):
                random_tags = random.choice(list(queryset))
                WeeklyTags.objects.create(tag=random_tags)
        elif weekly_tags.count() > 7:
            for i in range(weekly_tags.count() - 7):
                weekly_tags[0].delete()
    except:
        tag = Tag.objects.create(tag="여행")
        WeeklyTags.objects.create(tag=tag)


try:
    get_weekly_tags()
except:
    pass
scheduler.add_job(get_weekly_tags, "cron", hour=0, id="rand_3")

scheduler.start()


class WeeklyTagsView(APIView):
    """
    주간 태그를 보내주는 뷰
    """

    def get(self, request):
        weekly_tags = WeeklyTags.objects.all()
        serializer = TagSerializer(weekly_tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookMarkView(APIView):
    """게시글 북마크"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """(마이페이지) 북마크 리스트 보기"""
        bookmark = BookMark.objects.filter(user=request.user)
        serializer = BookMarkSerializer(bookmark, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """북마크 등록/취소"""
        article_id = request.data.get("article_id")
        article = get_object_or_404(Article, id=article_id)
        user = request.user

        if BookMark.objects.filter(article=article, user=user):
            BookMark.objects.filter(article=article, user=user).delete()
            article_bookmarks = len(BookMark.objects.filter(article=article))
            return Response(
                {"message": "북마크 취소!", "article_bookmarks": article_bookmarks},
                status=status.HTTP_200_OK,
            )
        else:
            BookMark.objects.create(user=user, article=article)
            article_bookmarks = len(BookMark.objects.filter(article=article))
            return Response(
                {"message": "북마크 등록!", "article_bookmarks": article_bookmarks},
                status=status.HTTP_200_OK,
            )


class ReplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        reply = Reply.objects.filter(comment=comment, db_status=1).order_by(
            "-created_at"
        )
        serializer = ReplySerializer(reply, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(comment=comment, writer=user)
            # 알림 생성
            if request.user != comment.writer:  # 대댓글 작성자와 댓글 주인이 다를때만 알림 생성
                Alarm.objects.create(
                    target_user=comment.writer,
                    type="reply",
                    type_id=serializer.data["id"],
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, comment_id):
        reply_id = request.data["reply_id"]
        comment = get_object_or_404(Comment, id=comment_id, db_status=1)
        reply = get_object_or_404(Reply, id=reply_id, comment=comment, db_status=1)
        if request.user == reply.writer:
            serializer = ReplySerializer(reply, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

    def delete(self, request, comment_id):
        reply_id = request.data.get("reply_id")
        reply = get_object_or_404(Reply, id=reply_id, db_status=1)
        if request.user == reply.writer:
            reply.db_status = 2
            reply.save()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)
