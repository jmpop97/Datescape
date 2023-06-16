from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ParseError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        cur_password = validated_data.pop("password1", None)
        new_password = validated_data.pop("password2", None)

        user = super().update(instance, validated_data)

        if not cur_password or not new_password:
            return ParseError

        if not user.check_password(cur_password):
            raise ValueError
        # password = user.password
        user.set_password(new_password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        token["login_type"] = user.login_type
        token["is_admin"] = user.is_admin

        return token


# 상대방 유저 정보 확인용
class UserDetailSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return obj.like_user.count()

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "profileimage",
            "likes",
        ]


# 비밀번호 변경
class PasswordEditSerializer(serializers.ModelSerializer):
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "new_password1",
            "new_password2",
        ]

    def update(self, instance, validated_data):
        new_password1 = validated_data.pop("new_password1", None)
        new_password2 = validated_data.pop("new_password2", None)

        user = super().update(instance, validated_data)

        if not new_password1 or not new_password2:
            print("새로운 비번1,2 중 하나가 없음")
            return ParseError

        if new_password1 != new_password2:
            print("새로운 비번1,2가 같지 않음")
            raise ValueError

        user.set_password(new_password1)
        user.save()

        return user


# username, profileimage 변경
class ProfileEditSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    # profileimage = serializers.ImageField(required=False)
    new_password1 = serializers.CharField(write_only=True, required=False)
    new_password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["username", "profileimage", "new_password1", "new_password2"]

    def update(self, instance, validated_data):
        new_password1 = validated_data.pop("new_password1", None)
        new_password2 = validated_data.pop("new_password2", None)

        user = super().update(instance, validated_data)

        if not new_password1 and new_password2:
            return ParseError
        if new_password1 != new_password2:
            return ValueError

        user.save()

        return user
