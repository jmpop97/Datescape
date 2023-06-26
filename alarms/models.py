from django.db import models
from users.models import User, CommonModel


class Alarm(CommonModel):
    target_user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField("알림 타입", max_length=50)
    type_id = models.IntegerField("타입 아이디")
