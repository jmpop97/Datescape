from rest_framework import serializers
from alarms.models import Alarm
from articles.models import Comment, Reply
from emoticons.models import Emoticon


class AlarmSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()
    emoticon = serializers.SerializerMethodField()

    def get_article(self, alarm):
        try:
            if alarm.type == "comment":
                comment = Comment.objects.get(id=alarm.type_id)
                return {"id": comment.article.id, "title": comment.article.title}
            if alarm.type == "reply":
                reply = Reply.objects.get(id=alarm.type_id)
                return {
                    "id": reply.comment.article.id,
                    "title": reply.comment.article.title,
                }
        except:
            alarm.delete()
            return None

    def get_emoticon(self, alarm):
        try:
            if alarm.type == "emoticon":
                print("--------------------: ", alarm.type_id)
                emoticon = Emoticon.objects.get(id=alarm.type_id)
                return {"id": emoticon.id, "title": emoticon.title}
        except:
            alarm.delete()
            return None

    class Meta:
        model = Alarm
        fields = "__all__"
