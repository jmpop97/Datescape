from rest_framework import serializers
from articles.models import (
    Article,
    ArticleImage,
    Tag,
    Comment,
    CommentLike,
    MapDataBase,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["tag"]

    # def to_representation(self, instance):
    #     return instance.tag


class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ("id", "images", "article")


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
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
            image_urls = [article_image.image.url for article_image in article_images]
        except AttributeError:
            image_urls = None
        return image_urls

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

    article_set = ArticleSerializer(many=True, read_only=True)

    class Meta:
        model = MapDataBase
        fields = (
            "jibun_address",
            "road_address",
            "coordinate_x",
            "coordinate_y",
            "id",
            "article_set",
        )

    def create(self, validated_data):
        return MapDataBase.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """댓글 조회"""

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
    """댓글 생성 / 수정"""

    class Meta:
        model = Comment
        fields = ("comment", "use_emoticon", "id")


class CommentLikeSerizlizer(serializers.ModelSerializer):
    """댓글 좋아요"""

    class Meta:
        model = CommentLike
        fields = "__all__"
