from django.urls import re_path

from common.consumer import ChatConsumer

websocket_urlpatterns = [
    re_path('ws/', ChatConsumer.as_asgi()),
]