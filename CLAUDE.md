# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working with this repository.

## Project identity

**Resonans CMS** — an AI-friendly, reusable Django content management system packaged for
`pip install resonans-cms`. Consumers install it into their own Django project, call
`apply_cms_defaults(globals())` from their settings module, and get the CMS wired:
blog, news, authors, tags, comments, newsletter, internal link building, and optional
Gemini-powered image generation.

This repo is **the package itself**, not an application that uses the package. Treat the
code like a library: stable app labels, predictable URL namespaces, no business logic
from any particular consumer project.

Public marks use brand red `#CC0025`. Logo assets live at
`src/resonans_cms/static/resonans_cms/img/`; the designer source SVGs stay in
`docs/brand-input/` so they travel with the repo.

## Language rule — non-negotiable

All code, templates, comments, UI copy, identifiers, and docs in this repo are in
**English only**. No Persian (or any other language) in source files.

If a consumer project wants to serve non-English audiences, that goes through Django's
i18n layer (`gettext`, `.po` files, `LANGUAGE_CODE`), never by writing translated strings
into the package.

## Repo layout (high level)

```
resonans-cms/
├── pyproject.toml                      hatchling build, pinned deps, extras [ai], [celery], [dev]
├── src/resonans_cms/                   THE pip package (everything under this ships)
│   ├── __init__.py                     __version__
│   ├── conf.py                         apply_cms_defaults(globals()) — the entry point
│   ├── utils/                          html_sanitize, markdown_convert, auto_link
│   ├── templates/resonans_cms/         generic Tailwind templates (base.html, blog/, news/, cms_admin/)
│   ├── static/resonans_cms/            minimal base.css + logos (favicon.svg, logo-icon.svg, logo-wordmark.svg)
│   └── apps/
│       ├── users/                      label: resonans_cms_users   — UUID-pk User, Role, UserRole, allauth adapters
│       ├── core/                       label: resonans_cms_core    — NewsletterSubscriber, AiSetting singleton
│       ├── blog/                       label: resonans_cms_blog    — Post, Author, Category, Tag, Comment + Markdown signal
│       ├── news/                       label: resonans_cms_news    — NewsPost, NewsComment
│       ├── linking/                    label: resonans_cms_linking — UserIntent, Keyword
│       ├── ai_media/                   label: resonans_cms_ai_media — optional Gemini image gen
│       └── cms_admin/                  label: resonans_cms_admin   — dashboard view + seed_demo command
├── demo/                               Django test project (SQLite); has its own manage.py
├── docs/{brand-input,screenshots}/     designer assets + README images
├── tests/                              pytest suite (empty placeholder — add as features land)
└── .github/workflows/                  CI scaffolding (empty — candidate 0.2.0 work)
```

## App label convention (do not break)

Every Django app in this package uses an app label prefixed with `resonans_cms_`. Every
`db_table` on every model is prefixed `resonans_cms_<app>_<model>`. This is how the
package coexists safely with host-project apps and with third-party apps — someone's
own `blog` app never collides with ours.

**Never rename an existing app label or db_table once released.** Host projects rely on
them for FKs and migrations. Additive changes only.

## Commands

### First-time setup (in a fresh clone)

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev,ai,celery]"
```

### Run the demo

```bash
cd demo
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py seed_demo --reset       # populate demo content
../.venv/bin/python manage.py createsuperuser         # (first time)
../.venv/bin/python manage.py runserver 0.0.0.0:8900
```

Public site at `http://localhost:8900/blog/`, Unfold admin at `/admin/`, CMS dashboard
at `/cms/`.

### Applying UI changes

For CSS / template changes in the package, **re-collecting static is not required** in
the demo project — runserver serves `src/resonans_cms/static/` via the
`STATICFILES_DIRS` that `apply_cms_defaults` sets up. Just reload the page.

If you're testing the package in a real (non-demo) host project running under WhiteNoise,
run `python manage.py collectstatic --noinput` there.

### Seeding demo content

```bash
python manage.py seed_demo            # no-op if Posts already exist
python manage.py seed_demo --reset    # wipe all demo content and recreate
```

