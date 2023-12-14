from django.urls import re_path,path

from . import consumers

websocket_urlpatterns = [
    path(r"scheduler/", consumers.ProcessConsumer.as_asgi()),
]