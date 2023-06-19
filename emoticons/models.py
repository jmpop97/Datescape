from django.db import models
from users.models import CommonModel, User
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# from users.models import User
# from articles.models import Article


# Create your models here.
def send_emoticon_registration_email(recipient_email, subject, emoticon):
    """
    안내 이메일
    """
    html_message = render_to_string('emoticon_registration.html', {'username': emoticon.creator, 'title': emoticon.title})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, 'datescape2306@gmail.com', [recipient_email], html_message=html_message)


class Emoticon(CommonModel):
    """
    이모티콘 모델입니다.
    1. 클라이언트가 제작, 판매할 수 있습니다.
    2. 이모티콘 제작시 임시저장상태로 반영되며 임시저장상태인 경우 수정 / 삭제처리 가능
        관리자의 승인 후 판매중 상태로 변경 판매중 상태에는 수정 / 삭제 불가
    3. 댓글 작성시 '댓글내용 + 이모티콘' 또는 '이모티콘' 의 작성으로 사용할 수 있습니다.
    4. 사용가능한 이모티콘은 기본 이모티콘 + 구매한 이모티콘입니다.
    Emoticon 객체는 제작자를 의미하는 creator필드, 이모티콘 제목을 의미하는 title필드, 이모티콘 판매상태를 의미하는 status필드로 구성됩니다.
    수정/삭제 여부 방향 결정 필요
    """

    """
    CommonModel의 db_status_choice 오버라이딩
    default = 0
    0 = 임시저장, 1 = 판매중, 2 = 판매중단
    """
    db_status_choice = [
        (0, "신청상태"),
        (1, "판매중"),
        (2, "판매중지"),
        (3, "신청삭제"),
    ]

    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )  # User 삭제시 이모티콘은 유지
    title = models.CharField("이모티콘 제목", max_length=50)
    db_status = models.IntegerField("이모티콘 상태", choices=db_status_choice, default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("emoticon_detail", kwargs={"emoticon_id": self.pk})
    
    def save(self, *args, **kwargs):
        # 인스턴스가 존재하는지 확인(수정인지 확인)
        is_new = self.pk is None
        if not is_new:
            old_status = Emoticon.objects.get(pk=self.pk).db_status
        
        super().save(*args, **kwargs)

        if not is_new:
            if (old_status == 0) and (self.db_status == 1):
                # db_status가 신청상태에서 판매중으로 변경됐을때만 이메일 보내기
                print(self.title)
                subject = '(안내) DateScape 이모티콘 상품 등록 완료 안내'
                send_emoticon_registration_email(self.creator.email, subject, self)


class EmoticonImage(CommonModel):
    """
    이모티콘 이미지 모델입니다.
    하나의 이모티콘 객체에 다중 이미지를 구현하기 위해 사용자가 업로드 한 이미지를 이모티콘 객체에 연결합니다.
    각각의 EmoticonImage객체는 연결되는 이모티콘을 의미하는 emoticon필드, 업로드 한 이미지파일 필드, 파일용량을 의미하는 size필드로 구성됩니다.
    """

    emoticon = models.ForeignKey(
        Emoticon, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        "이미지", upload_to="%Y/%m/", blank=True, default=None
    )  # 필수로 받을지?
    size = models.IntegerField("이미지 용량", default=0)

    def __str__(self):
        return f"{self.emoticon.title} - {self.image}"


class UserEmoticonList(CommonModel):
    """
    이모티콘 구매 테이블 모델입니다.
    클라이언트가 구매한(사용할 수 있는) 이모티콘들을 나타냅니다.
    UserEmoticonList객체는 구매자를 의미하는 buyer필드, 구매한 이모티콘을 의미하는 emoticon필드로 구성됩니다.
    DB를 판매량 조회로 사용하기 위해 유저, 이모티콘 delete_on은 SET_NULL로 채택했습니다.
    """

    buyer = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="emoticon_list", null=True
    )
    sold_emoticon = models.ForeignKey(
        Emoticon, on_delete=models.SET_NULL, related_name="sold_emoticon", null=True
    )

    def __str__(self):
        return f"이모티콘: {self.sold_emoticon} - 사용자: {self.buyer}"


class EmoticonPrice(CommonModel):
    """
    이모티콘 가격 책정 모델입니다.

    독립적인 모델로 이모티콘의 총 용량에 해당하는 가격을 설정하여 저장합니다.
        - 이모티콘에 연결돼있는 이모티콘 이미지 용량들의 총 합을 계산합니다.
        - 이모티콘의 총 용량 속하는 제한값의 가격을 프론트로 보내줍니다.
    """

    emoticon_size_start = models.IntegerField("이미지 총 용량 시작 값(KB) / 이상", default=0)
    emoticon_size_limit = models.IntegerField("이미지 총 용량 제한 값(KB) / 미만", default=0)
    price = models.IntegerField("가격", default=0)

    def __str__(self):
        return f"용량 범위: {self.emoticon_size_start}KB({self.emoticon_size_start/1000}MB)~{self.emoticon_size_limit}KB({self.emoticon_size_limit/1000}MB) / 가격: {self.price}"
