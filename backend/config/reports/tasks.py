# reports/tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.conf import settings
import logging
import json
import time
import traceback

from .models import Report, APIUsage
from data_collectors.website_analyzer import WebsiteAnalyzer
from data_collectors.seo_collector import SEODataCollector
from data_collectors.social_collector import SocialDataCollector
from data_collectors.reputation_collector import ReputationCollector
from data_collectors.competitor_collector import CompetitorCollector
from ai_analyzer.trust_score import TrustScoreCalculator
from ai_analyzer.summary_generator import SummaryGenerator
from ai_analyzer.growth_analyzer import GrowthAnalyzer

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_marketing_report(self, report_id):
    """
    Main task for generating a comprehensive marketing report

    Args:
        report_id: UUID string of the report to generate

    Returns:
        Dict with generation results and metrics
    """
    channel_layer = get_channel_layer()
    group_name = f'report_{report_id}'

    def send_progress(step, status, progress, message, error=None):
        """Send progress update via WebSocket"""
        try:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'report_progress_update',
                        'step': step,
                        'status': status,
                        'progress': progress,
                        'message': message,
                        'timestamp': timezone.now().isoformat(),
                        'error': error
                    }
                )
        except Exception as e:
            logger.error(f"Failed to send progress update: {e}")

    def send_status_update(status, message=""):
        """Send status update via WebSocket"""
        try:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'report_status_update',
                        'report_id': report_id,
                        'status': status,
                        'message': message,
                        'timestamp': timezone.now().isoformat(),
                    }
                )
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")

    def update_processing_step(report, step_name, status, progress, message):
        """Update a specific processing step in the report"""
        try:
            for step in report.processing_steps:
                if step['step'] == step_name:
                    step.update({
                        'status': status,
                        'progress': progress,
                        'message': message,
                        'updated_at': timezone.now().isoformat()
                    })
                    break
            report.save()
        except Exception as e:
            logger.error(f"Failed to update processing step: {e}")

    try:
        # Get report instance
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            logger.error(f"Report {report_id} not found")
            return {'error': 'Report not found'}

        # Update report status
        report.status = 'processing'
        report.processing_started_at = timezone.now()
        report.error_messages = []  # Clear previous errors
        report.save()

        send_status_update('processing', 'Starting report generation...')
        logger.info(f"Starting report generation for {report.website.url}")

        # Initialize processing steps
        processing_steps = [
            {'step': 'website_analysis', 'status': 'pending', 'progress': 0,
             'message': 'Analyzing website structure and content...'},
            {'step': 'seo_analysis', 'status': 'pending', 'progress': 0,
             'message': 'Collecting SEO performance data...'},
            {'step': 'social_analysis', 'status': 'pending', 'progress': 0,
             'message': 'Analyzing social media presence...'},
            {'step': 'reputation_analysis', 'status': 'pending', 'progress': 0,
             'message': 'Checking online reputation and reviews...'},
            {'step': 'competitor_analysis', 'status': 'pending', 'progress': 0,
             'message': 'Analyzing competitive landscape...'},
            {'step': 'ai_analysis', 'status': 'pending', 'progress': 0, 'message': 'Running AI-powered analysis...'},
            {'step': 'report_compilation', 'status': 'pending', 'progress': 0,
             'message': 'Compiling final report and recommendations...'},
        ]

        report.processing_steps = processing_steps
        report.save()

        # Dictionary to store all collected data
        collected_data = {}

        # Step 1: Website Analysis
        try:
            send_progress('website_analysis', 'in_progress', 10, 'Analyzing website structure and content...')
            logger.info(f"Starting website analysis for {report.website.url}")

            website_analyzer = WebsiteAnalyzer()
            website_data = website_analyzer.analyze_website(report.website.url)

            if 'error' in website_data:
                raise Exception(f"Website analysis failed: {website_data['error']}")

            collected_data['website_data'] = website_data

            # Update company name if found
            if website_data.get('company_name') and not report.website.company_name:
                report.website.company_name = website_data['company_name']
                report.website.save()

            update_processing_step(report, 'website_analysis', 'completed', 100,
                                   'Website analysis completed successfully')
            send_progress('website_analysis', 'completed', 100, 'Website analysis completed')
            logger.info(f"Website analysis completed for {report.website.url}")

        except Exception as e:
            error_msg = f"Website analysis failed: {str(e)}"
            logger.error(error_msg)
            update_processing_step(report, 'website_analysis', 'failed', 0, error_msg)
            send_progress('website_analysis', 'failed', 0, error_msg, str(e))

            # Use fallback data
            collected_data['website_data'] = {
                'url': report.website.url,
                'domain': report.website.domain,
                'error': str(e),
                'has_ssl': report.website.url.startswith('https://'),
                'title': f"Analysis for {report.website.domain}",
                'word_count': 0
            }

        # Step 2: SEO Analysis
        try:
            send_progress('seo_analysis', 'in_progress', 30, 'Collecting SEO performance data...')
            logger.info(f"Starting SEO analysis for {report.website.url}")

            seo_collector = SEODataCollector()
            seo_data = seo_collector.collect_seo_data(report.website.url, collected_data['website_data'])

            collected_data['seo_data'] = seo_data
            report.seo_data = seo_data

            update_processing_step(report, 'seo_analysis', 'completed', 100, 'SEO analysis completed successfully')
            send_progress('seo_analysis', 'completed', 100, 'SEO data collection completed')
            logger.info(f"SEO analysis completed for {report.website.url}")

        except Exception as e:
            error_msg = f"SEO analysis failed: {str(e)}"
            logger.error(error_msg)
            update_processing_step(report, 'seo_analysis', 'failed', 0, error_msg)
            send_progress('seo_analysis', 'failed', 0, error_msg, str(e))

            # Use fallback data
            collected_data['seo_data'] = {
                'url': report.website.url,
                'error': str(e),
                'page_speed': {'performance_score': 0, 'seo_score': 0},
                'mobile_friendly': {'mobile_friendly': False}
            }

        # Step 3: Social Media Analysis
        try:
            send_progress('social_analysis', 'in_progress', 50, 'Analyzing social media presence...')
            logger.info(f"Starting social media analysis for {report.website.url}")

            social_collector = SocialDataCollector()
            social_data = social_collector.collect_social_data(
                report.website.domain,
                collected_data['website_data'].get('company_name', '')
            )

            collected_data['social_data'] = social_data
            report.social_data = social_data

            update_processing_step(report, 'social_analysis', 'completed', 100, 'Social media analysis completed')
            send_progress('social_analysis', 'completed', 100, 'Social media analysis completed')
            logger.info(f"Social media analysis completed for {report.website.url}")

        except Exception as e:
            error_msg = f"Social media analysis failed: {str(e)}"
            logger.error(error_msg)
            update_processing_step(report, 'social_analysis', 'failed', 0, error_msg)
            send_progress('social_analysis', 'failed', 0, error_msg, str(e))

            # Use fallback data
            collected_data['social_data'] = {
                'domain': report.website.domain,
                'error': str(e),
                'platforms': {}
            }

        # Step 4: Reputation Analysis
        try:
            send_progress('reputation_analysis', 'in_progress', 65, 'Checking online reputation and reviews...')
            logger.info(f"Starting reputation analysis for {report.website.url}")

            reputation_collector = ReputationCollector()
            reputation_data = reputation_collector.collect_reputation_data(
                report.website.domain,
                collected_data['website_data'].get('company_name', '')
            )

            collected_data['reputation_data'] = reputation_data
            report.reputation_data = reputation_data

            update_processing_step(report, 'reputation_analysis', 'completed', 100, 'Reputation analysis completed')
            send_progress('reputation_analysis', 'completed', 100, 'Reputation analysis completed')
            logger.info(f"Reputation analysis completed for {report.website.url}")

        except Exception as e:
            error_msg = f"Reputation analysis failed: {str(e)}"
            logger.error(error_msg)
            update_processing_step(report, 'reputation_analysis', 'failed', 0, error_msg)
            send_progress('reputation_analysis', 'failed', 0, error_msg, str(e))

            # Use fallback data
            collected_data['reputation_data'] = {
                'domain': report.website.domain,
                'error': str(e),
                'overall_rating': 0,
                'reviews': []
            }

        # Step 5: Competitor Analysis
        try:
            send_progress('competitor_analysis', 'in_progress', 75, 'Analyzing competitive landscape...')
            logger.info(f"Starting competitor analysis for {report.website.url}")

            competitor_collector = CompetitorCollector()
            # Extract keywords from SEO data for competitor analysis
            keywords = []
            if 'seo_data' in collected_data and 'keyword_density' in collected_data['seo_data']:
                keyword_data = collected_data['seo_data']['keyword_density'].get('top_keywords', {})
                keywords = list(keyword_data.keys())[:5]  # Top 5 keywords

            competitor_data = competitor_collector.collect_competitor_data(
                report.website.domain,
                keywords
            )

            collected_data['competitor_data'] = competitor_data
            report.competitor_data = competitor_data

            update_processing_step(report, 'competitor_analysis', 'completed', 100, 'Competitor analysis completed')
            send_progress('competitor_analysis', 'completed', 100, 'Competitor analysis completed')
            logger.info(f"Competitor analysis completed for {report.website.url}")

        except Exception as e:
            error_msg = f"Competitor analysis failed: {str(e)}"
            logger.error(error_msg)
            update_processing_step(report, 'competitor_analysis', 'failed', 0, error_msg)
            send_progress('competitor_analysis', 'failed', 0, error_msg, str(e))

            # Use fallback data
            collected_data['competitor_data'] = {
                'domain': report.website.domain,
                'error': str(e),
                'competitors': [],
                'market_position': {}
            }

        # Step 6: AI Analysis
        try:
            send_progress('ai_analysis', 'in_progress', 85, 'Running AI-powered analysis...')
            logger.info(f"Starting AI analysis for {report.website.url}")

            # Calculate trust score
            trust_calculator = TrustScoreCalculator()
            trust_score = trust_calculator.calculate_trust_score(collected_data)

            collected_data['trust_score'] = trust_score
            report.trust_score = trust_score

            # Generate growth recommendations
            growth_analyzer = GrowthAnalyzer()
            growth_opportunities = growth_analyzer.generate_recommendations(collected_data)

            collected_data['growth_opportunities'] = growth_opportunities
            report.growth_opportunities = growth_opportunities

            update_processing_step(report, 'ai_analysis', 'completed', 100, 'AI analysis completed')
            send_progress('ai_analysis', 'completed', 100, 'AI analysis completed')
            logger.info(f"AI analysis completed for {report.website.url}")

        except Exception as e:
            error_msg = f"AI analysis failed: {str(e)}"
            logger.error(error_msg)
            update_processing_step(report, 'ai_analysis', 'failed', 0, error_msg)
            send_progress('ai_analysis', 'failed', 0, error_msg, str(e))

            # Use fallback data
            collected_data['trust_score'] = {'overall': 5.0, 'breakdown': {}, 'error': str(e)}
            collected_data['growth_opportunities'] = []
            report.trust_score = collected_data['trust_score']
            report.growth_opportunities = collected_data['growth_opportunities']

        # Step 7: Report Compilation
        try:
            send_progress('report_compilation', 'in_progress', 95, 'Compiling final report and recommendations...')
            logger.info(f"Starting report compilation for {report.website.url}")

            # Generate executive summary
            summary_generator = SummaryGenerator()
            executive_summary = summary_generator.generate_summary(collected_data)

            report.executive_summary = executive_summary

            # Store technical analysis
            report.technical_analysis = {
                'data_sources_used': list(collected_data.keys()),
                'analysis_timestamp': timezone.now().isoformat(),
                'processing_duration_seconds': int((timezone.now() - report.processing_started_at).total_seconds()),
                'data_quality_score': calculate_data_quality_score(collected_data),
                'collection_errors': [
                    key for key, value in collected_data.items()
                    if isinstance(value, dict) and 'error' in value
                ]
            }

            update_processing_step(report, 'report_compilation', 'completed', 100, 'Report compilation completed')
            send_progress('report_compilation', 'completed', 100, 'Report compilation completed')
            logger.info(f"Report compilation completed for {report.website.url}")

        except Exception as e:
            error_msg = f"Report compilation failed: {str(e)}"
            logger.error(error_msg)
            update_processing_step(report, 'report_compilation', 'failed', 0, error_msg)
            send_progress('report_compilation', 'failed', 0, error_msg, str(e))

            # Create basic executive summary
            report.executive_summary = {
                'summary_text': f"Report generated for {report.website.domain} with basic analysis.",
                'organic_traffic_change': '+0%',
                'ai_visibility': collected_data.get('trust_score', {}).get('overall', 5.0),
                'avg_rating': 0,
                'error': str(e)
            }

        # Final completion
        report.status = 'completed'
        report.completed_at = timezone.now()

        # Calculate processing time
        if report.processing_started_at:
            processing_time = timezone.now() - report.processing_started_at
            report.processing_time_seconds = int(processing_time.total_seconds())

        report.save()

        # Send completion notification
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'report_completed',
                    'report_id': report_id,
                    'timestamp': timezone.now().isoformat(),
                }
            )

            # Send to report list group
            async_to_sync(channel_layer.group_send)(
                'report_list',
                {
                    'type': 'report_status_changed',
                    'report_id': report_id,
                    'old_status': 'processing',
                    'new_status': 'completed',
                    'timestamp': timezone.now().isoformat(),
                }
            )

        logger.info(f"Report generation completed successfully for {report.website.url}")

        # Send email notification if email is provided
        if report.requester_email:
            send_report_notification.delay(report.requester_email, str(report.id))

        return {
            'status': 'completed',
            'report_id': str(report.id),
            'processing_time_seconds': report.processing_time_seconds,
            'data_sources_used': len(collected_data),
            'trust_score': collected_data.get('trust_score', {}).get('overall', 0)
        }

    except Report.DoesNotExist:
        error_msg = f"Report {report_id} not found"
        logger.error(error_msg)
        return {'error': error_msg}

    except Exception as exc:
        error_msg = f"Report generation failed for {report_id}: {str(exc)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")

        try:
            report = Report.objects.get(id=report_id)
            report.status = 'failed'
            if not report.error_messages:
                report.error_messages = []
            report.error_messages.append(str(exc))
            report.save()

            # Send failure notification
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'report_failed',
                        'report_id': report_id,
                        'error': str(exc),
                        'timestamp': timezone.now().isoformat(),
                    }
                )

        except Exception as e:
            logger.error(f"Failed to update report status after error: {e}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying report generation for {report_id}, attempt {self.request.retries + 1}")
            # Exponential backoff: 60s, 120s, 240s
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(countdown=countdown, exc=exc)

        return {'error': error_msg, 'retries_exhausted': True}


