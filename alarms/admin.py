from django.contrib import admin
from alarms.models import Alarm
from users.admin import CommonModelAdmin

# Register your models here.


class AlarmAdmin(CommonModelAdmin):
    fields = ("target_user", "type", "type_id")
    list_display = ("target_user", "type", "type_id")


admin.site.register(Alarm, AlarmAdmin)
