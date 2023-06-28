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
    Reply,
)
from users.admin import CommonModelAdmin


class TagListInline(admin.TabularInline):
    model = TagList


class TagListAdmin(admin.ModelAdmin):
    list_display = ["id", "tag", "article"]
    list_display_links = ["id", "tag", "article"]
    search_fields = ["id", "tag", "article"]
    list_per_page = 10


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "user", "content", "score", "db_status","created_at",]
    list_filter = [
        "db_status",
        "created_at",
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
        "user",
        "title",
        "content",
    ]
    extra = 0
    list_per_page = 10
    actions = ["make_active", "make_delete"]

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


class CommentAdmin(CommonModelAdmin):
    fields = ("article", "writer", "comment", "use_emoticon")
    list_display = ("id", "article", "writer", "comment", "use_emoticon")
    list_display_links = [
        "id",
        "article",
        "writer",
        "comment",
    ]


class CommentLikeAdmin(CommonModelAdmin):
    fields = ("likers", "comment")
    list_display = ("likers", "comment")
    list_display_links = [
        "likers",
        "comment",
    ]


class BookMarkAdmin(CommonModelAdmin):
    fields = ("user", "article")
    list_display = ("user", "article")
    list_display_links = [
        "user",
        "article",
    ]


class ReplyAdmin(CommonModelAdmin):
    fields = ("writer", "comment", "content")
    list_display = ("writer", "comment", "content")
    list_display_links = ["writer", "comment", "content"]


class WeeklyTagsAdmin(CommonModelAdmin):
    fields = (
        "id",
        "tag",
    )
    list_display = (
        "id",
        "tag",
    )
    readonly_fields = ("id",)
    list_display_links = ["id", "tag"]


class ArticleImageAdmin(CommonModelAdmin):
    fields = (
        "id",
        "article",
        "image",
    )
    list_display = (
        "id",
        "article",
        "image",
    )
    readonly_fields = ("id",)
    list_display_links = [
        "id",
        "article",
    ]


class MapDataBaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "jibun_address",
    )
    list_display_links = [
        "id",
        "jibun_address",
    ]
    search_fields = [
        "jibun_address",
        "road_address",
    ]
    list_per_page = 10


class TagAdmin(CommonModelAdmin):
    list_display = ["id", "tag"]
    list_display_links = ["id", "tag"]
    search_fields = ["tag"]
    list_per_page = 10


admin.site.register(Tag, TagAdmin)
admin.site.register(WeeklyTags, WeeklyTagsAdmin)
admin.site.register(MapDataBase, MapDataBaseAdmin)
admin.site.register(TagList, TagListAdmin)
admin.site.register(Article, ArticlesAdmin)
admin.site.register(ArticleImage, ArticleImageAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
admin.site.register(BookMark, BookMarkAdmin)
admin.site.register(Reply, ReplyAdmin)
