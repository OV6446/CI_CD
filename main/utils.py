"""Безопасные редиректы (защита от open redirect)."""
from django.utils.http import url_has_allowed_host_and_scheme


def is_safe_redirect_url(url, request):
    if not url:
        return False
    return url_has_allowed_host_and_scheme(
        url=url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )


def append_scroll_fragment(url, scroll_position):
    if not scroll_position or not str(scroll_position).isdigit():
        return url
    return f'{url}#scroll={scroll_position}'
