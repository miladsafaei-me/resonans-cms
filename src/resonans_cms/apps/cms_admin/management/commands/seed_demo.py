"""
Seed the database with a small, realistic set of demo content so someone
who just cloned the repo can see the CMS come alive with one command.

    python manage.py seed_demo           # idempotent: does nothing if content exists
    python manage.py seed_demo --reset   # wipe and recreate the demo content
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from resonans_cms.apps.blog.models import (
    Author,
    Category,
    ContentScope,
    Post,
    Tag,
)
from resonans_cms.apps.core.models import NewsletterSubscriber
from resonans_cms.apps.linking.models import Keyword, UserIntent
from resonans_cms.apps.news.models import NewsPost


AUTHORS = [
    {
        "name": "Jane Mercer",
        "slug": "jane-mercer",
        "role": "Editor-in-Chief",
        "bio": "Covers product strategy, content ops, and the intersection of AI with publishing workflows.",
        "avatar_url": "https://i.pravatar.cc/200?img=47",
    },
    {
        "name": "Sam Ortega",
        "slug": "sam-ortega",
        "role": "Senior Writer",
        "bio": "Writes about design systems, typography, and building calm user interfaces.",
        "avatar_url": "https://i.pravatar.cc/200?img=11",
    },
]

CATEGORIES = [
    {"name": "Technology", "slug": "technology", "scope": ContentScope.BLOG, "description": "Deep dives on software, AI, and infrastructure."},
    {"name": "Design", "slug": "design", "scope": ContentScope.BLOG, "description": "Product design and visual language."},
    {"name": "Markets", "slug": "markets", "scope": ContentScope.NEWS, "description": "Industry news and market moves."},
]

TAGS = [
    ("AI", "ai"),
    ("Django", "django"),
    ("CMS", "cms"),
    ("Design Systems", "design-systems"),
]

POST_P1_MD = """## Why this matters

Teams that publish AI-generated content hit the same wall: the model emits Markdown, the CMS expects HTML, and the gap between them is full of broken escapes, orphan heading IDs, and `<script>` tags you never asked for.

Resonans CMS closes the gap with a **pre-save signal** that:

1. Accepts Markdown in a dedicated source field
2. Runs it through markdown2 with fenced code, tables, and strike-through extras
3. Sanitizes the output with nh3 using an allowlist of tags and attributes
4. Stores the sanitized HTML in `content_raw` and keeps the Markdown source around for round-trip editing

### What you avoid

- `<style>` injection from prompt leakage
- Heading IDs longer than 120 characters
- `<iframe>` and `<object>` tags you didn't allowlist
- `data:` URIs pointing at SVG

All of this happens transparently at save time.

> "The best sanitizer is the one you never think about."

### Next steps

Next release will add an opt-in prompt-injection filter for the sanitizer.
"""

POST_P2_MD = """## The invisible CMS

Every CMS wants to be noticed. Tabs everywhere, nested menus, dashboards with twelve widgets you never read. Resonans goes the other way.

### Three rules we follow

1. **Public templates ship with zero brand assumptions.** System fonts, Tailwind utility classes, no "Powered by" headers.
2. **Admin uses Unfold, not custom chrome.** Every hour building a custom admin is an hour you aren't writing.
3. **The author never sees HTML.** Markdown goes in, HTML comes out.

### What this looks like in practice

A fresh install gives you a `/blog/` route, an admin under `/admin/`, and a `/cms/` dashboard with six tiles.

No megamenu. No sidebar. Just content and the controls to ship it.
"""

POST_P3_MD = """Images used to be the slowest part of publishing. Sourcing, licensing, cropping, alt text — every post needed a separate pass. With a single **Gemini API key** in your settings, Resonans generates both hero and inline images from the post's own context.

### The contract

- Set `GEMINI_API_KEY` in your environment, or store it on the singleton `AiSetting`
- Post save triggers optional image generation (controlled by `auto_generate_on_save`)
- Missing key? The feature silently disables.

### Why optional

Not every project wants AI images in production. The `ai_media` app is a separate `INSTALLED_APPS` entry:

```bash
pip install resonans-cms[ai]
```

