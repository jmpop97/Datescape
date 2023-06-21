from rest_framework import serializers
from reports.models import ReportUser, ReportArticle, ReportComment, ChildCategory
from users.models import User
from articles.models import Article, Comment


class ReportUserSerializer(serializers.ModelSerializer):
    """report_id값을 report_user로 변환,
    신고자id값과 함께 저장"""

    report_id = serializers.IntegerField(source="report_user")
    report_type = serializers.IntegerField(write_only=True)

    class Meta:
        model = ReportUser
        fields = (
            "report_id",
            "comment",
            "report_type",
        )

    def create(self, validated_data):
        validated_data["report_user"] = User.objects.get(
            id=validated_data["report_user"]
        )
        validated_data["reporter"] = User.objects.get(id=validated_data["reporter"])
        validated_data["report_type"] = ChildCategory.objects.get(
            id=validated_data["report_type"]
        ).category
        return super().create(validated_data)


class ReportArticleSerializer(serializers.ModelSerializer):
    """report_id값을 report_article로 변환,
    신고자id값과 함께 저장"""

    report_id = serializers.IntegerField(source="report_article")
    report_type = serializers.IntegerField(write_only=True)

    class Meta:
        model = ReportArticle
        fields = (
            "report_id",
            "comment",
            "report_type",
        )

    def create(self, validated_data):
        validated_data["report_article"] = Article.objects.get(
            id=validated_data["report_article"]
        )
        validated_data["reporter"] = User.objects.get(id=validated_data["reporter"])
        validated_data["report_type"] = ChildCategory.objects.get(
            id=validated_data["report_type"]
        ).category

        return super().create(validated_data)


class ReportCommentSerializer(serializers.ModelSerializer):
    """report_id값을 report_comment로 변환,
    신고자id값과 함께 저장"""

    report_id = serializers.IntegerField(source="report_comment")
    report_type = serializers.IntegerField(write_only=True)

    class Meta:
        model = ReportComment
        fields = (
            "report_id",
            "comment",
            "report_type",
        )

    def create(self, validated_data):
        validated_data["report_comment"] = Comment.objects.get(
            id=validated_data["report_comment"]
        )
        validated_data["reporter"] = User.objects.get(id=validated_data["reporter"])
        validated_data["report_type"] = ChildCategory.objects.get(
            id=validated_data["report_type"]
        ).category
        return super().create(validated_data)


class ChildCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildCategory
        fields = (
            "parent_category",
            "riority",
            "id",
        )
