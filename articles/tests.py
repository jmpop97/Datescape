from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from faker import Faker
from articles.models import Article, KakaoMapDataBase, Comment, Tag
from articles.serializers import ArticleSerializer
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
from emoticons.models import Emoticon, EmoticonImage
import tempfile


# 임시 이미지 파일 만들기
def get_temporary_image(temp_file):
    size = (200, 200)
    color = (250, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file


# 게시물 CRUD 테스트
class ArticleAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"username": "test2", "password": "test"}
        cls.article_data = {
            "title": "testcase",
            "content": "testcode",
            "score": 4,
            "query": "서울 구로구 가마산로 245",
            "tags": "#안녕#hi",
        }
        cls.user = User.objects.create_user("test2@test.com", "test2", "test")

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    # 전체 게시물 불러오기
    def test_articlelist(self):
        url = reverse("article_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # 이미지 없는 글 작성하기
    def test_create_article(self):
        response = self.client.post(
            path=reverse("search_map"),
            data=self.article_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 이미지 있는 글 작성하기
    def test_create_article_with_image(self):
        # 임시 이미지 파일 생성하기
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.article_data["images"] = image_file

        temp_file_2 = tempfile.NamedTemporaryFile()
        temp_file_2.name = "image2.png"
        image_file_2 = get_temporary_image(temp_file_2)
        image_file_2.seek(0)
        self.article_data["images"] = [image_file, image_file_2]
        # 글 작성
        response = self.client.post(
            path=reverse("search_map"),
            data=encode_multipart(data=self.article_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)


# 게시물 상세페이지
class ArticleDetailAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"username": "test2", "password": "test"}
        cls.articles = []
        cls.user = User.objects.create_user("test2@test.com", "test2", "test")
        cls.locaton = KakaoMapDataBase.objects.create(
            jibun_address="경기 평택시 팽성읍 본정리 15-3",
            road_address="경기 평택시 팽성읍 광덕계양로 963",
            coordinate_x=127.014450917838,
            coordinate_y=36.9465596862886,
        )
        cls.faker = Faker()
        for i in range(10):
            cls.articles.append(
                Article.objects.create(
                    user=cls.user,
                    title=cls.faker.sentence(),
                    content=cls.faker.text(),
                    location=cls.locaton,
                )
            )

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    # 글 상세보기
    def test_article_detail(self):
        for article in self.articles:
            url = article.get_absolute_url()
            response = self.client.get(url)
            serializer = ArticleSerializer(article).data
            for key, value in serializer.items():
                self.assertEqual(response.data[key], value)
            self.assertEqual(response.status_code, 200)

    # 글 수정하기 테스트
    # def test_update_article(self):
    #     # 임시 이미지 파일 생성하기
    #     temp_file = tempfile.NamedTemporaryFile()
    #     temp_file.name = 'image.png'
    #     image_file = get_temporary_image(temp_file)
    #     image_file.seek(0)
    #     # 수정
    #     for article in self.articles:
    #         url = article.get_absolute_url()
    #         response = self.client.put(
    #             path=url,
    #             data=encode_multipart(data={
    #         "title": "updatetest",
    #         "content": "update",
    #         "score":4}, boundary=BOUNDARY),
    #             content_type=MULTIPART_CONTENT,
    #             HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
    #         )
    #         self.assertEqual(response.status_code, 200)


# 댓글 CRUD/좋아요 테스트
class CommentAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"username": "test2", "password": "test"}
        cls.user = User.objects.create_user("test2@test.com", "test2", "test")
        cls.writer = User.objects.create_user("test@test.com", "test", "test")
        cls.locaton = KakaoMapDataBase.objects.create(
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
        cls.comment_data = {
            "comment": "comment test",
        }
        cls.comment = Comment.objects.create(
            article=cls.article, writer=cls.user, comment="comment test"
        )
        cls.emoticon_data = {
            "title": "test emoticon",
            "images": [],
            "db_status_choice": 0,
            "db_status": 1,
        }

    def setUp(self):
        self.access_token = self.client.post(
            reverse("token_obtain_pair"), self.user_data
        ).data["access"]

    # 댓글 가져오기
    def test_get_comment(self):
        url = reverse("comment_view", kwargs={"article_id": self.article.id})
        response = self.client.get(
            path=url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 200)

    # 댓글 작성하기
    def test_create_comment(self):
        url = reverse("comment_view", kwargs={"article_id": self.article.id})
        response = self.client.post(
            path=url,
            data=self.comment_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 이모티콘 있는 댓글 작성하기
    def test_create_comment_with_emoticon(self):
        # 임시 이모티콘 생성
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "emoticon.png"
        emoticon_file = get_temporary_image(temp_file)
        emoticon_file.seek(0)
        self.emoticon_data["images"] = emoticon_file

        emoticon = self.client.post(
            path=reverse("emoticon"),
            data=encode_multipart(data=self.emoticon_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.comment_data["use_emoticon"] = 9

        url = reverse("comment_view", kwargs={"article_id": self.article.id})
        response = self.client.post(
            path=url,
            data=self.comment_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 댓글 수정하기
    def test_update_comment(self):
        url = reverse("comment_view", kwargs={"article_id": self.article.id})
        response = self.client.put(
            path=url,
            data={
                "comment_id": self.comment.id,
                "comment": "update test",
                "use_emoticon": "",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 댓글 삭제하기
    def test_delete_comment(self):
        url = reverse("comment_view", kwargs={"article_id": self.article.id})
        response = self.client.delete(
            path=url,
            data={"comment_id": self.comment.id},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 204)

    # 댓글 좋아요
    def test_like_comment(self):
        url = reverse("comment_like_view")
        response = self.client.post(
            path=url,
            data={"comment_id": self.comment.id},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.data["message"], "좋아요!")


# 사용자 주변 데이터 가져오기
class LocationListAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"username": "test2", "password": "test"}
        cls.articles = []
        cls.user = User.objects.create_user("test2@test.com", "test2", "test")
        cls.locaton = KakaoMapDataBase.objects.create(
            jibun_address="서울 구로구 구로동 435",
            road_address="서울 구로구 가마산로 245",
            coordinate_x=126.88736266588283,
            coordinate_y=37.49478963186869,
        )
        cls.position = (37.4971139, 126.891002)
        cls.faker = Faker()
        for i in range(5):
            cls.articles.append(
                Article.objects.create(
                    user=cls.user,
                    title=cls.faker.sentence(),
                    content=cls.faker.text(),
                    location=cls.locaton,
                )
            )

    # 반경 2km 내의 데이터 조회
    def test_get_near_articles(self):
        url = f"/articles/location-list/?latitude={self.position[0]}&longitude={self.position[1]}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # 장소 별로 리뷰 받아오기
    def test_get_location_to_article(self):
        url = f"/articles/location-articles/?location={self.locaton.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


# 검색 테스트
class SearchAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"username": "test2", "password": "test"}
        cls.articles = []
        cls.user = User.objects.create_user("test2@test.com", "test2", "test")
        cls.tag1 = Tag.objects.create(tag="안녕")
        cls.tag2 = Tag.objects.create(tag="hello")
        cls.tag3 = Tag.objects.create(tag="hi")
        cls.articles_data = [
            {
                "title": "testcase",
                "content": "testcode",
                "score": 4,
                "tags": [cls.tag1.id, cls.tag2.id],
            },
            {
                "title": "case",
                "content": "code",
                "score": 5,
                "tags": [cls.tag3.id, cls.tag2.id],
            },
            {
                "title": "testcase",
                "content": "testcode",
                "score": 5,
                "tags": [cls.tag1.id, cls.tag3.id],
            },
        ]
        cls.locaton = KakaoMapDataBase.objects.create(
            jibun_address="서울 구로구 구로동 435",
            road_address="서울 구로구 가마산로 245",
            coordinate_x=126.88736266588283,
            coordinate_y=37.49478963186869,
        )
        for i in cls.articles_data:
            cls.article = Article.objects.create(
                user=cls.user,
                title=i["title"],
                content=i["content"],
                score=i["score"],
                location=cls.locaton,
            )
            cls.article.tags.set(i["tags"])
            cls.articles.append(cls.article)

    # 글 검색하기
    def test_search_article(self):
        url = f"/articles/article-search/?option=article&search=test"
        response = self.client.get(url)
        for data in response.data["results"]:
            self.assertEqual(data["title"], "testcase")
        self.assertEqual(response.status_code, 200)

    # 태그 검색하기
    def test_search_article(self):
        url = f"/articles/article-search/?option=tage&search=hi"
        response = self.client.get(url)
        for data in response.data["results"]:
            self.assertEqual(data["score"], 5)
        self.assertEqual(response.status_code, 200)