Drop the extra and the import lazy-fails to `None`. The core CMS keeps working.
"""

POSTS = [
    {
        "author": "jane-mercer",
        "category": "technology",
        "tags": ["ai", "cms", "django"],
        "title": "Turning AI-Authored Markdown Into Publish-Ready HTML",
        "slug": "ai-markdown-to-html",
        "excerpt": "How we built a single-signal pipeline that takes raw Markdown from any LLM and produces sanitized, SEO-ready HTML without a round-trip to staging.",
        "markdown": POST_P1_MD,
        "takeaways": "- One signal converts Markdown to sanitized HTML on every save\n- nh3 + markdown2 pipeline: safe by default\n- Round-trip editing preserved via `content_markdown_source`",
        "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&q=80",
        "days_ago": 2,
    },
    {
        "author": "sam-ortega",
        "category": "design",
        "tags": ["cms", "design-systems"],
        "title": "Designing a CMS That Stays Out of the Way",
        "slug": "cms-stays-out-of-the-way",
        "excerpt": "A good CMS lets you forget it exists. Here's the design philosophy behind Resonans' minimal chrome and Tailwind-first public templates.",
        "markdown": POST_P2_MD,
        "takeaways": "- Ship with minimal public chrome so projects add their own brand\n- Use Unfold for admin instead of inventing another dashboard\n- Authors work in Markdown, never raw HTML",
        "image": "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=1200&q=80",
        "days_ago": 5,
    },
    {
        "author": "jane-mercer",
        "category": "technology",
        "tags": ["ai", "cms"],
        "title": "One API Key, Every Image: The AI Media Pipeline",
        "slug": "ai-media-one-api-key",
        "excerpt": "Featured images and inline illustrations generated from a single Gemini key. Here's how the ai_media app stays optional and opt-in.",
        "markdown": POST_P3_MD,
        "takeaways": "- One `GEMINI_API_KEY` powers hero and inline generation\n- The AI app is an optional extras install\n- Singleton `AiSetting` lets non-developers swap models from the admin",
        "image": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&q=80",
        "days_ago": 9,
    },
]

NEWS = [
    {
        "author": "jane-mercer",
        "category": "markets",
        "title": "Resonans CMS 0.1.0 Released",
        "slug": "resonans-cms-0-1-0-released",
        "excerpt": "The first public release of an AI-friendly Django CMS lands on GitHub today.",
        "markdown": "The first version of **Resonans CMS** is now available as a public GitHub repo.",
        "image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1200&q=80",
        "days_ago": 1,
    },
    {
        "author": "sam-ortega",
        "category": "markets",
        "title": "Unfold 0.90 Lands With Refreshed Dashboard Widgets",
        "slug": "unfold-0-90-dashboard",
        "excerpt": "The Django admin theme we ship picks up a new widget library and import/export polish.",
        "markdown": "Unfold's latest release ships with better dashboard widgets and tighter accessibility defaults.",
        "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80",
        "days_ago": 3,
    },
]

INTENTS = [
    {
        "name": "Get started with Resonans",
        "url": "https://github.com/miladsafaei-me/resonans-cms#quick-start",
        "keywords": ["resonans cms", "AI-friendly django"],
    },
]

SUBSCRIBERS = [
    ("alex@example.com", "US"),
    ("priya@example.com", "IN"),
    ("hiro@example.com", "JP"),
]


class Command(BaseCommand):
    help = "Populate the database with demo blog posts, news, authors, tags, and subscribers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo content before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("Clearing existing CMS content...")
            Post.objects.all().delete()
            NewsPost.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            Author.objects.all().delete()
            UserIntent.objects.all().delete()
            NewsletterSubscriber.objects.all().delete()

        if Post.objects.exists() and not options["reset"]:
            self.stdout.write(self.style.WARNING(
                "Database already has posts. Run with --reset to wipe and reseed."
            ))
            return

        self.stdout.write("Creating authors...")
        authors = {
            data["slug"]: Author.objects.create(
                name=data["name"],
                slug=data["slug"],
                role=data["role"],
                bio=data["bio"],
                avatar_url=data["avatar_url"],
            )
            for data in AUTHORS
        }

        self.stdout.write("Creating categories...")
        categories = {
            data["slug"]: Category.objects.create(
                name=data["name"],
                slug=data["slug"],
                content_scope=data["scope"],
                description=data["description"],
            )
            for data in CATEGORIES
        }

        self.stdout.write("Creating tags...")
        tags = {slug: Tag.objects.create(name=name, slug=slug) for name, slug in TAGS}

        self.stdout.write("Creating blog posts...")
        now = timezone.now()
        for data in POSTS:
            post = Post.objects.create(
                title=data["title"],
                slug=data["slug"],
                excerpt=data["excerpt"],
                content_markdown_source=data["markdown"],
                key_takeaways_markdown_source=data["takeaways"],
                status=Post.Status.PUBLISHED,
                author=authors[data["author"]],
                category=categories[data["category"]],
                featured_image_url=data["image"],
                published_at=now - timedelta(days=data["days_ago"]),
            )
            post.tags.add(*(tags[t] for t in data["tags"]))

        self.stdout.write("Creating news articles...")
        for data in NEWS:
            NewsPost.objects.create(
                title=data["title"],
                slug=data["slug"],
                excerpt=data["excerpt"],
                content_markdown_source=data["markdown"],
                status=NewsPost.Status.PUBLISHED,
                author=authors[data["author"]],
                category=categories[data["category"]],
                featured_image_url=data["image"],
                published_at=now - timedelta(days=data["days_ago"]),
            )

        self.stdout.write("Creating internal-link intents...")
        for data in INTENTS:
            intent = UserIntent.objects.create(name=data["name"], target_url=data["url"])
            for phrase in data["keywords"]:
                Keyword.objects.create(intent=intent, phrase=phrase)

        self.stdout.write("Creating newsletter subscribers...")
        for email, country in SUBSCRIBERS:
            NewsletterSubscriber.objects.create(email=email, country_code=country)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Post.objects.count()} posts, {NewsPost.objects.count()} news, "
            f"{Author.objects.count()} authors, {Tag.objects.count()} tags, "
            f"{NewsletterSubscriber.objects.count()} subscribers."
        ))
