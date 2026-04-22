from django.views.generic import TemplateView

from resonans_cms.apps.blog.models import Post
from resonans_cms.apps.news.models import NewsPost


class HomeView(TemplateView):
    template_name = "resonans_cms/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_posts"] = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .select_related("author", "category")
            .order_by("-published_at", "-created_at")[:3]
        )
        context["latest_news"] = (
            NewsPost.objects.filter(status=NewsPost.Status.PUBLISHED)
            .select_related("author", "category")
            .order_by("-published_at", "-created_at")[:3]
        )
        return context
