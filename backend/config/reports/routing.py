# reports/routing.py - WebSocket routing for real-time updates
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/reports/(?P<report_id>[^/]+)/$', consumers.ReportProgressConsumer.as_asgi()),
    re_path(r'ws/reports/$', consumers.ReportListConsumer.as_asgi()),
]