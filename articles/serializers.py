from rest_framework import serializers
from articles.models import Article, Comment, CommentLike


class ArticleSerializer (serializers.ModelSerializer):
    """ 게시글 조회, 작성 """
    user = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = Article
        fields = "__all__"
    

# class ArticleSerializer (serializers.ModelSerializer):
    # """ 게시글 조회, 작성 """

#     class Meta:
#         model = Article
#         # fields = ("title", "content","score","images")
#         exclude = ("user",)

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
