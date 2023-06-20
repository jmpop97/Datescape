from django.contrib import admin
from articles.models import (
    Article,
    ArticleImage,
    Tag,
    TagList,
    Comment,
    CommentLike,
    MapDataBase,
    WeeklyTags,
    BookMark,
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


class BookMarkAdmin(CommonModelAdmin):
    fields = ("user", "article")
    list_display = ("user", "article")


admin.site.register(Tag)
admin.site.register(WeeklyTags)
admin.site.register(MapDataBase)
admin.site.register(TagList, TagListAdmin)
admin.site.register(Article, ArticlesAdmin)
admin.site.register(ArticleImage)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
admin.site.register(BookMark, BookMarkAdmin)
