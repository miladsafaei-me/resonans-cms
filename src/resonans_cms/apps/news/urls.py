from django.urls import path

from . import views

app_name = "news"

urlpatterns = [
    path("", views.NewsPostListView.as_view(), name="post_list"),
    path("topic/<slug:slug>/", views.NewsTopicListView.as_view(), name="topic_list"),
    path("tag/<slug:slug>/", views.NewsTagListView.as_view(), name="tag_list"),
    path("<slug:slug>/", views.NewsPostDetailView.as_view(), name="post_detail"),
]
