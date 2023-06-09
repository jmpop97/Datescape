from pprint import pprint
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from articles.serializers import (ArticleSerializer, ArticleCreateSerializer,
            CommentSerializer, CommentCreateSerializer, CommentLikeSerizlizer, MapSearchSerializer)
from articles.models import (Article, Tag,
                            Comment, CommentLike, KakaoMapDataBase)
from dsproject import settings
from django.db.models import Q
from haversine import haversine, Unit

import json
import requests

# Create your views here.
REST_API_KEY = settings.REST_API


class KakaoSaveView(APIView):
    """
    지도 db저장 뷰입니다.
    """
    def get(self, request):
        map_data = KakaoMapDataBase.objects.all()
        serializer = MapSearchSerializer(map_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MapSearchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KakaoMapCoordinateView(APIView):
    """
    get은필요없을거같지만 참고용으로두겠습니다 최종땐 삭제해야합니다.
    좌표검색용 뷰입니다.
    """
    def get(self, request, format=None):
        headers = {
            'Authorization': f'KakaoAK {REST_API_KEY}',  # REST API 키
            'Content-Type': 'application/x-www-form-urlencoded',
            # 헤더 설정
        }
        # 검색할 좌표 값
        x, y = 126.531039, 33.499553 
        url = f'https://dapi.kakao.com/v2/local/geo/coord2address.json?x={x}&y={y}'
        response = requests.get(url, headers=headers)
        data = response.json()

        # 주소 추출 및 반환
        documents = data.get('documents')
        if documents:
            address = documents[0].get('address').get('address_name')
            road_address = documents[0].get('road_address').get('address_name')
            return Response({'address': address, 'road_address':road_address})
        else:
            return Response({'error': '결과가 없습니다...니다...ㅠㅠㅠㅠㅠ'},status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        headers = {
            'Authorization': f'KakaoAK {REST_API_KEY}',
        }
        x = request.data.get('x', None)
        y = request.data.get('y', None)
        data = {
            'x': float(x),
            'y': float(y),    
        }
        url = f'https://dapi.kakao.com/v2/local/geo/coord2address.json?x={x}&y={y}'
        response = requests.post(url, headers=headers)
        data = response.json()
        documents = data.get('documents')
        if documents:
            address = documents[0].get('address').get('address_name')
            road_address = documents[0].get('road_address').get('address_name')
            return Response({'address': address, 'road_address':road_address})
        else:
            return Response({'error': '결과가 없습니다...니다...ㅠㅠㅠㅠㅠ'},status=status.HTTP_204_NO_CONTENT)


class KakaoMapSearchView(APIView):
    """
    지역명 검색용 뷰입니다.
    """
    def post(self, request):
        headers = {
            'Authorization': f'KakaoAK {REST_API_KEY}',
        }
        query = request.data.get('query', None)
        data = {
            'query': query
        }
        url = f'https://dapi.kakao.com/v2/local/search/keyword.json?query={query}'
        response = requests.post(url, headers=headers)
        data = response.json()
        documents = data.get('documents')
        if documents:
            serializer = MapSearchSerializer(data={
                'jibun_address': documents[0].get('address_name'),
                'road_address': documents[0].get('road_address_name'),
                'coordinate_x': documents[0].get('x'),
                'coordinate_y': documents[0].get('y'),
            })

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '결과가 없습니다.'},status=status.HTTP_204_NO_CONTENT)



class ArticleView(APIView):# serializer 수정? 꾸미기?
    def get(self, request):
        """
        delete에서도 언급하겠지만 db_status 값이 1인 게시글들만 출력되게 작업했습니다.
        """
        articles = Article.objects.filter(db_status=1)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        tags = request.data.pop('tags', [])
        serializer = ArticleSerializer(data=request.data)

        if serializer.is_valid():
            article = serializer.save(user=request.user)
            for tag in tags:
                tag_obj, _ = Tag.objects.get_or_create(tag=tag)
                article.tags.add(tag_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleCreateSerializer(article, data=request.data)
        # 작성자만 수정 가능하게!
        if request.user == article.user:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request,article_id):
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
        comments = Comment.objects.filter(article=article, db_status=1)
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
            return Response(CommentSerializer(Comment.objects.get(id=serializer.data['id'])).data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, article_id):
        """
        댓글 수정 요청을 처리합니다.

        request.data에 comment_id값을 같이 받아옵니다.
        input: 로그인 상태, 수정하고자 하는 댓글 id, 내용, 사용 이모티콘
        output: 요청 처리에 따라 status 값을 반환
        """
        comment_id = request.data['comment_id']
        article = get_object_or_404(Article, id=article_id, db_status=1)
        comment = get_object_or_404(Comment, id=comment_id, article=article, db_status=1)
        if request.user == comment.writer:
            serializer = CommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(CommentSerializer(Comment.objects.get(id=serializer.data['id'])).data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_id):
        """
        댓글 삭제 요청을 처리합니다.

        request.data에 comment_id값을 같이 받아옵니다.
        input: 로그인 권한, 게시글 id
        output: 요청 처리에 따라 status 값을 반환
        """
        comment_id = request.data['comment_id']
        article = get_object_or_404(Article, id=article_id, db_status=1)
        comment = get_object_or_404(Comment, id=comment_id, article=article, db_status=1)

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
        comment_id = request.data['comment_id']
        comment = get_object_or_404(Comment, id=comment_id, db_status=1)
        user = request.user

        if CommentLike.objects.filter(comment=comment, likers=user):
            CommentLike.objects.filter(comment=comment, likers=user).delete()
            return Response({'message':'좋아요 취소!'}, status=status.HTTP_200_OK)
        else:
            CommentLike.objects.create(likers=user, comment=comment)
            return Response({'message':'좋아요!'}, status=status.HTTP_200_OK)


class ArticleLocationView(APIView):
    """
    사용자 위치를 기반으로 반경 2km에 있는 데이터를 불러옵니다.
    """
    def get(self, request):
        latitude = self.request.GET.get('latitude', '')
        longitude = self.request.GET.get('longitude', '')
        position  = (float(latitude),float(longitude))
        print(position)
        # 필터 조건
        q = Q()
        q.add( Q(coordinate_y__range  = (float(latitude) - 0.01, float(latitude) + 0.01)) |
            Q(coordinate_x__range = (float(longitude) - 0.015, float(longitude) + 0.015)),
            q.AND)
        q.add(Q(db_status=1), q.AND)     
        # 필터링
        near_articles = (KakaoMapDataBase.objects.filter(q))
        print(near_articles)
        # 내 위치와 필터링된 객체 사이의 거리가 2km 이하인 것만 가져오기
        test = [na for na in near_articles if haversine(position, (na.coordinate_y, na.coordinate_x)) <= 2]
        print(test)
        serializer = MapSearchSerializer(test, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)