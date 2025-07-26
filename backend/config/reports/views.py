# reports/views.py
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
import logging

from .models import Website, Report, ReportTemplate, ReportShare
from .serializers import (
    WebsiteSerializer, ReportCreateSerializer, ReportDetailSerializer,
    ReportListSerializer, ReportProgressSerializer, ReportTemplateSerializer,
    ReportShareSerializer, ReportShareCreateSerializer
)
from .tasks import generate_marketing_report

logger = logging.getLogger(__name__)


class ReportCreateView(generics.CreateAPIView):
    """Create a new marketing report"""
    serializer_class = ReportCreateSerializer
    permission_classes = [permissions.AllowAny]  # For development

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the report
        report = serializer.save()

        # Start background task for report generation
        try:
            generate_marketing_report.delay(str(report.id))
            logger.info(f"Started report generation task for report {report.id}")
        except Exception as e:
            logger.error(f"Failed to start report generation task: {e}")
            report.status = 'failed'
            report.error_messages = [f"Failed to start processing: {str(e)}"]
            report.save()

        # Return report details
        response_serializer = ReportDetailSerializer(report)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReportListView(generics.ListAPIView):
    """List all reports with filtering and pagination"""
    serializer_class = ReportListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Report.objects.select_related('website').all()

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by domain
        domain = self.request.query_params.get('domain')
        if domain:
            queryset = queryset.filter(website__domain__icontains=domain)

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset.order_by('-created_at')


class ReportDetailView(generics.RetrieveAPIView):
    """Get detailed report information"""
    serializer_class = ReportDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        return Report.objects.select_related('website').all()


class ReportProgressView(APIView):
    """Get report progress and status"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
            serializer = ReportProgressSerializer(report)
            return Response(serializer.data)
        except Report.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ReportDeleteView(generics.DestroyAPIView):
    """Delete a report"""
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        return Report.objects.all()

    def destroy(self, request, *args, **kwargs):
        report = self.get_object()

        # Cancel if still processing
        if report.status in ['pending', 'processing']:
            report.status = 'cancelled'
            report.save()
            logger.info(f"Cancelled report {report.id}")

        # Delete the report
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WebsiteListView(generics.ListCreateAPIView):
    """List and create websites"""
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Website.objects.all()

        # Search by domain or company name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(domain__icontains=search) |
                Q(company_name__icontains=search)
            )

        return queryset.order_by('-created_at')


class WebsiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a website"""
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    permission_classes = [permissions.AllowAny]


class ReportTemplateListView(generics.ListCreateAPIView):
    """List and create report templates"""
    queryset = ReportTemplate.objects.filter(is_active=True)
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.AllowAny]


class ReportShareCreateView(generics.CreateAPIView):
    """Create a shareable link for a report"""
    serializer_class = ReportShareCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)

            # Check if report is completed
            if report.status != 'completed':
                return Response(
                    {'error': 'Report must be completed before sharing'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Create share
            share = serializer.save(report=report)

            response_serializer = ReportShareSerializer(share)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Report.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SharedReportView(APIView):
    """Access a shared report via share token"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, share_token):
        try:
            share = ReportShare.objects.select_related('report__website').get(
                share_token=share_token
            )

            # Check if share is accessible
            if not share.is_accessible:
                if share.is_expired:
                    return Response(
                        {'error': 'Share link has expired'},
                        status=status.HTTP_410_GONE
                    )
                elif share.max_views and share.current_views >= share.max_views:
                    return Response(
                        {'error': 'Share link has reached maximum views'},
                        status=status.HTTP_410_GONE
                    )
                else:
                    return Response(
                        {'error': 'Share link is not accessible'},
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Check password if required
            if share.share_type == 'password':
                provided_password = request.query_params.get('password')
                if not provided_password or provided_password != share.password:
                    return Response(
                        {'error': 'Password required or incorrect'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

            # Check email access if required
            if share.share_type == 'email':
                provided_email = request.query_params.get('email')
                if not provided_email or provided_email not in share.allowed_emails:
                    return Response(
                        {'error': 'Email not authorized'},
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Increment view count
            share.current_views += 1
            share.save()

            # Return report data
            report_serializer = ReportDetailSerializer(share.report)
            return Response(report_serializer.data)

        except ReportShare.DoesNotExist:
            return Response(
                {'error': 'Share link not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ReportAnalyticsView(APIView):
    """Get analytics and statistics about reports"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.db.models import Count, Avg, Q
        from datetime import datetime, timedelta

        # Date filters
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # Basic statistics
        total_reports = Report.objects.count()
        completed_reports = Report.objects.filter(status='completed').count()
        failed_reports = Report.objects.filter(status='failed').count()
        processing_reports = Report.objects.filter(
            status__in=['pending', 'processing']
        ).count()

        # Recent statistics
        recent_reports = Report.objects.filter(created_at__gte=start_date)
        recent_count = recent_reports.count()
        recent_completed = recent_reports.filter(status='completed').count()

        # Average processing time
        avg_processing_time = Report.objects.filter(
            status='completed',
            processing_time_seconds__isnull=False
        ).aggregate(Avg('processing_time_seconds'))['processing_time_seconds__avg']

        # Popular domains
        popular_domains = Website.objects.annotate(
            report_count=Count('reports')
        ).filter(report_count__gt=0).order_by('-report_count')[:10]

        # Reports by status
        status_breakdown = Report.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        # Reports by type
        type_breakdown = Report.objects.values('report_type').annotate(
            count=Count('id')
        ).order_by('-count')

        return Response({
            'total_reports': total_reports,
            'completed_reports': completed_reports,
            'failed_reports': failed_reports,
            'processing_reports': processing_reports,
            'recent_reports': recent_count,
            'recent_completed': recent_completed,
            'success_rate': (completed_reports / max(total_reports, 1)) * 100,
            'avg_processing_time_seconds': avg_processing_time,
            'popular_domains': [
                {
                    'domain': domain.domain,
                    'company_name': domain.company_name,
                    'report_count': domain.report_count
                }
                for domain in popular_domains
            ],
            'status_breakdown': list(status_breakdown),
            'type_breakdown': list(type_breakdown),
        })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_website_url(request):
    """Validate a website URL before creating a report"""
    url = request.data.get('url')

    if not url:
        return Response(
            {'error': 'URL is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        import requests
        from urllib.parse import urlparse

        # Basic URL validation
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            return Response(
                {'error': 'Invalid URL format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if URL is accessible
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            is_accessible = response.status_code < 400
            final_url = response.url
        except requests.RequestException:
            is_accessible = False
            final_url = url

        # Check if we already have reports for this domain
        domain = parsed_url.netloc
        existing_reports = Report.objects.filter(
            website__domain=domain
        ).count()

        return Response({
            'valid': True,
            'accessible': is_accessible,
            'final_url': final_url,
            'domain': domain,
            'existing_reports': existing_reports,
            'message': 'URL is valid and accessible' if is_accessible else 'URL is valid but may not be accessible'
        })

    except Exception as e:
        return Response(
            {'error': f'Error validating URL: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )