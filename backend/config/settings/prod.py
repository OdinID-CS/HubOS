"""Production settings. Requires DJANGO_DEBUG=false and a real secret key."""
from .base import *  # noqa: F401,F403
from .base import env_bool, env_list

DEBUG = False

# Fail fast if deployed with an obviously placeholder secret.
if SECRET_KEY.startswith("change-me"):  # noqa: F405
    raise RuntimeError("DJANGO_SECRET_KEY must be set to a real value in production")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "31536000"))  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