### Migrations

```bash
python manage.py makemigrations <app_label>      # e.g. resonans_cms_blog
python manage.py migrate
```

**Never create a migration without reading what it's going to do.** Run
`makemigrations --dry-run --verbosity 3` first when the change is non-trivial.

## Architecture notes

### Markdown pipeline

`Post.save()` and `NewsPost.save()` fire a `pre_save` signal
(`resonans_cms.apps.blog.signals`, `.news.signals`) that runs
`content_markdown_source` through `utils.markdown_convert.prepare_content_for_storage`
(Markdown → sanitized HTML via markdown2 + nh3) and stores the result in
`content_raw`. `content_rendered` is populated later by the auto-linker task.

Markdown detection is first-class: if the source contains Markdown syntax (headings,
fenced blocks, list markers, etc.), the pipeline always runs the Markdown path, even
when `<` characters appear inside inline code. Don't regress that check.

### Internal linking

`resonans_cms.apps.linking` exposes `UserIntent` (a URL with a friendly name) and
`Keyword` (phrases that should link to that URL). The auto-linker lives in
`resonans_cms.apps.blog.tasks.run_global_auto_linker` (runs as a Celery task if Celery
is installed, or synchronously otherwise). It reads `content_raw`, injects `<a>` tags
for matching keywords, sanitizes the result, and writes it to `content_rendered`.

### Admin surface

Two admins coexist:
1. **Django admin at `/admin/`**, themed by django-unfold. Every app registers its
   models here with `unfold.admin.ModelAdmin`. This is the primary CRUD surface.
2. **CMS dashboard at `/cms/`**, defined in `resonans_cms.apps.cms_admin`. Thin layer
   with stats + quick-links. Add project-specific custom views here, not in Django admin.

### AI integration

`resonans_cms.apps.ai_media` is the only place that talks to Gemini. The service lazy-
imports `google-generativeai` and returns `None` if the dependency is missing or
`GEMINI_API_KEY` is blank. **Every caller must treat AI as optional**. No code path in
the rest of the CMS should crash when AI is disabled.

## Database conventions

- Models must declare `class Meta: db_table = "resonans_cms_<app>_<model>"` explicitly.
- Use `UUIDField(primary_key=True, default=uuid.uuid4)` for any model exposed on a
  public URL (Post, NewsPost, Author, User, Comment). Exception: `Tag` uses
  `BigAutoField` because its slugs are the canonical identifiers.
- Always use `.select_related()` / `.prefetch_related()` on list and detail views. The
  sample views already do this; don't regress.
- JSONB payloads are fine for admin-configurable content (`AiSetting` prompts,
  `Author.social_links`, etc.) but every public-facing field must still be a typed
  column.

## URL conventions

- Path segments use kebab-case (`/blog/my-post/`, `/cms/linking/run/`).
- URL `name=` identifiers use snake_case.
- Each app owns its own `app_name` namespace in urls.py. Host projects include them
  under whatever prefix they choose; don't hard-code `/blog/` or `/news/` into views —
  use `reverse("blog:post_detail", ...)` etc.

## Environment variables

Full list: see [.env.example](.env.example). Key ones:

- `DJANGO_DEBUG` — `1` during dev, `0` in prod (requires `DJANGO_SECRET_KEY` + `DJANGO_ALLOWED_HOSTS`).
- `GEMINI_API_KEY` / `GEMINI_MODEL` — enables the `ai_media` app.
- `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` — enables the Google social
  login button.
- `CMS_SITE_TITLE` / `CMS_SITE_HEADER` — override the Unfold branding text without
  forking settings.

## Release / publishing (future)

Package is **not yet on PyPI** as of 2026-04-22. First release will need:
1. PyPI account + API token (user-side).
2. `python -m build` to produce sdist + wheel.
3. `twine upload dist/*` (or a GitHub Actions publish job on a `v*` tag).

Version lives in `src/resonans_cms/__init__.py` (`__version__`) and must match
`pyproject.toml` `[project].version`. Tag format: `v0.1.0`, `v0.2.0`, etc.
