from django.db import models
from users.models import CommonModel, User
from articles.models import Article, Comment


class CategoryName(CommonModel):
    name = models.TextField(default="", blank=True)

    def __str__(self):
        return self.name


class ParentCategory(CommonModel):
    name = models.ForeignKey(
        CategoryName, on_delete=models.SET_NULL, null=True, related_name="parentname"
    )

    def __str__(self):
        return str(self.id) + " - " + self.name.name


class ChildCategory(CommonModel):
    parent_category = models.ForeignKey(
        ParentCategory, on_delete=models.CASCADE, null=True, related_name="childname"
    )
    category = models.ForeignKey(
        CategoryName, on_delete=models.SET_NULL, null=True, related_name="list"
    )
    down_list_num = models.IntegerField(default=0)
    riority = models.IntegerField(default=0)

    def __str__(self):
        return self.category.name


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
    report_type = models.ForeignKey(
        CategoryName, on_delete=models.CASCADE, blank=True, null=True
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
    report_type = models.ForeignKey(
        CategoryName, on_delete=models.CASCADE, blank=True, null=True
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
    report_type = models.ForeignKey(
        CategoryName, on_delete=models.CASCADE, blank=True, null=True
    )
    comment = models.TextField(default="", blank=True)
