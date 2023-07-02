# from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from emoticons.models import Emoticon, EmoticonImage, UserEmoticonList
from emoticons.serializers import EmoticonSerializer
from faker import Faker

# 이미지 업로드
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile


"""
서버 요청 밴 기능으로 test코드 실행을 위해서 settings.py 137-141줄 DEFAULT_THROTTLE_RATES 항목 주석 필요
"""


def get_temporary_image(temp_file):
    """임시 이미지 파일 생성"""
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file


class EmoticonCreateTest(APITestCase):
    """이모티콘 테스트"""

    @classmethod
    def setUpTestData(cls):
        """생성용 data"""
        cls.user_data = {
            "email": "test@test.com",
            "username": "test",
            "password": "test",
        }
        cls.user = User.objects.create_user("test@test.com", "test", "test")
        cls.emoticon_data = {
            "title": "test emoticon",
            "images": [],
        }

    def setUp(self):
        """토큰"""
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    def test_fail_if_not_logged_in(self):
        """로그인 실패"""
        url = reverse("emoticon")
        response = self.client.post(url, self.emoticon_data)
        self.assertEqual(response.status_code, 401)

    def test_create_emoticon(self):
        """이모티콘 생성"""
        response = self.client.post(
            path=reverse("emoticon"),
            data=self.emoticon_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_create_emoticon_with_image(self):
        """이미지 파일 같이 생성"""
        # 임시 이미지 파일 다중 생성
        for i in range(10):
            temp_file = tempfile.NamedTemporaryFile()
            temp_file.name = f"image{i}.png"
            image_file = get_temporary_image(temp_file)
            image_file.seek(0)
            self.emoticon_data["images"].append(image_file)

        # post요청
        response = self.client.post(
            path=reverse("emoticon"),
            data=encode_multipart(data=self.emoticon_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)


class EmoticonCRUDTest(APITestCase):
    """유저 이모티콘 가져오기"""

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test@test.com",
            "username": "test",
            "password": "test",
        }
        cls.user = User.objects.create_user("test@test.com", "test", "test")
        cls.faker = Faker()
        # 이모티콘 더미 데이터 생성(다수)
        cls.emoticons = []
        for i in range(10):
            cls.user_faker = User.objects.create_user(
                cls.faker.email(), cls.faker.name(), cls.faker.word()
            )
            cls.emoticons.append(
                Emoticon.objects.create(creator=cls.user_faker, title=cls.faker.word())
            )
        # 이모티콘 더미 데이터 생성(단일)
        cls.emoticon_one = Emoticon.objects.create(
            creator=cls.user, title=cls.faker.word()
        )

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    def test_get_emoticon(self):
        """이모티콘 get요청"""
        for emoticon in self.emoticons:
            url = emoticon.get_absolute_url()

            response = self.client.get(
                path=url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
            )
            serializer = EmoticonSerializer(emoticon, context={"user": self.user}).data
            for key, value in serializer.items():
                self.assertEqual(response.data[key], value)
                self.assertEqual(emoticon.title, response.data["title"])

    def test_put_emoticon(self):
        """임시저장 이모티콘 수정"""
        response = self.client.put(
            path=reverse("emoticon"),
            data={"emoticon_id": self.emoticon_one.pk, "title": "수정 된 이모티콘"},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_emoticon(self):
        """임시저장 이모티콘 삭제"""
        response = self.client.put(
            path=reverse("emoticon"),
            data={
                "emoticon_id": self.emoticon_one.pk,
                # "remove_images":"" # 스트링으로 보내기
                "title": self.emoticon_one.title,
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )


#         self.assertEqual(response.status_code, 200)


class PaymentTest(APITestCase):
    """이모티콘 구매 테이블 생성"""

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test@test.com",
            "username": "test",
            "password": "test",
        }
        cls.superuser_data = {
            "email": "admin@admin.com",
            "username": "admin",
            "password": "admin",
        }
        cls.user = User.objects.create_user("test@test.com", "test", "test")
        cls.superuser = User.objects.create_superuser(
            "admin@admin.com", "admin", "admin"
        )
        cls.faker = Faker()
        # 이모티콘 더미 데이터 생성(단일)
        cls.emoticon_data = {
            "title": "test emoticon",
            "images": [],
        }
        # 이모티콘 판매승인용
        cls.emoticon_status_data = {
            "emoticon_id": 2,
            "title": "test emoticon",
            "db_status": 1,
        }

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]
        self.superaccess_token = self.client.post(
            reverse("token_obtain_pair"), self.superuser_data
        ).data["access"]

    def test_user_buy_emoticon(self):
        """이모티콘 생성 / 이미지 파일 같이 생성"""
        # 임시 이미지 파일 생성
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.emoticon_data["images"] = image_file

        # 이모티콘 생성 post요청
        rsp_emoticon = self.client.post(
            path=reverse("emoticon"),
            data=encode_multipart(data=self.emoticon_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        # 이모티콘 판매중 상태 변경
        rsp_emoticon_ok = self.client.put(
            path=reverse("emoticon"),
            data=encode_multipart(data=self.emoticon_status_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.superaccess_token}",
        )

        # # 구매 post요청 -> API요청방식으로 변경됨에 따라 테스트코드 불가
        # response = self.client.post(
        #     path=reverse("user_buy_emoticon"),
        #     data={"emoticon_id": 2, "user_id": self.user.pk},
        #     HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        # )

        self.assertEqual(rsp_emoticon_ok.status_code, 200)


class EmoticonListTest(APITestCase):
    """판매중 이모티콘 전체 조회"""

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test@test.com",
            "username": "test",
            "password": "test",
        }
        cls.user = User.objects.create_user("test@test.com", "test", "test")
        cls.faker = Faker()
        # 이모티콘 더미 데이터 생성(다수)
        cls.emoticons = []
        for i in range(10):
            if i % 2 == 0:
                cls.user_faker = User.objects.create_user(
                    cls.faker.email(), cls.faker.name(), cls.faker.word()
                )
                cls.emoticons.append(
                    Emoticon.objects.create(
                        creator=cls.user_faker, title=cls.faker.word(), db_status=1
                    )  # 판매중
                )
            else:
                cls.user_faker = User.objects.create_user(
                    cls.faker.email(), cls.faker.name(), cls.faker.word()
                )
                cls.emoticons.append(
                    Emoticon.objects.create(
                        creator=cls.user_faker, title=cls.faker.word(), db_status=0
                    )  # 임시저장
                )

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    def test_emoticon_list_all(self):
        """판매중 이모티콘 전체 가져오기"""
        # 이모티콘 조회 get요청
        rsp_emoticon_list = self.client.get(
            path=reverse("emoticon_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        # for i, a in enumerate(rsp_emoticon_list.data):

        self.assertEqual(rsp_emoticon_list.status_code, 200)


class EmoticonTempListTest(APITestCase):
    """판매중 이모티콘 전체 조회"""

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test@test.com",
            "username": "test",
            "password": "test",
        }
        cls.superuser_data = {
            "email": "admin@admin.com",
            "username": "admin",
            "password": "admin",
        }
        cls.user = User.objects.create_user("test@test.com", "test", "test")
        cls.superuser = User.objects.create_superuser(
            "admin@admin.com", "admin", "admin"
        )
        cls.faker = Faker()
        # 이모티콘 더미 데이터 생성(다수)
        cls.emoticons = []
        for i in range(10):
            if i % 2 == 0:
                cls.user_faker = User.objects.create_user(
                    cls.faker.email(), cls.faker.name(), cls.faker.word()
                )
                cls.emoticons.append(
                    Emoticon.objects.create(
                        creator=cls.user_faker, title=cls.faker.word(), db_status=1
                    )  # 판매중
                )
            else:
                cls.user_faker = User.objects.create_user(
                    cls.faker.email(), cls.faker.name(), cls.faker.word()
                )
                cls.emoticons.append(
                    Emoticon.objects.create(
                        creator=cls.user_faker, title=cls.faker.word(), db_status=0
                    )  # 임시저장
                )
        cls.emoticons.append(
            Emoticon.objects.create(
                creator=cls.user, title=cls.faker.word(), db_status=0
            )  # request.user의 임시저장
        )

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]
        self.superaccess_token = self.client.post(
            reverse("token_obtain_pair"), self.superuser_data
        ).data["access"]

    def test_emoticon_list_all_user(self):
        """임시저장중 이모티콘 가져오기"""
        # 일반유저 이모티콘 조회 get요청
        rsp_emoticon_list = self.client.get(
            path=reverse("emoticon_temp_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        # for i, a in enumerate(rsp_emoticon_list.data):
        self.assertEqual(rsp_emoticon_list.status_code, 200)

    def test_emoticon_list_all_superuser(self):
        """임시저장중 이모티콘 가져오기"""
        # 관리자유저 이모티콘 조회 get요청
        rsp_emoticon_list = self.client.get(
            path=reverse("emoticon_temp_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.superaccess_token}",
        )
        # for i, a in enumerate(rsp_emoticon_list.data):
        self.assertEqual(rsp_emoticon_list.status_code, 200)
