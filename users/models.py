from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator, FileExtensionValidator


class CommonModel(models.Model):
    db_status_choice = [
        (1, "active"),
        (2, "delete"),
    ]
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    db_status = models.PositiveIntegerField(choices=db_status_choice, default=1)

    class Meta:
        abstract = True


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, username and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email, username and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    {
        'email',
        'username',
        'password',
        'login_type',
        'profileimage', => 회원가입시에는 기본 프로필 이미지, 로그인후 마이페이지에서 수정
    }
    """

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField("아이디", max_length=50, unique=True)

    nickname = models.CharField("닉네임", max_length=50, null=True, blank=True)
    profileimageurl = models.URLField(blank=True, null=True)
    profileimage = models.ImageField(
        upload_to="profile/",
        blank=True,
        default="profile/default.png",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    )
    LOGIN_TYPE = [
        ("normal", "일반"),
        ("google", "구글"),
        ("kakao", "카카오"),
        ("naver", "네이버"),
        ("github", "깃허브"),
    ]
    login_type = models.CharField(
        "로그인 타입", max_length=10, choices=LOGIN_TYPE, default="normal"
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    User_Status_Type = [("active", "활동중"), ("sleep", "휴면중"), ("delete", "탈퇴")]
    user_status = models.CharField(
        "계정 상태", max_length=10, choices=User_Status_Type, default="active"
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
