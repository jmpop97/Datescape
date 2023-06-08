from django.contrib import admin
from articles.models import (Article, Tag, 
                             Comment, CommentLike, 
                             KakaoMapDataBase)
from users.admin import CommonModelAdmin


# Register your models here.
admin.site.register(Tag)
# admin.site.register(Article)
admin.site.register(KakaoMapDataBase)


class ArticlesAdmin(admin.ModelAdmin):

    list_display = ["id", "title", "content", "score"]
    list_filter = ["title",]
    fieldsets = []

    search_fields = ["title", "content",]
    ordering = ["title"]
    filter_horizontal = []
    list_display_links = ["id", "title", "content",]


admin.site.register(Article, ArticlesAdmin)

class CommentAdmin(CommonModelAdmin):
    fields = ("article", "writer", "comment", "use_emoticon")
    list_display = ("article", "writer", "comment", "use_emoticon")


class CommentLikeAdmin(CommonModelAdmin):
    fields = ("likers", "comment")
    list_display = ("likers", "comment")


admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
