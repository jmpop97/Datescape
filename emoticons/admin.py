from django.contrib import admin
from emoticons.models import Emoticon, EmoticonImage, UserEmoticonList, EmoticonPrice
from users.admin import CommonModelAdmin


class EmoticonAdmin(admin.ModelAdmin):
    fields = ("creator", "title", "created_at", "updated_at", "db_status")
    list_display = ("creator", "title", "created_at", "updated_at", "db_status")
    readonly_fields = ("created_at", "updated_at")
    list_display_links = ["creator", "title"]
    list_filter = [
        "db_status",
        "created_at",
    ]
    list_per_page = 10
    actions = ["make_sale", "make_stop_selling", "make_delete"]

    # admin action 추가
    def make_sale(self, request, queryset):
        updated_count = queryset.update(db_status=1)  # queryset.update
        self.message_user(
            request, "{}건의 항목을 판매중 상태로 변경".format(updated_count)
        )  # django message framework 활용

    make_sale.short_description = "지정 항목을 판매중 상태로 변경"

    def make_stop_selling(self, request, queryset):
        updated_count = queryset.update(db_status=2)  # queryset.update
        self.message_user(
            request, "{}건의 항목을 판매중지 상태로 변경".format(updated_count)
        )  # django message framework 활용

    make_stop_selling.short_description = "지정 항목을 판매중지 상태로 변경"

    def make_delete(self, request, queryset):
        updated_count = queryset.update(db_status=3)  # queryset.update
        self.message_user(
            request, "{}건의 항목을 신청삭제 상태로 변경".format(updated_count)
        )  # django message framework 활용

    make_delete.short_description = "지정 항목을 신청삭제 상태로 변경"


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
