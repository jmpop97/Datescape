from rest_framework import serializers
from articles.models import (Article,Tag,
                            Comment, CommentLike, KakaoMapDataBase)


class MapSearchSerializer(serializers.ModelSerializer):
    """지도정보 db저장"""

    class Meta:
        model = KakaoMapDataBase
        fields = ('jibun_address', 'road_address', 'coordinate_x', 'coordinate_y')

    def create(self, validated_data):
        return KakaoMapDataBase.objects.create(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag']

    # def to_representation(self, instance):
    #     return instance.tag


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'content', 'images', 'score', 'tags']


class ArticleCreateSerializer (serializers.ModelSerializer):
    """ 상세 게시글 조회 """
    user = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = Article
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """댓글 조회 """
    username = serializers.SerializerMethodField()
    likers = serializers.SerializerMethodField()

    def get_username(self, comment):
        return comment.writer.username
    
    def get_likers(self, comment):
        qs = CommentLike.objects.filter(comment=comment, db_status=1)
        likes = CommentLikeSerizlizer(qs, many=True).data
        return likes

    class Meta:
        model = Comment
        fields = "__all__"


class CommentCreateSerializer(serializers.ModelSerializer):
    """ 댓글 생성 / 수정 """
    class Meta:
        model = Comment
        fields = ('comment', 'use_emoticon', 'id')


class CommentLikeSerizlizer(serializers.ModelSerializer):
    """ 댓글 좋아요 """
    class Meta:
        model = CommentLike
        fields = "__all__"