def calculate_data_quality_score(collected_data: dict) -> float:
    """Calculate data quality score based on successful collections"""
    total_sources = len(collected_data)
    if total_sources == 0:
        return 0.0

    successful_sources = 0
    for key, value in collected_data.items():
        if isinstance(value, dict) and 'error' not in value:
            successful_sources += 1
        elif not isinstance(value, dict):
            successful_sources += 1

    return round((successful_sources / total_sources) * 100, 1)


@shared_task
def cleanup_old_reports():
    """Clean up old reports and shared links"""
    from datetime import timedelta

    try:
        # Delete reports older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        old_reports = Report.objects.filter(created_at__lt=cutoff_date)

        deleted_count = 0
        for report in old_reports.iterator():
            logger.info(f"Deleting old report {report.id}")
            report.delete()
            deleted_count += 1

        logger.info(f"Cleaned up {deleted_count} old reports")

        # Clean up expired shares
        from .models import ReportShare
        expired_shares = ReportShare.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )

        expired_count = expired_shares.count()
        expired_shares.update(is_active=False)

        logger.info(f"Deactivated {expired_count} expired share links")

        return {
            'deleted_reports': deleted_count,
            'expired_shares': expired_count
        }

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {'error': str(e)}


@shared_task
def send_report_notification(email, report_id):
    """Send email notification when report is completed"""
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        report = Report.objects.get(id=report_id)

        subject = f"Your Marketing Report for {report.website.domain} is Ready!"

        # Create rich HTML email
        context = {
            'report': report,
            'trust_score': report.trust_score.get('overall', 'N/A'),
            'processing_time': report.processing_time_seconds,
            'growth_opportunities_count': len(report.growth_opportunities),
            'report_url': f"{settings.FRONTEND_URL}/report/{report_id}" if hasattr(settings,
                                                                                   'FRONTEND_URL') else f"http://localhost:3000/report/{report_id}",
            'admin_url': f"http://localhost:8000/admin/reports/report/{report_id}/change/"
        }

        # HTML email content
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Your Marketing Report is Ready! 🎉</h2>

                <p>Hello,</p>

                <p>Your comprehensive marketing report for <strong>{report.website.domain}</strong> has been completed successfully!</p>

                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Report Summary</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 10px 0;">🎯 <strong>Trust Score:</strong> {context['trust_score']}/10</li>
                        <li style="margin: 10px 0;">⏱️ <strong>Processing Time:</strong> {context['processing_time'] or 'N/A'} seconds</li>
                        <li style="margin: 10px 0;">📈 <strong>Growth Opportunities:</strong> {context['growth_opportunities_count']} identified</li>
                    </ul>
                </div>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{context['report_url']}" 
                       style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        View Your Report
                    </a>
                </p>

                <p>This report includes:</p>
                <ul>
                    <li>Comprehensive website analysis</li>
                    <li>SEO performance metrics</li>
                    <li>Social media presence evaluation</li>
                    <li>AI-powered trust score calculation</li>
                    <li>Actionable growth recommendations</li>
                </ul>

                <p>Thank you for using our AI Marketing Report Generator!</p>

                <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                    Best regards,<br>
                    The Marketing Report Team
                </p>
            </div>
        </body>
        </html>
        """

        # Plain text fallback
        text_message = f"""
        Hello,

        Your comprehensive marketing report for {report.website.domain} has been completed successfully!

        Report Summary:
        - Trust Score: {context['trust_score']}/10
        - Processing Time: {context['processing_time'] or 'N/A'} seconds
        - Growth Opportunities: {context['growth_opportunities_count']} identified

        View your report at: {context['report_url']}

        Thank you for using our AI Marketing Report Generator!

        Best regards,
        The Marketing Report Team
        """

        send_mail(
            subject,
            text_message,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@marketingreports.com'),
            [email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent report notification to {email} for report {report_id}")
        return {'status': 'sent', 'email': email}

    except Report.DoesNotExist:
        error_msg = f"Report {report_id} not found for email notification"
        logger.error(error_msg)
        return {'error': error_msg}
    except Exception as e:
        error_msg = f"Failed to send email notification: {e}"
        logger.error(error_msg)
        return {'error': error_msg}


@shared_task
def update_report_progress(report_id, step, status, progress, message):
    """Update report progress and send WebSocket notification"""
    try:
        report = Report.objects.get(id=report_id)

        # Update processing steps
        step_updated = False
        for step_data in report.processing_steps:
            if step_data['step'] == step:
                step_data.update({
                    'status': status,
                    'progress': progress,
                    'message': message,
                    'updated_at': timezone.now().isoformat()
                })
                step_updated = True
                break

        if not step_updated:
            # Add new step if not found
            report.processing_steps.append({
                'step': step,
                'status': status,
                'progress': progress,
                'message': message,
                'updated_at': timezone.now().isoformat()
            })

        report.save()

        # Send WebSocket update
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'report_{report_id}',
                {
                    'type': 'report_progress_update',
                    'step': step,
                    'status': status,
                    'progress': progress,
                    'message': message,
                    'timestamp': timezone.now().isoformat(),
                }
            )

        return {'status': 'updated', 'step': step}

    except Exception as e:
        logger.error(f"Failed to update report progress: {e}")
        return {'error': str(e)}


@shared_task
def test_api_connections():
    """Test all API connections and log results"""
    results = {}

    try:
        # Test Google PageSpeed Insights
        if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
            try:
                import requests
                api_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
                params = {
                    'url': 'https://example.com',
                    'key': settings.GOOGLE_API_KEY
                }
                response = requests.get(api_url, params=params, timeout=10)
                results['google_pagespeed'] = {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'message': 'Connected successfully' if response.status_code == 200 else 'Connection failed'
                }
            except Exception as e:
                results['google_pagespeed'] = {
                    'success': False,
                    'error': str(e)
                }
        else:
            results['google_pagespeed'] = {
                'success': False,
                'message': 'API key not configured'
            }

        # Test OpenAI
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            try:
                import openai
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                results['openai'] = {
                    'success': True,
                    'message': 'Connected successfully',
                    'model': 'gpt-3.5-turbo'
                }
            except Exception as e:
                results['openai'] = {
                    'success': False,
                    'error': str(e)
                }
        else:
            results['openai'] = {
                'success': False,
                'message': 'API key not configured'
            }

        # Log results
        for api_name, result in results.items():
            if result['success']:
                logger.info(f"API {api_name} is working correctly")
            else:
                logger.error(f"API {api_name} failed: {result.get('error', result.get('message', 'Unknown error'))}")

        return results

    except Exception as e:
        logger.error(f"Error testing API connections: {e}")
        return {'error': str(e)}


@shared_task
def generate_sample_report():
    """Generate a sample report for testing purposes"""
    try:
        from .models import Website

        # Create or get sample website
        website, created = Website.objects.get_or_create(
            domain='example.com',
            defaults={
                'url': 'https://example.com',
                'company_name': 'Example Company',
                'industry': 'Technology'
            }
        )

        # Create sample report
        report = Report.objects.create(
            website=website,
            report_type='basic',
            requester_email='test@example.com',
            requester_name='Test User'
        )

        logger.info(f"Created sample report with ID: {report.id}")

        # Generate the report
        result = generate_marketing_report.delay(str(report.id))

        return {
            'report_id': str(report.id),
            'task_id': result.id,
            'website_url': website.url,
            'status': 'started'
        }

    except Exception as e:
        logger.error(f"Error generating sample report: {e}")
        return {'error': str(e)}


@shared_task
def batch_process_reports(report_ids):
    """Process multiple reports in batch"""
    results = []

    for report_id in report_ids:
        try:
            result = generate_marketing_report.delay(report_id)
            results.append({
                'report_id': report_id,
                'task_id': result.id,
                'status': 'started'
            })
        except Exception as e:
            results.append({
                'report_id': report_id,
                'status': 'failed',
                'error': str(e)
            })

    return results


@shared_task
def regenerate_failed_reports():
    """Regenerate all failed reports"""
    try:
        failed_reports = Report.objects.filter(status='failed')
        regenerated_count = 0

        for report in failed_reports:
            # Reset report status
            report.status = 'pending'
            report.error_messages = []
            report.processing_steps = []
            report.save()

            # Start regeneration
            generate_marketing_report.delay(str(report.id))
            regenerated_count += 1

            logger.info(f"Regenerating failed report {report.id}")

        logger.info(f"Started regeneration for {regenerated_count} failed reports")
        return {
            'regenerated_count': regenerated_count,
            'status': 'completed'
        }

    except Exception as e:
        logger.error(f"Error regenerating failed reports: {e}")
        return {'error': str(e)}


@shared_task
def monitor_report_processing():
    """Monitor report processing and handle stuck reports"""
    try:
        from datetime import timedelta

        # Find reports that have been processing for more than 30 minutes
        stuck_threshold = timezone.now() - timedelta(minutes=30)
        stuck_reports = Report.objects.filter(
            status='processing',
            processing_started_at__lt=stuck_threshold
        )

        stuck_count = 0
        for report in stuck_reports:
            logger.warning(f"Report {report.id} appears to be stuck, marking as failed")

            report.status = 'failed'
            if not report.error_messages:
                report.error_messages = []
            report.error_messages.append("Report processing timed out after 30 minutes")
            report.save()

            stuck_count += 1

        # Find reports that are pending for more than 1 hour
        pending_threshold = timezone.now() - timedelta(hours=1)
        old_pending = Report.objects.filter(
            status='pending',
            created_at__lt=pending_threshold
        )

        restarted_count = 0
        for report in old_pending:
            logger.info(f"Restarting old pending report {report.id}")
            generate_marketing_report.delay(str(report.id))
            restarted_count += 1

        return {
            'stuck_reports_failed': stuck_count,
            'old_pending_restarted': restarted_count,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error monitoring report processing: {e}")
        return {'error': str(e)}


@shared_task
def generate_analytics_report():
    """Generate analytics report for admin dashboard"""
    try:
        from django.db.models import Count, Avg, Q
        from datetime import timedelta

        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)

        # Basic statistics
        total_reports = Report.objects.count()
        reports_24h = Report.objects.filter(created_at__gte=last_24h).count()
        reports_7d = Report.objects.filter(created_at__gte=last_7d).count()
        reports_30d = Report.objects.filter(created_at__gte=last_30d).count()

        # Status breakdown
        status_breakdown = Report.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        # Average processing time
        avg_processing_time = Report.objects.filter(
            status='completed',
            processing_time_seconds__isnull=False
        ).aggregate(Avg('processing_time_seconds'))['processing_time_seconds__avg']

        # Success rate
        completed_reports = Report.objects.filter(status='completed').count()
        success_rate = (completed_reports / max(total_reports, 1)) * 100

        # Top domains
        top_domains = Report.objects.values('website__domain').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # API usage statistics (if APIUsage model has data)
        try:
            api_usage = APIUsage.objects.filter(
                created_at__gte=last_24h
            ).values('api_name').annotate(
                requests=Count('id'),
                avg_response_time=Avg('response_time_ms')
            ).order_by('-requests')
        except:
            api_usage = []

        analytics = {
            'generated_at': now.isoformat(),
            'period': '30_days',
            'summary': {
                'total_reports': total_reports,
                'reports_24h': reports_24h,
                'reports_7d': reports_7d,
                'reports_30d': reports_30d,
                'success_rate': round(success_rate, 1),
                'avg_processing_time_seconds': round(avg_processing_time or 0, 1)
            },
            'status_breakdown': list(status_breakdown),
            'top_domains': list(top_domains),
            'api_usage': list(api_usage),
            'trends': {
                'daily_growth': reports_24h,
                'weekly_growth': reports_7d,
                'monthly_growth': reports_30d
            }
        }

        logger.info("Generated analytics report successfully")
        return analytics

    except Exception as e:
        logger.error(f"Error generating analytics report: {e}")
        return {'error': str(e)}


@shared_task
def optimize_database():
    """Optimize database performance by cleaning up old data"""
    try:
        from datetime import timedelta

        # Clean up old API usage records (keep only last 30 days)
        api_cutoff = timezone.now() - timedelta(days=30)
        deleted_api_records = APIUsage.objects.filter(
            created_at__lt=api_cutoff
        ).delete()

        # Clean up very old reports (older than 1 year)
        report_cutoff = timezone.now() - timedelta(days=365)
        very_old_reports = Report.objects.filter(
            created_at__lt=report_cutoff
        )
        deleted_old_reports = very_old_reports.count()
        very_old_reports.delete()

        # Clean up orphaned websites (no reports)
        from .models import Website
        orphaned_websites = Website.objects.filter(reports__isnull=True)
        deleted_websites = orphaned_websites.count()
        orphaned_websites.delete()

        logger.info(
            f"Database optimization completed: {deleted_api_records[0]} API records, {deleted_old_reports} old reports, {deleted_websites} orphaned websites deleted")

        return {
            'deleted_api_records': deleted_api_records[0] if deleted_api_records else 0,
            'deleted_old_reports': deleted_old_reports,
            'deleted_orphaned_websites': deleted_websites,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return {'error': str(e)}


# Periodic tasks configuration (add this to your celery beat schedule)
"""
To set up periodic tasks, add this to your Django settings:

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-reports': {
        'task': 'reports.tasks.cleanup_old_reports',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'monitor-report-processing': {
        'task': 'reports.tasks.monitor_report_processing',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'test-api-connections': {
        'task': 'reports.tasks.test_api_connections',
        'schedule': crontab(hour='*/6', minute=0),  # Every 6 hours
    },
    'generate-analytics-report': {
        'task': 'reports.tasks.generate_analytics_report',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
    'optimize-database': {
        'task': 'reports.tasks.optimize_database',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Weekly on Sunday at 3 AM
    },
}
"""