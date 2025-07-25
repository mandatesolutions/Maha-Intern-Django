from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import decode as jwt_decode
from django.conf import settings
from .models import UserModel 

@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token["user_id"]
        return UserModel.objects.get(id=user_id)
    except UserModel.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")

        if token:
            try:
                validated_token = UntypedToken(token[0])
                scope["user"] = await get_user(validated_token)
            except Exception as e:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
