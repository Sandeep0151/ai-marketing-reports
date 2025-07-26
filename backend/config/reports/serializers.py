# reports/serializers.py
from rest_framework import serializers
from .models import Website, Report, ReportTemplate, APIUsage, ReportShare
from urllib.parse import urlparse


class WebsiteSerializer(serializers.ModelSerializer):
    """Serializer for Website model"""

    class Meta:
        model = Website
        fields = ['id', 'url', 'domain', 'company_name', 'industry', 'created_at', 'updated_at']
        read_only_fields = ['id', 'domain', 'created_at', 'updated_at']

    def validate_url(self, value):
        """Validate URL format and accessibility"""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")

        # Extract domain for validation
        try:
            parsed_url = urlparse(value)
            if not parsed_url.netloc:
                raise serializers.ValidationError("Invalid URL format")
        except Exception:
            raise serializers.ValidationError("Invalid URL format")

        return value


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new reports"""
    website_url = serializers.URLField(write_only=True)

    class Meta:
        model = Report
        fields = [
            'website_url', 'report_type', 'requester_email',
            'requester_name'
        ]

    def create(self, validated_data):
        website_url = validated_data.pop('website_url')

        # Get or create website
        parsed_url = urlparse(website_url)
        domain = parsed_url.netloc

        website, created = Website.objects.get_or_create(
            domain=domain,
            defaults={
                'url': website_url,
                'domain': domain
            }
        )

        # Create report
        report = Report.objects.create(
            website=website,
            **validated_data
        )

        return report


class ReportDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Report model"""
    website = WebsiteSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Report
        fields = [
            'id', 'website', 'status', 'report_type', 'requester_email',
            'requester_name', 'executive_summary', 'seo_data', 'social_data',
            'reputation_data', 'competitor_data', 'trust_score',
            'growth_opportunities', 'technical_analysis', 'created_at',
            'updated_at', 'completed_at', 'processing_started_at',
            'processing_steps', 'error_messages', 'processing_time_seconds',
            'progress_percentage'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'completed_at',
            'processing_started_at', 'processing_time_seconds',
            'progress_percentage'
        ]


class ReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing reports"""
    website = WebsiteSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Report
        fields = [
            'id', 'website', 'status', 'report_type', 'created_at',
            'completed_at', 'processing_time_seconds', 'progress_percentage'
        ]


class ReportProgressSerializer(serializers.ModelSerializer):
    """Serializer for report progress updates"""
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Report
        fields = [
            'id', 'status', 'processing_steps', 'error_messages',
            'progress_percentage', 'updated_at'
        ]


class ExecutiveSummarySerializer(serializers.Serializer):
    """Serializer for executive summary data structure"""
    organic_traffic_change = serializers.CharField(max_length=50)
    ai_visibility = serializers.FloatField()
    avg_rating = serializers.FloatField()
    summary_text = serializers.CharField()
    key_metrics = serializers.DictField(required=False)
    month_over_month = serializers.DictField(required=False)


class SEODataSerializer(serializers.Serializer):
    """Serializer for SEO data structure"""
    title = serializers.CharField(max_length=500, required=False)
    description = serializers.CharField(required=False)
    keywords = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    page_speed_score = serializers.IntegerField(min_value=0, max_value=100, required=False)
    mobile_friendly = serializers.BooleanField(required=False)
    ssl_certificate = serializers.BooleanField(required=False)
    structured_data = serializers.ListField(required=False)
    internal_links = serializers.IntegerField(required=False)
    external_links = serializers.IntegerField(required=False)
    images_count = serializers.IntegerField(required=False)
    traffic_data = serializers.ListField(
        child=serializers.DictField(), required=False
    )


class SocialDataSerializer(serializers.Serializer):
    """Serializer for social media data structure"""
    instagram = serializers.DictField(required=False)
    facebook = serializers.DictField(required=False)
    twitter = serializers.DictField(required=False)
    linkedin = serializers.DictField(required=False)
    youtube = serializers.DictField(required=False)
    tiktok = serializers.DictField(required=False)
    social_mentions = serializers.DictField(required=False)
    engagement_analysis = serializers.DictField(required=False)


class TrustScoreSerializer(serializers.Serializer):
    """Serializer for trust score data structure"""
    overall = serializers.FloatField(min_value=0, max_value=10)
    breakdown = serializers.DictField(required=False)
    factors = serializers.DictField(required=False)
    recommendations = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class CompetitorDataSerializer(serializers.Serializer):
    """Serializer for competitor data structure"""
    competitors = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    market_position = serializers.DictField(required=False)
    competitive_gaps = serializers.ListField(required=False)
    opportunities = serializers.ListField(required=False)


class GrowthOpportunitySerializer(serializers.Serializer):
    """Serializer for growth opportunities"""
    category = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    priority = serializers.ChoiceField(choices=['high', 'medium', 'low'])
    estimated_impact = serializers.CharField(max_length=100)
    effort_required = serializers.CharField(max_length=100)
    timeline = serializers.CharField(max_length=100)


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for Report Template"""

    class Meta:
        model = ReportTemplate
        fields = '__all__'


class APIUsageSerializer(serializers.ModelSerializer):
    """Serializer for API Usage tracking"""

    class Meta:
        model = APIUsage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ReportShareSerializer(serializers.ModelSerializer):
    """Serializer for Report Sharing"""
    is_expired = serializers.ReadOnlyField()
    is_accessible = serializers.ReadOnlyField()

    class Meta:
        model = ReportShare
        fields = [
            'id', 'share_token', 'share_type', 'password', 'allowed_emails',
            'max_views', 'current_views', 'expires_at', 'created_at',
            'created_by_email', 'is_active', 'is_expired', 'is_accessible'
        ]
        read_only_fields = ['id', 'share_token', 'current_views', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class ReportShareCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating report shares"""

    class Meta:
        model = ReportShare
        fields = [
            'share_type', 'password', 'allowed_emails', 'max_views',
            'expires_at', 'created_by_email'
        ]