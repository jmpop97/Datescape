from rest_framework import serializers
from django.db.models import Avg
from articles.models import (
    Article,
    ArticleImage,
    Tag,
    Comment,
    CommentLike,
    MapDataBase,
    EmoticonImage,
    BookMark,
    Reply,
)
from emoticons.serializers import EmoticonImageSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["tag"]

    # def to_representation(self, instance):
    #     return instance.tag


class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")
    # username = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    jibun_address = serializers.SerializerMethodField()
    road_address = serializers.SerializerMethodField()
    coordinate_x = serializers.SerializerMethodField()
    coordinate_y = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()  # 조회 이미지 리스트
    images = serializers.ListSerializer(
        child=serializers.ImageField(), required=False, write_only=True
    )  # 게시글 저장할때 이미지
    # 위에서 아래로 변경된 부분 : ListSerializer와 serializers.ImageField

    class Meta:
        model = Article
        fields = [
            "id",
            "user",
            "title",
            "content",
            "images",
            "image",
            "main_image",
            "score",
            "tags",
            "jibun_address",
            "road_address",
            "coordinate_x",
            "coordinate_y",
            "location",
            "book_mark",
        ]

    def create(self, validated_data):
        """
        위에서 변경된 부분 : getlist() 메서드를 사용해서 여러 개의 이미지 파일 처리
        게시글 저장
        images사용
        """
        article = Article.objects.create(**validated_data)
        # 이미지 저장
        images_data = self.context.get("images", None)
        for image_data in images_data:
            ArticleImage.objects.create(article=article, image=image_data)
            # 위에서 변경된 부분 : images -> image
        return article

    def get_image(self, obj):
        """
        조회이미지리스트 보여주기
        """
        try:
            article_images = obj.article_images.all()
            temp = ArticleImageSerializer(article_images, many=True)
        except AttributeError:
            image_urls = None
        return temp.data

    def get_jibun_address(self, obj):
        kakao_map_data = obj.location
        jibun_address = kakao_map_data.jibun_address
        return jibun_address

    def get_road_address(self, obj):
        kakao_map_data = obj.location
        road_address = kakao_map_data.road_address
        return road_address

    def get_coordinate_x(self, obj):
        kakao_map_data = obj.location
        coordinate_x = kakao_map_data.coordinate_x
        return coordinate_x

    def get_coordinate_y(self, obj):
        kakao_map_data = obj.location
        coordinate_y = kakao_map_data.coordinate_y
        return coordinate_y


class MapSearchSerializer(serializers.ModelSerializer):
    """지도정보 db저장"""

    score_avg = serializers.SerializerMethodField()
    articles = serializers.SerializerMethodField()

    def get_articles(self, obj):
        qs = obj.article_set.filter(db_status=1)
        serializer = ArticleSerializer(instance=qs, many=True, read_only=True)
        return serializer.data

    def get_score_avg(self, obj):
        avg = obj.article_set.aggregate(Avg("score"))
        return avg["score__avg"]

    class Meta:
        model = MapDataBase
        fields = (
            "jibun_address",
            "road_address",
            "coordinate_x",
            "coordinate_y",
            "id",
            "articles",
            "score_avg",
        )

    def create(self, validated_data):
        return MapDataBase.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """댓글 조회"""

    username = serializers.SerializerMethodField()
    likers = serializers.SerializerMethodField()
    emoticon_image = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    article_id = serializers.IntegerField(source="article.id")
    article_title = serializers.CharField(source="article.title")
    article_content = serializers.CharField(source="article.content")
    article_main_image = serializers.ImageField(source="article.main_image")

    def get_username(self, comment):
        return comment.writer.username

    def get_likers(self, comment):
        qs = CommentLike.objects.filter(comment=comment, db_status=1)
        likes = CommentLikeSerizlizer(qs, many=True).data
        return likes

    def get_emoticon_image(self, comment):
        if comment.use_emoticon:
            image = EmoticonImage.objects.get(id=comment.use_emoticon.id)
            emoticon_image = EmoticonImageSerializer(image).data
            return emoticon_image["image"]
        else:
            return None

    def get_reply_count(self, comment):
        return len(Reply.objects.filter(comment=comment, db_status=1))

    class Meta:
        model = Comment
        fields = "__all__"


class CommentCreateSerializer(serializers.ModelSerializer):
    """댓글 생성 / 수정"""

    class Meta:
        model = Comment
        fields = ("comment", "use_emoticon", "id")


class CommentLikeSerizlizer(serializers.ModelSerializer):
    """댓글 좋아요"""

    class Meta:
        model = CommentLike
        fields = "__all__"


class BookMarkSerializer(serializers.ModelSerializer):
    article_id = serializers.IntegerField(source="article.id")
    article_user = serializers.CharField(source="user.username")
    article_title = serializers.CharField(source="article.title")
    article_content = serializers.CharField(source="article.content")
    article_main_image = serializers.ImageField(source="article.main_image")

    class Meta:
        model = BookMark
        fields = "__all__"


class ReplySerializer(serializers.ModelSerializer):
    writer_name = serializers.SerializerMethodField()
    emoticon_image = serializers.SerializerMethodField()

    def get_writer_name(self, reply):
        return reply.writer.username

    def get_emoticon_image(self, comment):
        if comment.use_emoticon:
            image = EmoticonImage.objects.get(id=comment.use_emoticon.id)
            emoticon_image = EmoticonImageSerializer(image).data
            return emoticon_image["image"]
        else:
            return None

    class Meta:
        model = Reply
        fields = "__all__"
