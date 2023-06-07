from django.contrib import admin
from articles.models import Article, Tag, Comment
# Register your models here.
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(Comment)


# class ArticlesAdmin(admin.ModelAdmin):

#     list_display = ["id", "title", "content", "score"]
#     list_filter = ["title",]
#     fieldsets = []

#     search_fields = ["title", "content",]
#     ordering = ["title"]
#     filter_horizontal = []
#     list_display_links = ["id", "title", "content",]


# admin.site.register(Article, ArticlesAdmin)
