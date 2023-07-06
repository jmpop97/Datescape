from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from emoticons.serializers import (
    EmoticonSerializer,
    EmoticonCreateSerializer,
    EmoticonImageSerializer,
)
from users.serializers import UserSerializer
from emoticons.models import Emoticon, EmoticonImage, UserEmoticonList
from users.models import User
from dsproject import settings
import requests
import json


# 포트원 토큰 요청
def getTokenApi(path):
    API_HOST = "https://api.iamport.kr"
    url = API_HOST + path

    headers = {"Content-Type": "application/json", "charset": "UTF-8", "Accept": "*/*"}
    body = {
        "imp_key": settings.PORTONE_REST_API_KEY,  # REST API Key
        "imp_secret": settings.PORTONE_REST_API_SECRET,  # REST API Secret
    }
    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(body, ensure_ascii=False, indent="\t")
        )
        return response
    except Exception as ex:
        # 포트원 공식문서 사용법 가져온거라 익셉트로 빠지는 경우 위치확인용으로 프린트 남겼습니다.
        print(
            "포트원 토큰 요청 에러\n/emoticons/views.py/getTokenApi(path) - 17번째 줄, 또는 사용된 위치에서 에러 발생"
        )


# Create your views here.
class EmoticonView(APIView):
    """
    사용자가 구매한 이모티콘 조회 / 이모티콘 제작 / 임시저장 이모티콘 수정 / 삭제

    사용자가 구매한 이모티콘 조회 및 이모티콘 제작 요청을 처리합니다.
    이모티콘 제작요청시 임시저장상태로 저장되며 임시저장상태에서는 수정 및 삭제가 가능합니다.
    로그인 권한이 요구됩니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        사용자가 구매한 이모티콘을 조회합니다.

        input: 로그인 상태
        output: db_status=1, 사용자가 구매한 이모티콘 객체들을 Response
        """
        emoticon = UserEmoticonList.objects.filter(
            db_status=1, buyer=request.user
        ).order_by("-created_at")
        qs = []
        for a in emoticon:
            qs.append(a.sold_emoticon)
        qs.append(Emoticon.objects.get(title="기본"))

        serializer = EmoticonSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        이모티콘 제작 요청을 처리합니다.

        이모티콘 제작시 사용될 이미지들과 함께 저장할 수 있도록 작성됐습니다.
        프론트에서 보내는 data에 images를 필수로 받을 수 있도록 구현했습니다.
        input: 이모티콘 제목(title)
        output: 요청 처리에 따라 status 값을 반환
        """
        if "db_status" in request.data:
            return Response(
                {"message": "수정할 수 없는 정보가 포함되어 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        if "images" in request.data:
            serializer = EmoticonCreateSerializer(
                data=request.data,
                context={
                    "images": request.data.getlist("images"),
                    "file_size": request.data.getlist("file_size"),
                },
            )
        else:
            serializer = EmoticonCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        임시저장된 이모티콘 수정 요청을 처리합니다.

        request.data에 emoticon_id값을 같이 받아옵니다.
        input: 수정하고자 하는 이모티콘 id, 제목, 이미지
        output: 요청 처리에 따라 status 값을 반환
        """
        if "creator" in request.data:
            return Response(
                {"message": "수정할 수 없는 정보가 포함되어 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        if request.user.is_admin == 0:
            if "db_status" in request.data:
                return Response(
                    {"message": "수정할 수 없는 정보가 포함되어 있습니다."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            emoticon = get_object_or_404(
                Emoticon, id=request.data.get("emoticon_id"), db_status=0
            )
            """404에러 프론트에서 '판매중으로 수정할 수 없거나 등록되지 않은 이모티콘입니다' 메세지 띄우기"""
            # 프론트 데이터 형식
        else:
            emoticon = get_object_or_404(Emoticon, id=request.data.get("emoticon_id"))

        if emoticon.db_status == 0:
            remove_ids = request.data.get("remove_images")
            if remove_ids:
                ids_list = remove_ids.split(",")
            else:
                ids_list = []

            if (request.user == emoticon.creator) or (request.user.is_admin == 1):
                if "images" in request.data:
                    serializer = EmoticonSerializer(
                        emoticon,
                        data=request.data,
                        context={
                            "images": request.data.getlist("images"),
                            "file_size": request.data.getlist("file_size"),
                        },
                    )
                else:
                    serializer = EmoticonSerializer(emoticon, data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    # 제거할 이미지가 있으면 제거해주는 코드
                    if ids_list != None:
                        for id in ids_list:
                            k = EmoticonImage.objects.get(id=id)
                            k.db_status = 2
                            k.save()

                    # 이미지 업로드시 생성, 이모티콘에 추가
                    images_data = serializer.context.get("images", None)
                    file_size_data = serializer.context.get("file_size", None)
                    if images_data:
                        for i, image_data in enumerate(images_data):
                            EmoticonImage.objects.create(
                                emoticon=emoticon,
                                image=image_data,
                                size=file_size_data[i],
                            )
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"message": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"message": "상품등록 이전 상태일때만 수정이 가능합니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def delete(self, request):
        """
        임시저장된 이모티콘 삭제 요청을 처리합니다.

        request.data에 emoticon_id값을 같이 받아옵니다.
        input: 로그인 권한
        output: 요청 처리에 따라 status 값을 반환
        """
        emoticon = get_object_or_404(
            Emoticon, id=request.data["emoticon_id"], db_status=0
        )

        # 작성자만 삭제 가능하게
        if request.user == emoticon.creator:
            if emoticon.db_status == 0:
                emoticon.db_status = 3
                emoticon.save()
                return Response(
                    {"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
                )
            else:
                Response(
                    {"message": "상품 등록 된 이모티콘은 수정이 불가능합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)


class EmoticonDetailView(APIView):
    """
    이모티콘 상세보기

    이모티콘 객체 상세보기 요청을 처리합니다.
    로그인 권한이 요구되며 수정 / 삭제는 요청하는 사용자와 이모티콘 제작자가 동일한 경우에만 허용됩니다.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, emoticon_id):
        """
        이모티콘 상세보기 요청을 처리합니다.

        판매중 상태의 이모티콘들만 반환합니다.
        input: 로그인 권한
        output: 요청 처리에 따라 status 값을 반환
        """
        emoticon = get_object_or_404(Emoticon, id=emoticon_id)
        serializer = EmoticonSerializer(emoticon, context={"user": request.user})
        if (emoticon.db_status == 0) or (emoticon.db_status == 1):
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "상품 등록 대기중인 이모티콘 입니다!"}, status=status.HTTP_403_FORBIDDEN
            )


class EmoticonListView(APIView):
    """
    전체 이모티콘 조회

    판매중인 전체 이모티콘 조회 요청을 처리합니다.
    판매중 상태의 이모티콘 객체들을 반환합니다.
    """

    def get(self, request):
        """
        판매중인 전체 이모티콘 조회 요청을 처리합니다.

        output: 요청 처리에 따라 data와 status 값을 반환
        """
        emoticon_list = Emoticon.objects.filter(db_status=1).order_by("-created_at")
        serializer = EmoticonSerializer(emoticon_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmoticonCreatorListView(APIView):
    """
    제작자별 이모티콘 보기

    판매중인 이모티콘 중 제작자별 조회 요청을 처리합니다.
    제작자의 판매중 상태인 이모티콘 객체들을 반환합니다.
    """

    def get(self, request, creator_id, nickname):
        """
        제작자의 판매중인 이모티콘 조회 요청을 처리합니다.

        output: 요청 처리에 따라 data와 status 값을 반환
        """
        nickname = nickname
        if nickname == "null":
            if creator_id == 0:
                emoticon_list = Emoticon.objects.filter(creator=None)
                serializer = EmoticonSerializer(emoticon_list, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                creator = get_object_or_404(User, id=creator_id)
                emoticon_list = Emoticon.objects.filter(
                    db_status=1, creator=creator
                ).order_by("-created_at")
                serializer = EmoticonSerializer(emoticon_list, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif nickname == "nickname":
            qs = []
            emoticon_list = Emoticon.objects.filter(db_status=1).order_by("-created_at")
            for a in emoticon_list:
                if a.creator:
                    if a.creator in qs:
                        pass
                    else:
                        qs.append(a.creator)
            serializer = UserSerializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class EmoticonTempListView(APIView):
    """
    임시저장 이모티콘 조회

    임시저장(유저가 제작 신청 한) 이모티콘 조회 요청을 처리합니다.
    로그인 권한이 요구되며 요청하는 사용자의 임시저장 이모티콘 객체들을 반환합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        임시저장 이모티콘 조회 요청을 처리합니다.

        요청하는 유저가 제작 신청 한 이모티콘 리스트를 반환합니다.
        관리자인 경우 신청중인 이모티콘리스트 전체를 반환합니다.
        input: 로그인 권한
        output: 요청 처리에 따라 data와 status 값을 반환
        """
        if request.user.is_admin == 1:  # 관리자인 경우
            emoticon_list = Emoticon.objects.filter(db_status=0).order_by("-created_at")
            serializer = EmoticonSerializer(emoticon_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.user.is_admin == 0:  # 일반 유저인 경우
            emoticon_list = Emoticon.objects.filter(
                db_status=0, creator=request.user
            ).order_by("-created_at")
            serializer = EmoticonSerializer(emoticon_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserEmoticonListView(APIView):
    """ """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """ """
        emoticon = get_object_or_404(
            Emoticon, id=int(request.data["emoticon_id"]), db_status=1
        )
        # 포트원 access token
        res = getTokenApi("/users/getToken")  # API call
        json_object = json.loads(res.text)  # json 객체로 변환
        TokenVal = json_object["response"]["access_token"]  # 토큰값 파싱

        # 포트원 결제 조회
        imp_uid = request.data["imp_uid"]
        headers = {"Authorization": TokenVal}
        response = requests.get(
            f"https://api.iamport.kr/payments/{imp_uid}", headers=headers
        )
        if response.status_code == 200:
            payment_response = response.json()
            if payment_response["response"]["status"] == "paid":
                UserEmoticonList.objects.create(
                    sold_emoticon=emoticon, buyer=request.user
                )
                return Response({"message": "결제 완료!"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "결제 취소 또는 결제실패"},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )
        elif response.status_code == 401:
            return Response(
                {"message": "포트원 request 토큰 오류"},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )
        elif response.status_code == 404:
            return Response(
                {"message": "유효하지 않은 imp_uid"}, status=status.HTTP_402_PAYMENT_REQUIRED
            )
        else:
            return Response(
                {"message": "확인 되지 않는 오류, 포트원 문의 필요"},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )


# 기본 이모티콘 저장
try:
    if Emoticon.objects.filter(title="기본"):
        pass
    else:
        base_emoticon = Emoticon(title="기본", db_status=1)
        base_emoticon.save()
        input_images = [
            "base_emoticon/기본1.png",
            "base_emoticon/기본2.jfif",
            "base_emoticon/기본3.gif",
            "base_emoticon/기본4.png",
            "base_emoticon/기본5.png",
            "base_emoticon/기본6.gif",
            "base_emoticon/기본7.png",
            "base_emoticon/기본8.png",
        ]
        for a in input_images:
            temp = EmoticonImage(emoticon=base_emoticon, image=a)
            temp.save()
except:
    pass


class EmoticonImageView(APIView):
    """이모티콘 이미지 전체"""

    def get(self, request):
        emoticon_images = EmoticonImage.objects.filter(db_status=1)
        serializer = EmoticonImageSerializer(emoticon_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SoldEmoticonCountListView(APIView):
    """관리자/ 판매중+판매중단 이모티콘 리스트 조회"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        판매중+판매중단 이모티콘 리스트 조회(관리자만 조회 가능)
        판매자 지급금 계산을 위한 상품등록 된 이모티콘 리스트 조회
        """
        if request.user:
            # if request.user.is_admin == 1: # 피드백 기간동안 일반유저 오픈
            emoticon_list = Emoticon.objects.all().order_by("-created_at")
            serializer = EmoticonSerializer(emoticon_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "관리자만 접근 가능합니다!"}, status=status.HTTP_403_FORBIDDEN
            )


class SoldEmoticonCountView(APIView):
    """이모티콘 누적 판매량 조회"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, emoticon_id):
        """
        누적 판매량 조회(관리자만 조회 가능)
        판매자 지급금 계산을 위한 판매량 조회
        """
        if request.user:
            # if request.user.is_admin == 1: # 피드백 기간동안 일반유저 오픈
            emoticon = get_object_or_404(Emoticon, id=emoticon_id)
            serializer = EmoticonSerializer(emoticon, context={"user": request.user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "관리자만 접근 가능합니다!"}, status=status.HTTP_403_FORBIDDEN
            )
