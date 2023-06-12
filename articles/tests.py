from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from faker import Faker
from articles.models import Article
from articles.serializers import ArticleSerializer


# 아티클 CRUD 테스트
class ArticleAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"username": "test2", "password": "test"}
        cls.article_data = {
            "title": "testcase",
            "content": "testcode",
        }
        cls.user = User.objects.create_user("test2@test.com", "test2", "test")

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    # 전체 아티클 불러오기 테스트
    def test_articlelist(self):
        url = reverse("article_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # 로그인 안 되어 있을 때 글 작성
    # def test_fail_if_not_login(self):
    #     url = reverse("search_map")
    #     response = self.client.post(url, self.article_data)
    #     self.assertEqual(response.status_code, 400)

    # 글 작성하기 테스트/이미지없음
    def test_create_article(self):
        response = self.client.post(
            path=reverse("search_map"),
            data=self.article_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)


class ArticleDetailAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"username": "test2", "password": "test"}
        cls.articles = []
        cls.user = User.objects.create_user("test2@test.com", "test2", "test")
        cls.faker = Faker()
        for i in range(10):
            cls.articles.append(
                Article.objects.create(
                    user=cls.user, title=cls.faker.sentence(), content=cls.faker.text()
                )
            )

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    # 글 상세보기 테스트
    # def test_article_detail(self):
    #     for article in self.articles:
    #         url = article.get_absolute_url()
    #         response = self.client.get(url)
    #         serializer = ArticleSerializer(article)
    #         for key, value in serializer.items():
    #             self.assertEqual(response[key], value)
