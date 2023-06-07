from rest_framework import serializers
from emoticons.models import Emoticon, EmoticonImage, UserEmoticonList


class EmoticonImageSerializer(serializers.ModelSerializer):
    """이모티콘 이미지"""
    class Meta:
        model = EmoticonImage
        fields = ("id", "image", "db_status",)


class EmoticonSerializer(serializers.ModelSerializer):
    """이모티콘 조회 / 수정 / 삭제"""
    images = serializers.SerializerMethodField()
    creator_name = serializers.SerializerMethodField()

    def get_images(self, emoticon):
        qs = EmoticonImage.objects.filter(db_status=1, emoticon=emoticon)
        serializer = EmoticonImageSerializer(instance=qs, many=True)
        return serializer.data
    
    def get_creator_name(self, emoticon):
        return emoticon.creator.username

    class Meta:
        model = Emoticon
        fields = "__all__"


class EmoticonCreateSerializer(serializers.ModelSerializer):
    """이모티콘 생성"""
    images = EmoticonImageSerializer(many=True, required=False)

    class Meta:
        model = Emoticon
        fields = "__all__"

    def create(self, validated_data):
        images_data = self.context.get('images', None)
        emoticon = super().create(validated_data)
        if images_data:
            for image_data in images_data:
                EmoticonImage.objects.create(emoticon=emoticon, image=image_data)
        return emoticon


class UserEmoticonListSerializer(serializers.ModelSerializer):
    """유저가 구매한 이모티콘"""
    class Meta:
        model = UserEmoticonList
        fields = "__all__"
