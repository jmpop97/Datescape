from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from users.models import User


class CommonModelAdmin(admin.ModelAdmin):
    """공통모델의 어드민"""

    fields = ()
    list_display = ()
    readonly_fields = ()
    list_filter = ()
    common_list_display = (
        "db_status",
        "created_at",
        "updated_at",
    )
    common_fields = (
        "db_status",
        "created_at",
        "updated_at",
    )
    common_readonly_fields = ("created_at", "updated_at")
    common_list_filter = (
        "db_status",
        "created_at",
    )
    list_per_page = 10
    actions = ["make_active", "make_delete"]

    def __init__(self, model: type, admin_site):
        self.fields += self.common_fields
        self.list_display += self.common_list_display
        self.readonly_fields += self.common_readonly_fields
        self.list_filter += self.common_list_filter
        super().__init__(model, admin_site)

    # admin action 추가
    def make_active(self, request, queryset):
        updated_count = queryset.update(db_status=1)  # queryset.update
        self.message_user(
            request, "{}건의 항목을 Active 상태로 변경".format(updated_count)
        )  # django message framework 활용

    make_active.short_description = "지정 항목을 Active 상태로 변경"

    def make_delete(self, request, queryset):
        updated_count = queryset.update(db_status=2)  # queryset.update
        self.message_user(
            request, "{}건의 항목을 Delete 상태로 변경".format(updated_count)
        )  # django message framework 활용

    make_delete.short_description = "지정 항목을 Delete 상태로 변경"


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["email", "username", "profileimage"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "username",
            "profileimage",
            "is_active",
            "is_admin",
        ]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = [
        "id",
        "login_type",
        "email",
        "username",
        "nickname",
        "profileimage",
        "profileimageurl",
        "is_active",
        "is_admin",
        "last_login",
        "user_status",
    ]
    list_filter = [
        "is_admin",
        "login_type",
        "is_active",
        "user_status",
        "is_admin",
    ]
    list_display_links = ["username", "email", "login_type"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        (
            "Personal info",
            {
                "fields": [
                    "username",
                    "nickname",
                    "profileimage",
                    "profileimageurl",
                    "login_type",
                ]
            },
        ),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_admin",
                    "last_login",
                    "user_status",
                ]
            },
        ),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "username", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["username", "email", "nickname"]
    ordering = ["id"]
    filter_horizontal = []
    list_per_page = 10


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
