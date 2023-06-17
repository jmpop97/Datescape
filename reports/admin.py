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


# Register your models here.
class ReportUserAdmin(CommonModelAdmin):
    fields = ("reporter", "report_user", "report_type", "comment")
    list_display = ("id", "reporter", "report_user", "report_type")
    readonly_fields = ("reporter", "report_user")
    list_filter = ("report_user", "report_type")


class ReportArticleAdmin(CommonModelAdmin):
    fields = ("reporter", "report_article", "report_type", "comment")
    list_display = ("id", "reporter", "report_article", "report_type")
    readonly_fields = ("reporter", "report_article")
    list_filter = ("report_article", "report_type")


class ReportCommentAdmin(CommonModelAdmin):
    fields = ("reporter", "report_comment", "report_type", "comment")
    list_display = ("id", "reporter", "report_comment", "report_type")
    readonly_fields = ("reporter", "report_comment")
    list_filter = ("report_comment", "report_type")


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
