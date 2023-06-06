from django.db import models
from users.models import CommonModel
# from users.models import User
# from articles.models import Article

# Create your models here.

# 이모티콘 모델
class Emoticon(CommonModel):
    """
    이모티콘 모델입니다.
    1. 클라이언트가 제작, 판매할 수 있습니다.
    2. 댓글 작성시 '댓글내용 + 이모티콘' 또는 '이모티콘' 의 작성으로 사용할 수 있습니다.
    3. 사용가능한 이모티콘은 기본 이모티콘 + 구매한 이모티콘입니다.
    Emoticon 객체는 제작자를 의미하는 creator필드, 이모티콘 제목을 의미하는 title필드로 구성됩니다.
    수정/삭제 여부 방향 결정 필요
    """
    # creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)                   # User 삭제시 이모티콘은 유지
    title = models.CharField("이모티콘 제목", max_length=50)

    def __str__(self):
        return self.title

# 이모티콘 이미지 모델
class EmoticonImage(CommonModel):
    """
    이모티콘 이미지 모델입니다.
    하나의 이모티콘 객체에 다중 이미지를 구현하기 위해 사용자가 업로드 한 이미지를 이모티콘 객체에 연결합니다.
    각각의 EmoticonImage객체는 연결되는 이모티콘을 의미하는 emoticon필드, 업로드 한 이미지파일 필드로 구성됩니다.
    """
    emoticon = models.ForeignKey(Emoticon, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField("이미지", upload_to='%Y/%m/', blank=True, default=None)           # 필수로 받을지?

    def __str__(self):
        return self.emoticon.title

# 이모티콘 구매 테이블
class UserEmoticonList(CommonModel):
    """
    이모티콘 구매 테이블 모델입니다.
    클라이언트가 구매한(사용할 수 있는) 이모티콘들을 나타냅니다. 
    UserEmoticonList객체는 구매자를 의미하는 buyer필드, 구매한 이모티콘을 의미하는 emoticon필드로 구성됩니다.
    """
    # buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emoticon_list')
    sold_emoticon = models.ForeignKey(Emoticon, on_delete=models.CASCADE, related_name='sold_emoticon')

    def __str__(self):
        return f'이모티콘: {self.emoticon}//사용자: {self.buyer}'
