from .models import SiteSettings


def site_settings(request):
    """Makes `site_settings` available in every template without passing it
    from each view. Cached per-request via request attribute to avoid
    repeated queries if accessed multiple times."""
    if not hasattr(request, "_site_settings_cache"):
        request._site_settings_cache = SiteSettings.get_solo()
    return {"site_settings": request._site_settings_cache}
