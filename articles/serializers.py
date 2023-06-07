from rest_framework import serializers
from articles.models import Article


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
