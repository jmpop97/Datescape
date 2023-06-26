from django.contrib import admin
from reports.models import (
    ReportUser,
    ReportArticle,
    ReportComment,
    CategoryName,
    ChildCategory,
    ParentCategory,
)
from users.admin import CommonModelAdmin


class ReportUserAdmin(admin.ModelAdmin):
    fields = (
        "reporter",
        "report_user",
        "report_type",
        "comment",
        "db_status",
        "created_at",
        "updated_at",
    )
    list_display = (
        "id",
        "reporter",
        "report_user",
        "report_type",
        "db_status",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("reporter", "report_user", "created_at", "updated_at")
    list_filter = (
        "report_user",
        "report_type",
        "db_status",
        "created_at",
    )
    list_display_links = ["id", "reporter", "report_user"]
    list_per_page = 10
    actions = ["make_solved"]

    # admin action 추가
    def make_solved(self, request, queryset):
        updated_count = queryset.update(db_status=2)  # queryset.update
        self.message_user(
            request, "{}건의 항목을 해결됨 상태로 변경".format(updated_count)
        )  # django message framework 활용

    make_solved.short_description = "지정 항목을 해결됨 상태로 변경"


class ReportArticleAdmin(admin.ModelAdmin):
    fields = (
        "reporter",
        "report_article",
        "report_type",
        "comment",
        "db_status",
        "created_at",
        "updated_at",
    )
    list_display = (
        "id",
        "reporter",
        "report_article",
        "report_type",
        "db_status",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("reporter", "report_article", "created_at", "updated_at")
    list_filter = (
        "report_article",
        "report_type",
        "db_status",
        "created_at",
    )
    list_display_links = ["id", "reporter", "report_article"]
    list_per_page = 10
    actions = ["make_solved"]

    # admin action 추가
    def make_solved(self, request, queryset):
        updated_count = queryset.update(db_status=2)  # queryset.update
        self.message_user(
            request, "{}건의 항목을 해결됨 상태로 변경".format(updated_count)
        )  # django message framework 활용

    make_solved.short_description = "지정 항목을 해결됨 상태로 변경"


class ReportCommentAdmin(admin.ModelAdmin):
    fields = (
        "reporter",
        "report_comment",
        "report_type",
        "comment",
        "db_status",
        "created_at",
        "updated_at",
    )
    list_display = (
        "id",
        "reporter",
        "report_comment",
        "report_type",
        "db_status",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("reporter", "report_comment", "created_at", "updated_at")
    list_filter = (
        "report_comment",
        "report_type",
        "db_status",
        "created_at",
    )
    list_display_links = ["id", "reporter", "report_comment"]
    list_per_page = 10
    actions = ["make_solved"]

    # admin action 추가
    def make_solved(self, request, queryset):
        updated_count = queryset.update(db_status=2)  # queryset.update
        self.message_user(
            request, "{}건의 항목을 해결됨 상태로 변경".format(updated_count)
        )  # django message framework 활용

    make_solved.short_description = "지정 항목을 해결됨 상태로 변경"


class ChildCategoryAdmin(CommonModelAdmin):
    fields = ("parent_category", "category", "down_list_num", "riority")
    list_display = ("parent_category", "riority", "category", "down_list_num")
    readonly_fields = ()
    list_filter = ["parent_category"]
    ordering = ["parent_category", "riority"]


admin.site.register(ReportUser, ReportUserAdmin)
admin.site.register(ReportArticle, ReportArticleAdmin)
admin.site.register(ReportComment, ReportCommentAdmin)
admin.site.register(CategoryName)
admin.site.register(ChildCategory, ChildCategoryAdmin)
admin.site.register(ParentCategory)
