from rest_framework import serializers
from emoticons.models import Emoticon, EmoticonImage, UserEmoticonList


# 이모티콘 이미지들
class EmoticonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmoticonImage
        fields = ("id", "image", "db_status",)

# 이모티콘
class EmoticonSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, emoticon):
        qs = EmoticonImage.objects.filter(db_status=1, emoticon=emoticon)
        serializer = EmoticonImageSerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = Emoticon
        fields = "__all__"

# 이모티콘 생성
class EmoticonCreateSerializer(serializers.ModelSerializer):
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

# 유저가 구매한 이모티콘
class UserEmoticonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmoticonList
        fields = "__all__"
