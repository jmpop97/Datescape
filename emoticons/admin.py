from django.contrib import admin
from emoticons.models import Emoticon, EmoticonImage, UserEmoticonList, EmoticonPrice
from users.admin import CommonModelAdmin


# Register your models here.
class EmoticonAdmin(CommonModelAdmin):
    fields = ("creator", "title")
    list_display = ("creator", "title")


class EmoticonImageAdmin(CommonModelAdmin):
    fields = ("emoticon", "image", "size")
    list_display = ("emoticon", "image", "size")


class UserEmoticonListAdmin(CommonModelAdmin):
    fields = ("buyer", "sold_emoticon")
    list_display = ("buyer", "sold_emoticon")


class EmoticonPriceAdmin(CommonModelAdmin):
    fields = ("price", "emoticon_size_start", "emoticon_size_limit")
    list_display = ("price", "emoticon_size_start", "emoticon_size_limit")


admin.site.register(Emoticon, EmoticonAdmin)
admin.site.register(EmoticonImage, EmoticonImageAdmin)
admin.site.register(UserEmoticonList, UserEmoticonListAdmin)
admin.site.register(EmoticonPrice, EmoticonPriceAdmin)
