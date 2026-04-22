from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from resonans_cms.apps.blog.models import Post
from resonans_cms.apps.core.models import NewsletterSubscriber
from resonans_cms.apps.linking.models import Keyword, UserIntent
from resonans_cms.apps.news.models import NewsPost


@method_decorator([login_required, staff_member_required], name="dispatch")
class DashboardView(View):
    template_name = "resonans_cms/cms_admin/dashboard.html"

    def get(self, request):
        stats = {
            "blog_posts": Post.objects.count(),
            "blog_published": Post.objects.filter(status=Post.Status.PUBLISHED).count(),
            "news_posts": NewsPost.objects.count(),
            "newsletter_subscribers": NewsletterSubscriber.objects.filter(
                unsubscribed_at__isnull=True
            ).count(),
            "user_intents": UserIntent.objects.count(),
            "keywords": Keyword.objects.count(),
        }
        quick_links = [
            ("Blog posts", reverse("admin:resonans_cms_blog_post_changelist")),
            ("News posts", reverse("admin:resonans_cms_news_newspost_changelist")),
            ("Authors", reverse("admin:resonans_cms_blog_author_changelist")),
            ("Topics", reverse("admin:resonans_cms_blog_category_changelist")),
            ("Tags", reverse("admin:resonans_cms_blog_tag_changelist")),
            ("Comments", reverse("admin:resonans_cms_blog_comment_changelist")),
            ("Newsletter subscribers", reverse("admin:resonans_cms_core_newslettersubscriber_changelist")),
            ("Keyword mapping", reverse("admin:resonans_cms_linking_userintent_changelist")),
            ("AI settings", reverse("admin:resonans_cms_core_aisetting_changelist")),
        ]
        return render(request, self.template_name, {"stats": stats, "quick_links": quick_links})


@login_required
@staff_member_required
def run_auto_linker(request):
    """Trigger the auto-linker. Runs synchronously if Celery is not configured."""
    from resonans_cms.apps.blog.tasks import run_global_auto_linker

    result = run_global_auto_linker()
    if hasattr(result, "id"):
        return JsonResponse({"queued": True, "task_id": str(result.id)})
    return JsonResponse({"queued": False, "result": result})
