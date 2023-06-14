from django.db import models
from users.models import CommonModel, User
from articles.models import Article, Comment



class ReportUser(CommonModel):
    """유저 신고
    db_status={1:처리 안됨,2:해결됨}
    """

    db_status_choice = [
        (1, "처리 안됨"),
        (2, "해결됨"),
    ]
    db_status = models.PositiveIntegerField(choices=db_status_choice, default=1)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reported"
    )
    comment = models.TextField(default="", blank=True)


class ReportArticle(CommonModel):
    """유저 신고
    db_status={1:처리 안됨,2:해결됨}
    """

    db_status_choice = [
        (1, "처리 안됨"),
        (2, "해결됨"),
    ]
    db_status = models.PositiveIntegerField(choices=db_status_choice, default=1)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="reported"
    )
    comment = models.TextField(default="", blank=True)


class ReportComment(CommonModel):
    """유저 신고
    db_status={1:처리 안됨,2:해결됨}
    """

    db_status_choice = [
        (1, "처리 안됨"),
        (2, "해결됨"),
    ]
    db_status = models.PositiveIntegerField(choices=db_status_choice, default=1)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="reported"
    )
    comment = models.TextField(default="", blank=True)
