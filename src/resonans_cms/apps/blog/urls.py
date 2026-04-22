from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("topic/<slug:slug>/", views.TopicPostListView.as_view(), name="topic_list"),
    path("tag/<slug:slug>/", views.TagPostListView.as_view(), name="tag_list"),
    path("author/<slug:slug>/", views.AuthorPostListView.as_view(), name="author_list"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]
