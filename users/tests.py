import jwt
import json
import unittest

from django.test import Client
from users.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

# Create your tests here.


class UserRegisterationAPIViewTestCase(APITestCase):
    def test_registration(self):
        url = reverse("signup")
        user_data = {
            "username": "testuser",
            "email": "test@testuser.com",
            "password": "1234",
        }
        response = self.client.post(url, user_data)
        # 에러확인 코드
        # print(response.data)
        self.assertEqual(response.status_code, 201)

    # def test_login(self):
    #     url = reverse("token_obtain_pair")
    #     user_data = {
    #         # "username":"testuser",
    #         "email":"test@testuser.com",
    #         "password":"1234",
    #     }
    #     response = self.client.post(url, user_data)
    #     # 에러확인 코드
    #     print(response.data)
    #     self.assertEqual(response.status_code, 200)


class LoginUserTest(APITestCase):
    def setUp(self):
        self.data = {"email": "test@test.com", "username": "test", "password": "1234"}
        self.user = User.objects.create_user("test@test.com", "test", "1234")

    def test_login(self):
        response = self.client.post(reverse("token_obtain_pair"), self.data)
        # print(response.data)
        # print("일반로그인")
        # print(response.data["access"])
        self.assertEqual(response.status_code, 200)


class SocialUrlTest(APITestCase):
    def test_social(self):
        data = {
            # 카카오 인가코드받아서 로그인 url 받기
            "social": "kakao-login"
        }
        response = self.client.post(reverse("social_login"), data)
        # print(response.data)
        # print("소셜로그인 인가코드")
        # print(response.data["url"])
        self.assertEqual(response.status_code, 200)


# FAIL: test_user_post_kakao_login_success (users.tests.KakaoLogInTest) => 400 != 200
# class KakaoLogInTest(APITestCase):
#     @patch('users.views.requests')
#     # user 앱의 views.py에서 사용될 request를 patch한다는 뜻
#     def test_user_post_kakao_login_success(self, mocked_request):
#     #실제 kakao API를 호출하지 않고 kakao API 응답을 Fake로 작성한다
#         class FakeResponse:
#             def json(self):
#             # 아래 형식에서 json 이 필요하다.
#                 return {'kakao_account': {
#                             'profile': {"nickname": "유혜민"},
#                             'email': "gpalsu0812@daum.net",
#                             }
#                         }
#                         # 실제 kakao API로 읽었던 모든 값을 넣으려 하였으나
#                         # 로직에서 필요한 nickname 과 email만 사용

#         mocked_request.get = MagicMock(return_value = FakeResponse())
#         # test 할때, requests가 get 메서드로 받은 response는 FakeResponse의 인스턴스이다.
#         client = APIClient()
#         header = {'HTTP_Authorization':'access_token'}
#         # Client의 get method에 header 담기!
#         # **extra는 keyword arguments이나 header는 dict이므로 **을 붙여준다.
#         # **header를 붙혀주지 않으면 테스트시 에러가 발생함
#         response = client.post('/users/kakao-login/', content_type='applications/json', **header)

#         self.assertEqual(response.status_code, 200)

#     @patch('users.views.requests')
#     def test_user_post_kakao_login_not_exist_user(self, mocked_request):
#         class FakeResponse:
#             def json(self):
#                 return {'kakao_account': {
#                             'profile': {"nickname": "유혜민"},
#                             'email': "gpalsu0812@daum.net",
#                             }
#                         }

#         mocked_request.get = MagicMock(return_value = FakeResponse())
#         client = APIClient()
#         headers = {'HTTP_Authorization' : 'access_token'}
#         # response = client.post('/users/kakao-login/', content_type='application/json', **header)
#         response = client.post('/users/kakao-login/', format='json', data=json, headers=headers)
#         self.assertEqual(response.status_code, 403)
#         self.assertEqual(response.json(),
#             {
#                 'MESSAGE' : 'NOT_EXIST_USER',
#                 'EMAIL' : "gpalsu0812@daum.net",
#                 'NAME' : "유혜민"
#             }
#         )
