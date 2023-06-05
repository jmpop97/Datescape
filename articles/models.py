from django.db import models
from users.models import CommonModel
from emoticons.models import EmoticonImage

# Create your models here.
class Article(CommonModel):
    """
    게시글 모델입니다.
    아직 User모델과합치지않아서 User모델은 주석처리해뒀습니다.
    지도연동부분도 지도연동후에 주석을풀겠습니다.
    """
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=256,)
    content = models.TextField()
    images = models.ImageField(width_field=100,height_field=100,null=True,blank=True)
    score = models.IntegerField(null=True,blank=True)
    # place = models.CharField(max_length=200,null=True,blank=True) #필드를 뭐로 할지 아직 잘 모르겠습니다. 좌표는 숫자라 integer 일 거 같긴 한데 더 만들어보고 정하겠습니다.


    def __str__(self):
        return self.title

class Tag(CommonModel):
    """
    Tag관련 모델입니다.
    """
    tags = models.CharField(max_length=20)
    def __str__(self):
        return self.tags

class TagList(CommonModel):
    """
    Article, Tag

    """
    articles = models.ForeignKey(Article,on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag,on_delete=models.CASCADE)
    def __str__(self):
        return self.articles

class Comment(CommonModel):
    """
    댓글 모델입니다.
    게시글 객체와 일대다 관계를 가집니다.
    Comment객체는 게시글 객체를 의미하는 article필드, 댓글 작성자를 의미하는 writer필드,
    댓글내용의 comment필드, 사용된 이모티콘을 의미하는 use_emoticon필드로 구성됩니다.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    # writer = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField("댓글 내용", blank=True)
    use_emoticon = models.ForeignKey(EmoticonImage, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.comment
        # user연결되면 writer로 변경?

class CommentLike(CommonModel):
    # likers = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment
