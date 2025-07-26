# reports/models.py
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator


class Website(models.Model):
    """Website model to store basic website information"""
    url = models.URLField(max_length=500, validators=[URLValidator()])
    domain = models.CharField(max_length=255, db_index=True)
    company_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['domain']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.domain} ({self.company_name})" if self.company_name else self.domain

    def save(self, *args, **kwargs):
        if not self.domain and self.url:
            from urllib.parse import urlparse
            self.domain = urlparse(self.url).netloc
        super().save(*args, **kwargs)


class Report(models.Model):
    """Main report model storing all analysis data"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    REPORT_TYPE_CHOICES = [
        ('basic', 'Basic Report'),
        ('comprehensive', 'Comprehensive Report'),
        ('competitor', 'Competitor Analysis'),
        ('seo_only', 'SEO Only'),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='reports')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='comprehensive')

    # Contact information
    requester_email = models.EmailField(blank=True)
    requester_name = models.CharField(max_length=255, blank=True)

    # Report data - stored as JSON for flexibility
    executive_summary = models.JSONField(default=dict, blank=True)
    seo_data = models.JSONField(default=dict, blank=True)
    social_data = models.JSONField(default=dict, blank=True)
    reputation_data = models.JSONField(default=dict, blank=True)
    competitor_data = models.JSONField(default=dict, blank=True)
    trust_score = models.JSONField(default=dict, blank=True)
    growth_opportunities = models.JSONField(default=list, blank=True)
    technical_analysis = models.JSONField(default=dict, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)

    # Processing metadata
    processing_steps = models.JSONField(default=list, blank=True)  # Track progress
    error_messages = models.JSONField(default=list, blank=True)
    processing_time_seconds = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['website', 'created_at']),
        ]

    def __str__(self):
        return f"Report {self.id} for {self.website.domain} - {self.status}"

    def save(self, *args, **kwargs):
        # Update completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()

        # Calculate processing time
        if self.completed_at and self.processing_started_at:
            time_diff = self.completed_at - self.processing_started_at
            self.processing_time_seconds = int(time_diff.total_seconds())

        super().save(*args, **kwargs)

    @property
    def progress_percentage(self):
        """Calculate progress based on completed steps"""
        if not self.processing_steps:
            return 0

        completed_steps = sum(1 for step in self.processing_steps if step.get('status') == 'completed')
        total_steps = len(self.processing_steps)

        if total_steps == 0:
            return 0

        return (completed_steps / total_steps) * 100


class ReportTemplate(models.Model):
    """Template for different types of reports"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    report_type = models.CharField(max_length=20, choices=Report.REPORT_TYPE_CHOICES)

    # Configuration for what data to collect
    include_seo = models.BooleanField(default=True)
    include_social = models.BooleanField(default=True)
    include_reputation = models.BooleanField(default=True)
    include_competitors = models.BooleanField(default=True)
    include_technical = models.BooleanField(default=True)

    # Processing steps configuration
    processing_steps_config = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class APIUsage(models.Model):
    """Track API usage for monitoring and billing"""

    API_CHOICES = [
        ('openai', 'OpenAI'),
        ('google_pagespeed', 'Google PageSpeed'),
        ('google_search_console', 'Google Search Console'),
        ('semrush', 'SEMrush'),
        ('serpapi', 'SerpAPI'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='api_usage')
    api_name = models.CharField(max_length=50, choices=API_CHOICES)
    endpoint = models.CharField(max_length=200)

    # Usage metrics
    requests_count = models.IntegerField(default=1)
    tokens_used = models.IntegerField(null=True, blank=True)  # For OpenAI
    cost_usd = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    # Response metadata
    response_time_ms = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.api_name} usage for Report {self.report.id}"


class ReportShare(models.Model):
    """Model for sharing reports with clients"""

    SHARE_TYPE_CHOICES = [
        ('public', 'Public Link'),
        ('private', 'Private Link'),
        ('password', 'Password Protected'),
        ('email', 'Email Only'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='shares')
    share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    share_type = models.CharField(max_length=20, choices=SHARE_TYPE_CHOICES, default='private')

    # Access control
    password = models.CharField(max_length=100, blank=True)
    allowed_emails = models.JSONField(default=list, blank=True)
    max_views = models.IntegerField(null=True, blank=True)
    current_views = models.IntegerField(default=0)

    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_email = models.EmailField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Share for Report {self.report.id} - {self.share_type}"

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def is_accessible(self):
        if not self.is_active or self.is_expired:
            return False

        if self.max_views and self.current_views >= self.max_views:
            return False

        return True