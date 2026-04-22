from django.db.models.signals import pre_save
from django.dispatch import receiver

from resonans_cms.utils.markdown_convert import markdown_to_html, prepare_content_for_storage

from .models import NewsPost


@receiver(pre_save, sender=NewsPost)
def render_news_markdown(sender, instance: NewsPost, **kwargs):
    if instance.content_markdown_source:
        instance.content_raw = prepare_content_for_storage(instance.content_markdown_source)
    if instance.key_takeaways_markdown_source:
        instance.key_takeaways = markdown_to_html(instance.key_takeaways_markdown_source)
