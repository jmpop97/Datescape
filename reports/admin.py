from django.contrib import admin
from reports.models import ReportUser, ReportArticle, ReportComment
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


admin.site.register(ReportUser, ReportUserAdmin)
admin.site.register(ReportArticle, ReportArticleAdmin)
admin.site.register(ReportComment, ReportCommentAdmin)
