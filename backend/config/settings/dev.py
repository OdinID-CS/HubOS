"""Local development settings. Insecure by design — never use in production."""
from .base import *  # noqa: F401,F403
from .base import env_list

DEBUG = True

# Dev server plus the Vite dev servers the frontend actually uses.
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://(127\.0\.0\.1|localhost)(:\d+)?$",
]

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
)

# Allow the cookie to be sent/read from http origins during local development.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
