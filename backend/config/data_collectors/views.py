# data_collectors/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .website_analyzer import WebsiteAnalyzer
from .seo_collector import SEODataCollector
from django.shortcuts import render
import requests


class AnalyzeWebsiteView(APIView):
    """Analyze a website and return basic information"""

    def post(self, request):
        url = request.data.get('url')

        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            analyzer = WebsiteAnalyzer()
            analysis = analyzer.analyze_website(url)

            return Response(analysis)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CollectSEODataView(APIView):
    """Collect SEO data for a website"""

    def post(self, request):
        url = request.data.get('url')

        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # First analyze the website
            analyzer = WebsiteAnalyzer()
            website_data = analyzer.analyze_website(url)

            if 'error' in website_data:
                return Response(website_data, status=status.HTTP_400_BAD_REQUEST)

            # Then collect SEO data
            seo_collector = SEODataCollector()
            seo_data = seo_collector.collect_seo_data(url, website_data)

            return Response(seo_data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestAPIConnectionView(APIView):
    """Test API connections"""

    def get(self, request):
        results = {}

        # Test Google PageSpeed Insights
        try:
            from django.conf import settings
            if settings.GOOGLE_API_KEY:
                api_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
                params = {
                    'url': 'https://example.com',
                    'key': settings.GOOGLE_API_KEY
                }
                response = requests.get(api_url, params=params, timeout=10)
                results['google_pagespeed'] = {
                    'status': 'success' if response.status_code == 200 else 'failed',
                    'status_code': response.status_code
                }
            else:
                results['google_pagespeed'] = {'status': 'not_configured'}
        except Exception as e:
            results['google_pagespeed'] = {'status': 'error', 'message': str(e)}

        return Response(results)


class CollectSocialDataView(APIView):
    """Collect social media data"""

    def post(self, request):
        # Placeholder for social data collection
        return Response({
            'message': 'Social data collection not yet implemented',
            'status': 'placeholder'
        })


class CollectReputationDataView(APIView):
    """Collect reputation data"""

    def post(self, request):
        # Placeholder for reputation data collection
        return Response({
            'message': 'Reputation data collection not yet implemented',
            'status': 'placeholder'
        })


class CollectCompetitorDataView(APIView):
    """Collect competitor data"""

    def post(self, request):
        # Placeholder for competitor data collection
        return Response({
            'message': 'Competitor data collection not yet implemented',
            'status': 'placeholder'
        })




# Create your views here.
