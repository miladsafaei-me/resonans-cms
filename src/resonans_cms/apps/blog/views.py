from django.contrib import messages
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView

from .models import Author, Category, Comment, ContentScope, Post, Tag


def _published_posts_qs():
    return (
        Post.objects.filter(status=Post.Status.PUBLISHED)
        .select_related("author", "category")
        .prefetch_related("tags")
    )


class PostListView(ListView):
    template_name = "resonans_cms/blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        qs = _published_posts_qs().order_by("-published_at", "-created_at")
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(excerpt__icontains=q)
                | Q(content_raw__icontains=q)
            )
        return qs


class PostDetailView(DetailView):
    template_name = "resonans_cms/blog/post_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return _published_posts_qs().prefetch_related(
            Prefetch(
                "comments",
                queryset=Comment.objects.filter(
                    status=Comment.Status.APPROVED, parent__isnull=True
                ).select_related("user").prefetch_related(
                    Prefetch(
                        "replies",
                        queryset=Comment.objects.filter(status=Comment.Status.APPROVED).select_related("user"),
                    )
                ),
                to_attr="approved_root_comments",
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context["post"]
        context["related_posts"] = (
            _published_posts_qs().exclude(pk=post.pk).order_by("-published_at")[:3]
        )
        return context

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
                parent = get_object_or_404(Comment, pk=parent_id, post=self.object)
                depth = parent.depth + 1
            Comment.objects.create(
                post=self.object,
                parent=parent,
                author_name=author_name,
                author_email=author_email,
                body=body,
                status=Comment.Status.PENDING,
                depth=depth,
            )
            messages.success(request, "Your comment has been submitted and is awaiting moderation.")
        url = reverse("blog:post_detail", kwargs={"slug": self.object.slug})
        return HttpResponseRedirect(url + "#comments")


class TopicPostListView(ListView):
    template_name = "resonans_cms/blog/topic_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        self.topic = get_object_or_404(
            Category, slug=self.kwargs["slug"], content_scope=ContentScope.BLOG
        )
        return _published_posts_qs().filter(category=self.topic).order_by("-published_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topic"] = self.topic
        return context


class TagPostListView(ListView):
    template_name = "resonans_cms/blog/tag_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return _published_posts_qs().filter(tags=self.tag).order_by("-published_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context


class AuthorPostListView(ListView):
    template_name = "resonans_cms/blog/author_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        self.author = get_object_or_404(Author, slug=self.kwargs["slug"])
        return _published_posts_qs().filter(author=self.author).order_by("-published_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = self.author
        return context
