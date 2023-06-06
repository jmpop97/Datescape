from django.contrib import admin
from emoticons.models import Emoticon, EmoticonImage, UserEmoticonList

# Register your models here.
admin.site.register(Emoticon)
admin.site.register(EmoticonImage)
admin.site.register(UserEmoticonList)
