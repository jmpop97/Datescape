from django.urls import path

from . import views


urlpatterns = [
    path("unread/", views.AlarmView.as_view(), name="unread"),
    path("detail/", views.AlarmDetailView.as_view(), name="detail"),
]
