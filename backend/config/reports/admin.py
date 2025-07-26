# reports/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Website, Report, ReportTemplate, APIUsage, ReportShare


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['domain', 'company_name', 'industry', 'report_count', 'created_at']
    list_filter = ['industry', 'created_at']
    search_fields = ['domain', 'company_name', 'url']
    readonly_fields = ['created_at', 'updated_at']

    def report_count(self, obj):
        count = obj.reports.count()
        if count > 0:
            url = reverse('admin:reports_report_changelist') + f'?website__id={obj.id}'
            return format_html('<a href="{}">{} reports</a>', url, count)
        return '0 reports'

    report_count.short_description = 'Reports'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'website_link', 'status', 'report_type', 'progress_bar', 'created_at', 'processing_time']
    list_filter = ['status', 'report_type', 'created_at']
    search_fields = ['id', 'website__domain', 'website__company_name', 'requester_email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'processing_started_at',
                       'processing_time_seconds']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'website', 'status', 'report_type', 'requester_email', 'requester_name')
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at', 'processing_started_at', 'completed_at', 'processing_time_seconds'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processing_steps', 'error_messages'),
            'classes': ('collapse',)
        }),
        ('Report Data', {
            'fields': ('executive_summary', 'seo_data', 'social_data', 'reputation_data', 'competitor_data',
                       'trust_score', 'growth_opportunities'),
            'classes': ('collapse',)
        })
    )

    def website_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.website.url, obj.website.domain)

    website_link.short_description = 'Website'

    def progress_bar(self, obj):
        progress = obj.progress_percentage
        if obj.status == 'completed':
            color = 'green'
        elif obj.status == 'failed':
            color = 'red'
        elif obj.status == 'processing':
            color = 'blue'
        else:
            color = 'gray'

        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%</div></div>',
            progress, color, int(progress)
        )

    progress_bar.short_description = 'Progress'

    def processing_time(self, obj):
        if obj.processing_time_seconds:
            minutes = obj.processing_time_seconds // 60
            seconds = obj.processing_time_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"

    processing_time.short_description = 'Processing Time'

    actions = ['regenerate_reports', 'cancel_processing_reports']

    def regenerate_reports(self, request, queryset):
        from .tasks import generate_marketing_report

        count = 0