"""Celery task: refresh `content_rendered` with injected internal links."""

try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(fn):
            return fn
        if args and callable(args[0]):
            return args[0]
        return decorator

from resonans_cms.utils.auto_link import apply_auto_links
from resonans_cms.utils.html_sanitize import sanitize_html


def _build_intents_data():
    from resonans_cms.apps.linking.models import UserIntent

    intents_data = []
    for intent in UserIntent.objects.prefetch_related("keywords").all():
        keywords = [kw.phrase for kw in intent.keywords.all() if kw.phrase]
        if keywords:
            intents_data.append({"url": intent.target_url, "keywords": keywords})
    return intents_data


def refresh_article_rendered(instance) -> None:
    """Recompute `content_rendered` from `content_raw` on a Post or NewsPost."""
    intents_data = _build_intents_data()
    html_input = instance.content_raw or ""
    html_output = apply_auto_links(html_input, intents_data)
    instance.content_rendered = sanitize_html(html_output or "")
    instance.save(update_fields=["content_rendered"])


@shared_task(name="resonans_cms.blog.run_global_auto_linker")
def run_global_auto_linker():
    """Batch process: inject internal links into all blog posts and news articles."""
    from resonans_cms.apps.blog.models import Post

    intents_data = _build_intents_data()
    if not intents_data:
        return {"processed": 0, "message": "No keyword mappings found."}

    processed = 0
    for post in Post.objects.iterator(chunk_size=100):
        refresh_article_rendered(post)
        processed += 1

    try:
        from resonans_cms.apps.news.models import NewsPost
    except ImportError:
        pass
    else:
        for article in NewsPost.objects.iterator(chunk_size=100):
            refresh_article_rendered(article)
            processed += 1

    return {
        "processed": processed,
        "intents": len(intents_data),
        "keywords": sum(len(i["keywords"]) for i in intents_data),
    }
