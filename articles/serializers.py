from rest_framework import serializers
from articles.models import (
    Article,
    ArticleImage,
    Tag,
    Comment,
    CommentLike,
    KakaoMapDataBase,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["tag"]

    # def to_representation(self, instance):
    #     return instance.tag


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")
    tags = TagSerializer(many=True, read_only=True)
    # image = serializers.ListField(
    #     child=serializers.ImageField(),
    #     required=True
    # )
    jibun_address = serializers.SerializerMethodField()
    road_address = serializers.SerializerMethodField()
    coordinate_x = serializers.SerializerMethodField()
    coordinate_y = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "user",
            "title",
            "content",
            "images",
            "score",
            "tags",
            "jibun_address",
            "road_address",
            "coordinate_x",
            "coordinate_y",
        ]

    def create(self, validated_data):
        validated_data["location"] = KakaoMapDataBase.objects.get(
            id=validated_data["location"]
        )
        return super().create(validated_data)
    

class MapSearchSerializer(serializers.ModelSerializer):
    """지도정보 db저장"""
    article_set = ArticleSerializer(many=True, read_only=True)
    

    class Meta:
        model = KakaoMapDataBase
        fields = ("jibun_address", "road_address", "coordinate_x", "coordinate_y", "id", "article_set")

    def create(self, validated_data):
        return KakaoMapDataBase.objects.create(**validated_data)


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


class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ("id", "images", "article")


class ArticleCreateSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")
    tags = TagSerializer(many=True, read_only=True)
    # image = serializers.SerializerMethodField()
    jibun_address = serializers.SerializerMethodField()
    road_address = serializers.SerializerMethodField()
    coordinate_x = serializers.SerializerMethodField()
    coordinate_y = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    images = serializers.ListSerializer(
        child=serializers.ImageField(), required=False, write_only=True
    )
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
            "score",
            "tags",
            "jibun_address",
            "road_address",
            "coordinate_x",
            "coordinate_y",
        ]

    def create(self, validated_data):
        images_data = self.context.get("request").FILES.getlist("images")
        # print(images_data)
        # print("===========images_data============")
        # 위에서 변경된 부분 : getlist() 메서드를 사용해서 여러 개의 이미지 파일 처리
        validated_data["location"] = KakaoMapDataBase.objects.get(
            id=validated_data["location"]
        )
        article = Article.objects.create(**validated_data)
        for image_data in images_data:
            ArticleImage.objects.create(article=article, image=image_data)
            # 위에서 변경된 부분 : images -> image
        return article

    def get_image(self, obj):
        try:
            article_images = obj.articleimage_set.all()
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


class ArticlePutSerializer(serializers.ModelSerializer):
    """상세 게시글 조회"""

    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Article
        fields = "__all__"


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
