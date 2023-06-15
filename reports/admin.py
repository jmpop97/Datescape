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
    fields = ("reporter", "report_user")
    list_display = ("reporter", "report_user")
    readonly_fields = ("reporter", "report_user")


class ReportArticleAdmin(CommonModelAdmin):
    fields = ("reporter", "report_article")
    list_display = ("reporter", "report_article")
    readonly_fields = ("reporter", "report_article")


class ReportCommentAdmin(CommonModelAdmin):
    fields = ("reporter", "report_comment")
    list_display = ("reporter", "report_comment")
    readonly_fields = ("reporter", "report_comment")


class ChildCategoryAdmin(CommonModelAdmin):
    fields = ("parent_category", "category", "down_list_num", "riority")
    list_display = ("parent_category", "riority", "category", "down_list_num")
    readonly_fields = ("parent_category", "category")
    list_filter = ["parent_category"]
    ordering = ["parent_category", "riority"]


admin.site.register(ReportUser, ReportUserAdmin)
admin.site.register(ReportArticle, ReportArticleAdmin)
admin.site.register(ReportComment, ReportCommentAdmin)
admin.site.register(CategoryName)
admin.site.register(ChildCategory, ChildCategoryAdmin)
admin.site.register(ParentCategory)
