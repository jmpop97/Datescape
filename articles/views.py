from django.shortcuts import render
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from articles.serializers import (ArticleSerializer, ArticleCreateSerializer,
                                CommentSerializer, CommentCreateSerializer)
from articles.models import Article, Comment
import json
# Create your views here.

class ArticleView(APIView):# serializer 수정? 꾸미기?
    def get(self, request):
        """
        delete에서도 언급하겠지만 db_status 값이 1인 게시글들만 출력되게 작업했습니다.
        """
        articles = Article.objects.filter(db_status=1)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
