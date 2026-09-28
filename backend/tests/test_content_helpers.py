from app.services.content import slugify


def test_slugify_is_stable_and_safe():
    assert slugify("  Product & AI Notes! ") == "product-ai-notes"


def test_slugify_has_a_nonempty_fallback():
    assert slugify("🔥") == "untitled"
