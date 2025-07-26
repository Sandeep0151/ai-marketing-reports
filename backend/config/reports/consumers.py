# reports/consumers.py - WebSocket consumers for real-time updates
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Report


class ReportProgressConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time report progress updates"""

    async def connect(self):
        self.report_id = self.scope['url_route']['kwargs']['report_id']
        self.report_group_name = f'report_{self.report_id}'

        # Join report group
        await self.channel_layer.group_add(
            self.report_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave report group
        await self.channel_layer.group_discard(
            self.report_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            if message_type == 'get_status':
                # Send current report status
                report = await self.get_report(self.report_id)
                if report:
                    await self.send(text_data=json.dumps({
                        'type': 'status_update',
                        'report_id': str(report.id),
                        'status': report.status,
                        'progress_percentage': report.progress_percentage,
                        'processing_steps': report.processing_steps,
                        'error_messages': report.error_messages,
                    }))
        except json.JSONDecodeError:
            pass

    async def report_progress_update(self, event):
        """Handle progress update from group"""
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'step': event['step'],
            'status': event['status'],
            'progress': event['progress'],
            'message': event['message'],
            'timestamp': event.get('timestamp'),
        }))

    async def report_status_update(self, event):
        """Handle status update from group"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'report_id': event['report_id'],
            'status': event['status'],
            'progress_percentage': event.get('progress_percentage', 0),
            'message': event.get('message', ''),
            'timestamp': event.get('timestamp'),
        }))

    async def report_completed(self, event):
        """Handle report completion"""
        await self.send(text_data=json.dumps({
            'type': 'report_completed',
            'report_id': event['report_id'],
            'message': 'Report generation completed successfully!',
            'timestamp': event.get('timestamp'),
        }))

    async def report_failed(self, event):
        """Handle report failure"""
        await self.send(text_data=json.dumps({
            'type': 'report_failed',
            'report_id': event['report_id'],
            'error': event.get('error', 'Unknown error'),
            'timestamp': event.get('timestamp'),
        }))

    @database_sync_to_async
    def get_report(self, report_id):
        """Get report from database"""
        try:
            return Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return None


class ReportListConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time report list updates"""

    async def connect(self):
        self.group_name = 'report_list'

        # Join report list group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave report list group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def report_created(self, event):
        """Handle new report creation"""
        await self.send(text_data=json.dumps({
            'type': 'report_created',
            'report_id': event['report_id'],
            'website_domain': event.get('website_domain'),
            'timestamp': event.get('timestamp'),
        }))

    async def report_status_changed(self, event):
        """Handle report status changes"""
        await self.send(text_data=json.dumps({
            'type': 'report_status_changed',
            'report_id': event['report_id'],
            'old_status': event.get('old_status'),
            'new_status': event['new_status'],
            'timestamp': event.get('timestamp'),
        }))