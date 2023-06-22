import datetime, random
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ParseError
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from users.models import User
from users.tokens import account_activation_token


def message(domain, uidb64, token):
    return f"아래 링크를 클릭하면 회원가입 인증이 완료됩니다.\n\n회원가입 링크 : http://{domain}/users/activate/{uidb64}/{token}\n\n감사합니다."


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        ran_num = str(random.randint(0, 99))
        user = super().create(validated_data)
        user.nickname = user.username + ran_num
        password = user.password
        user.is_active = False
        user.set_password(password)
        user.save()

        # domain = "localhost:8000"
        domain = "https://back.datescape.shop/"
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        message_data = message(domain, uidb64, token)

        mail_title = "DateScape : 이메일 인증을 완료해주세요"
        to_email = user.email
        email = EmailMessage(mail_title, message_data, to=[to_email])
        email.send()

        return user

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        token["nickname"] = user.nickname
        token["login_type"] = user.login_type
        token["is_admin"] = user.is_admin
        # json_str = json.dumps(user.last_login, default=str)
        token["last_login"] = str(user.last_login)

        return token

    def update_last_login(self, user):
        user.last_login = datetime.now()
        user.save(update_fields=["last_login"])


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
            return ParseError

        if new_password1 != new_password2:
            raise ValueError

        user.set_password(new_password1)
        user.save()

        return user


# userID, profileimage 변경
class ProfileEditSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=False)
    nickname = serializers.CharField(required=False)
    # profileimage = serializers.ImageField(required=False)
    new_password1 = serializers.CharField(write_only=True, required=False)
    new_password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["nickname", "profileimage", "new_password1", "new_password2"]

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
