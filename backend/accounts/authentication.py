import hashlib
import secrets

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import ApiKey


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def generate_api_key():
    raw = f"at_{secrets.token_urlsafe(32)}"
    prefix = raw[:10]
    return raw, prefix, hash_api_key(raw)


class ApiKeyAuthentication(BaseAuthentication):
    www_authenticate_realm = "api"

    def authenticate(self, request):
        raw = request.headers.get("X-API-Key")
        auth = request.headers.get("Authorization", "")
        if not raw and auth.lower().startswith("apikey "):
            raw = auth.split(" ", 1)[1].strip()
        if not raw:
            return None
        key = ApiKey.objects.select_related("created_by", "organization").filter(key_hash=hash_api_key(raw)).first()
        if not key or not key.is_active:
            raise AuthenticationFailed("Invalid API key.")
        if not key.created_by or not key.created_by.is_active:
            raise AuthenticationFailed("API key owner is inactive.")
        ApiKey.objects.filter(pk=key.pk).update(last_used_at=timezone.now())
        request.api_key = key
        request.organization = key.organization
        return (key.created_by, key)
