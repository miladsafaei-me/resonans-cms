# Changelog

All notable changes to Resonans CMS are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-04-22

### Added
- Initial release.
- `resonans_cms.apps.users` — custom `User` model (UUID pk), allauth integration for email and Google OAuth, role/permission management.
- `resonans_cms.apps.core` — `NewsletterSubscriber` and singleton `AiSetting` models; shared utilities (markdown, HTML sanitize, media URL helpers).
- `resonans_cms.apps.blog` — `Post`, `Author`, `Category`, `Tag`, `Comment` with Markdown authoring, threaded comments, and simple list/detail views.
- `resonans_cms.apps.news` — `NewsPost` and news-scoped comments; mirrors blog structure.
- `resonans_cms.apps.linking` — `UserIntent` and `Keyword` for keyword-based internal link building.
- `resonans_cms.apps.ai_media` — optional Gemini-powered featured and inline image generation.
- `resonans_cms.apps.cms_admin` — Unfold-based admin dashboard with CRUD for all CMS models.
- Minimal Tailwind-styled base template and public-facing blog/news templates.
- Demo Django project (`demo/`) for local development and testing.
