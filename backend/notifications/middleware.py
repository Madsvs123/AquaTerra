from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken


@database_sync_to_async
def user_from_token(raw):
    from accounts.models import User

    if not raw:
        return AnonymousUser()
    try:
        token = AccessToken(raw)
    except Exception:
        return AnonymousUser()
    user = User.objects.filter(id=token.get("user_id")).first()
    return user or AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        raw = (query.get("token") or [None])[0]
        org_id = (query.get("organization") or [None])[0]
        scope["user"] = await user_from_token(raw)
        scope["organization_id"] = org_id
        return await super().__call__(scope, receive, send)
