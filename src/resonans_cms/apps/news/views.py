from django.contrib import messages
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView

from resonans_cms.apps.blog.models import Category, ContentScope, Tag

from .models import NewsComment, NewsPost


def _published_qs():
    return (
        NewsPost.objects.filter(status=NewsPost.Status.PUBLISHED)
        .select_related("author", "category")
        .prefetch_related("tags")
    )


class NewsPostListView(ListView):
    template_name = "resonans_cms/news/post_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        qs = _published_qs().order_by("-published_at", "-created_at")
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(excerpt__icontains=q)
                | Q(content_raw__icontains=q)
            )
        return qs


class NewsPostDetailView(DetailView):
    template_name = "resonans_cms/news/post_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return _published_qs().prefetch_related(
            Prefetch(
                "comments",
                queryset=NewsComment.objects.filter(
                    status=NewsComment.Status.APPROVED, parent__isnull=True
                ).select_related("user").prefetch_related(
                    Prefetch(
                        "replies",
                        queryset=NewsComment.objects.filter(
                            status=NewsComment.Status.APPROVED
                        ).select_related("user"),
                    )
                ),
                to_attr="approved_root_comments",
            ),
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        author_name = (request.POST.get("author_name") or "").strip()
        author_email = (request.POST.get("author_email") or "").strip()
        body = (request.POST.get("body") or "").strip()
        parent_id = (request.POST.get("parent_id") or "").strip()
        if not (author_name and author_email and body):
            messages.error(request, "Please fill in all required fields.")
        else:
            parent = None
            depth = 0
            if parent_id:
                parent = get_object_or_404(NewsComment, pk=parent_id, news_post=self.object)
                depth = parent.depth + 1
            NewsComment.objects.create(
                news_post=self.object,
                parent=parent,
                author_name=author_name,
                author_email=author_email,
                body=body,
                status=NewsComment.Status.PENDING,
                depth=depth,
            )
            messages.success(request, "Your comment has been submitted and is awaiting moderation.")
        url = reverse("news:post_detail", kwargs={"slug": self.object.slug})
        return HttpResponseRedirect(url + "#comments")


class NewsTopicListView(ListView):
    template_name = "resonans_cms/news/topic_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        self.topic = get_object_or_404(
            Category, slug=self.kwargs["slug"], content_scope=ContentScope.NEWS
        )
        return _published_qs().filter(category=self.topic).order_by("-published_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topic"] = self.topic
        return context


class NewsTagListView(ListView):
    template_name = "resonans_cms/news/tag_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return _published_qs().filter(tags=self.tag).order_by("-published_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context
