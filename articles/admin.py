from django.contrib import admin
from articles.models import (
    Article,
    Tag,
    TagList,
    Comment,
    CommentLike,
    KakaoMapDataBase,
)
from users.admin import CommonModelAdmin


# Register your models here.


class TagListInline(admin.TabularInline):
    model = TagList


class TagListAdmin(admin.ModelAdmin):
    list_display = ["id", "tag", "article"]
    list_display_links = ["id", "tag", "article"]
    search_fields = ["id", "tag", "article"]


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "content", "score"]
    list_filter = [
        "title",
    ]
    fieldsets = []
    inlines = [TagListInline]
    search_fields = [
        "title",
        "content",
    ]
    ordering = ["title"]
    filter_horizontal = []
    list_display_links = [
        "id",
        "title",
        "content",
    ]
    extra = 0


class CommentAdmin(CommonModelAdmin):
    fields = ("article", "writer", "comment", "use_emoticon")
    list_display = ("article", "writer", "comment", "use_emoticon")


class CommentLikeAdmin(CommonModelAdmin):
    fields = ("likers", "comment")
    list_display = ("likers", "comment")


admin.site.register(Tag)
admin.site.register(KakaoMapDataBase)
admin.site.register(TagList, TagListAdmin)
admin.site.register(Article, ArticlesAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
