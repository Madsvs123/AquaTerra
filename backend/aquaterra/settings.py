import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("AQUATERRA_SECRET_KEY", "dev-only-change-me-aquaterra")
DEBUG = os.environ.get("AQUATERRA_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("AQUATERRA_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "channels",
    "common",
    "accounts",
    "organizations",
    "farms",
    "devices",
    "irrigation",
    "recommendations",
    "alerts",
    "analytics",
    "maintenance",
    "work",
    "reports",
    "notifications",
    "weather",
    "audit",
    "search",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "accounts.middleware.RequestContextMiddleware",
    "audit.middleware.AuditMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "aquaterra.urls"
ASGI_APPLICATION = "aquaterra.asgi.application"
WSGI_APPLICATION = "aquaterra.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("AQUATERRA_DB_NAME", "aquaterra"),
        "USER": os.environ.get("AQUATERRA_DB_USER", "aquaterra"),
        "PASSWORD": os.environ.get("AQUATERRA_DB_PASSWORD", "aquaterra"),
        "HOST": os.environ.get("AQUATERRA_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("AQUATERRA_DB_PORT", "5432"),
    }
}

AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "AQUATERRA_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "x-csrftoken",
    "x-organization-id",
    "x-farm-id",
    "x-api-key",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "accounts.authentication.ApiKeyAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "common.permissions.IsAuthenticatedTenant",
        "common.permissions.HasOrgPermission",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "user": "4000/hour",
        "anon": "120/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=45),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

REDIS_URL = os.environ.get("AQUATERRA_REDIS_URL", "redis://127.0.0.1:6379/8")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

CELERY_BROKER_URL = os.environ.get("AQUATERRA_CELERY_BROKER", REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get("AQUATERRA_CELERY_RESULT", REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULE = {
    "evaluate-alerts": {
        "task": "alerts.tasks.evaluate_all_organizations",
        "schedule": 120.0,
    },
    "generate-recommendations": {
        "task": "recommendations.tasks.generate_all_recommendations",
        "schedule": 300.0,
    },
    "refresh-weather": {
        "task": "weather.tasks.refresh_all_weather",
        "schedule": 900.0,
    },
    "check-device-health": {
        "task": "devices.tasks.check_device_health",
        "schedule": 180.0,
    },
    "run-due-schedules": {
        "task": "irrigation.tasks.run_due_schedules",
        "schedule": 60.0,
    },
    "capture-usage-snapshots": {
        "task": "analytics.tasks.capture_usage_snapshots",
        "schedule": 3600.0,
    },
    "due-maintenance": {
        "task": "maintenance.tasks.flag_due_maintenance",
        "schedule": 3600.0,
    },
    "expire-invitations": {
        "task": "accounts.tasks.expire_invitations",
        "schedule": 3600.0,
    },
}

EMAIL_BACKEND = os.environ.get(
    "AQUATERRA_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.environ.get("AQUATERRA_FROM_EMAIL", "ops@aquaterra.local")
FRONTEND_URL = os.environ.get("AQUATERRA_FRONTEND_URL", "http://localhost:5173")
WEATHER_API_URL = os.environ.get("AQUATERRA_WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")
DEVICE_OFFLINE_SECONDS = int(os.environ.get("AQUATERRA_DEVICE_OFFLINE_SECONDS", "300"))
