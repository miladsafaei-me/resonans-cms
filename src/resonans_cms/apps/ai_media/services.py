"""
Gemini-powered image generation service.

Requires the optional `google-generativeai` dependency:
    pip install resonans-cms[ai]

Returns `None` and logs a warning if the dependency is missing or the
API key is not configured — callers should treat the feature as optional.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from resonans_cms.apps.core.models import AiSetting

logger = logging.getLogger(__name__)


@dataclass
class GeneratedImageResult:
    image_bytes: bytes
    mime_type: str
    model_name: str


def _import_genai():
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        logger.warning(
            "google-generativeai is not installed; image generation is disabled. "
            "Install resonans-cms[ai] to enable it."
        )
        return None


def generate_image(
    prompt: str,
    kind: str = "hero",
    aspect_ratio: Optional[str] = None,
) -> Optional[GeneratedImageResult]:
    """Generate an image from a text prompt using Gemini / Imagen."""
    genai = _import_genai()
    if genai is None:
        return None

    settings = AiSetting.load()
    api_key = settings.resolved_image_ai_api_key()
    if not api_key:
        logger.warning("No image AI API key configured in AiSetting.")
        return None

    model_name = (
        settings.hero_image_model if kind == "hero" else settings.inline_image_model
    )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        for part in response.parts:
            inline_data = getattr(part, "inline_data", None)
            if inline_data and inline_data.data:
                return GeneratedImageResult(
                    image_bytes=inline_data.data,
                    mime_type=inline_data.mime_type or "image/png",
                    model_name=model_name,
                )
    except Exception as exc:
        logger.exception("Gemini image generation failed: %s", exc)
        return None

    logger.warning("Gemini response contained no inline image data.")
    return None
