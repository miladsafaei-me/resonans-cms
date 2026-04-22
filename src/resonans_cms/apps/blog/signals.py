"""Post-save signal: convert Markdown → sanitized HTML and cache on the model."""

from django.db.models.signals import pre_save
from django.dispatch import receiver

from resonans_cms.utils.markdown_convert import markdown_to_html, prepare_content_for_storage

from .models import Post


@receiver(pre_save, sender=Post)
def render_post_markdown(sender, instance: Post, **kwargs):
    """Render Markdown sources to HTML whenever a Post is saved."""
    if instance.content_markdown_source:
        instance.content_raw = prepare_content_for_storage(instance.content_markdown_source)
    if instance.key_takeaways_markdown_source:
        instance.key_takeaways = markdown_to_html(instance.key_takeaways_markdown_source)
