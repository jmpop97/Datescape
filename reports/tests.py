from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from faker import Faker
from articles.models import Article, MapDataBase, Comment, Tag
from articles.serializers import ArticleSerializer
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
from emoticons.models import Emoticon, EmoticonImage
import tempfile


class ReportsAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"username": "test2", "password": "test"}
        cls.user = User.objects.create_user("test2@test.com", "test2", "test")
        cls.writer = User.objects.create_user("test@test.com", "test", "test")
        cls.locaton = MapDataBase.objects.create(
            jibun_address="경기 평택시 팽성읍 본정리 15-3",
            road_address="경기 평택시 팽성읍 광덕계양로 963",
            coordinate_x=127.014450917838,
            coordinate_y=36.9465596862886,
        )
        cls.article = Article.objects.create(
            user=cls.writer,
            title="testcase",
            content="testcode",
            score=4,
            location=cls.locaton,
        )
        cls.comment = Comment.objects.create(
            article=cls.article, writer=cls.writer, comment="comment test"
        )

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    # 신고하기
    def test_report(self):
        response = self.client.post(
            path=reverse("report"),
            data={"request_type": "article", "report_id": 1},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
