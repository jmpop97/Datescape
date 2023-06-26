from rest_framework import serializers
from alarms.models import Alarm
from articles.models import Comment, Reply
from emoticons.models import Emoticon


class AlarmSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()
    emoticon = serializers.SerializerMethodField()

    def get_article(self, alarm):
        if alarm.type == "comment":
            comment = Comment.objects.get(id=alarm.type_id)
            return {"id": comment.article.id, "title": comment.article.title}
        if alarm.type == "reply":
            reply = Reply.objects.get(id=alarm.type_id)
            return {
                "id": reply.comment.article.id,
                "title": reply.comment.article.title,
            }
        else:
            return None

    def get_emoticon(self, alarm):
        if alarm.type == "emoticon":
            emoticon = Emoticon.objects.get(id=alarm.type_id)
            return {"id": emoticon.id, "title": emoticon.title}
        else:
            return None

    class Meta:
        model = Alarm
        fields = "__all__"
