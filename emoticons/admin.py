from django.contrib import admin
from emoticons.models import Emoticon, EmoticonImage, UserEmoticonList
from users.admin import CommonModelAdmin


# Register your models here.
class EmoticonAdmin(CommonModelAdmin):
    fields = ("creator", "title")
    list_display = ("creator", "title")


class EmoticonImageAdmin(CommonModelAdmin):
    fields = ("emoticon", "image")
    list_display = ("emoticon", "image")


class UserEmoticonListAdmin(CommonModelAdmin):
    fields = ("buyer", "sold_emoticon")
    list_display = ("buyer", "sold_emoticon")


admin.site.register(Emoticon, EmoticonAdmin)
admin.site.register(EmoticonImage, EmoticonImageAdmin)
admin.site.register(UserEmoticonList, UserEmoticonListAdmin)
