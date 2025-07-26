# data_collectors/seo_collector.py
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class SEODataCollector:
    """Collect SEO-related data"""

    def __init__(self):
        self.google_api_key = settings.GOOGLE_API_KEY

    def collect_seo_data(self, url: str, website_data: Dict) -> Dict:
        """Collect comprehensive SEO data"""
        try:
            seo_data = {
                'url': url,
                'collection_timestamp': time.time(),

                # Basic SEO elements from website analysis
                'title': website_data.get('title', ''),
                'description': website_data.get('description', ''),
                'keywords': website_data.get('keywords', ''),
                'canonical_url': website_data.get('canonical_url', ''),
                'structured_data': website_data.get('structured_data', []),

                # Technical SEO
                'page_speed': self._get_page_speed_insights(url),
                'mobile_friendly': self._check_mobile_friendly(url),
                'ssl_certificate': website_data.get('has_ssl', False),
                'robots_txt': website_data.get('has_robots_txt', False),
                'sitemap_xml': website_data.get('has_sitemap', False),

                # Content analysis
                'word_count': website_data.get('word_count', 0),
                'heading_structure': website_data.get('heading_structure', {}),
                'internal_links': website_data.get('links', {}).get('internal_links', 0),
                'external_links': website_data.get('links', {}).get('external_links', 0),
                'images_analysis': website_data.get('images', {}),

                # Social and Open Graph
                'social_tags': website_data.get('social_tags', {}),

                # Basic keyword analysis
                'keyword_density': self._analyze_keyword_density(website_data),

                # Recommendations
                'seo_recommendations': self._generate_seo_recommendations(website_data),
            }

            logger.info(f"SEO data collection completed for {url}")
            return seo_data

        except Exception as e:
            logger.error(f"Error collecting SEO data for {url}: {e}")
            return {'error': str(e)}

    def _get_page_speed_insights(self, url: str) -> Dict:
        """Get PageSpeed Insights data"""
        if not self.google_api_key:
            return {'error': 'Google API key not configured'}

        try:
            api_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
            params = {
                'url': url,
                'key': self.google_api_key,
                'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO']
            }

            response = requests.get(api_url, params=params, timeout=30)
            data = response.json()

            if 'error' in data:
                return {'error': data['error']['message']}

            lighthouse_result = data.get('lighthouseResult', {})
            categories = lighthouse_result.get('categories', {})

            return {
                'performance_score': categories.get('performance', {}).get('score', 0) * 100,
                'accessibility_score': categories.get('accessibility', {}).get('score', 0) * 100,
                'best_practices_score': categories.get('best-practices', {}).get('score', 0) * 100,
                'seo_score': categories.get('seo', {}).get('score', 0) * 100,
                'loading_experience': data.get('loadingExperience', {}),
                'origin_loading_experience': data.get('originLoadingExperience', {}),
            }

        except Exception as e:
            logger.error(f"Error getting PageSpeed Insights for {url}: {e}")
            return {'error': str(e)}

    def _check_mobile_friendly(self, url: str) -> Dict:
        """Check mobile-friendliness using Google Mobile-Friendly Test API"""
        if not self.google_api_key:
            return {'mobile_friendly': None, 'error': 'API key not configured'}

        try:
            api_url = 'https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run'
            headers = {'Content-Type': 'application/json'}
            data = {
                'url': url,
                'requestScreenshot': False
            }

            response = requests.post(
                f"{api_url}?key={self.google_api_key}",
                headers=headers,
                json=data,
                timeout=20
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'mobile_friendly': result.get('mobileFriendliness') == 'MOBILE_FRIENDLY',
                    'mobile_friendly_issues': result.get('mobileFriendlyIssues', []),
                    'resource_issues': result.get('resourceIssues', [])
                }
            else:
                return {'mobile_friendly': None, 'error': 'API request failed'}

        except Exception as e:
            logger.error(f"Error checking mobile-friendliness for {url}: {e}")
            return {'mobile_friendly': None, 'error': str(e)}

    def _analyze_keyword_density(self, website_data: Dict) -> Dict:
        """Analyze keyword density from page content"""
        try:
            # This is a simplified version - in production, you'd want more sophisticated analysis
            title = website_data.get('title', '').lower()
            description = website_data.get('description', '').lower()
            headings = website_data.get('heading_structure', {})

            # Combine all text
            all_text = f"{title} {description}"
            for heading_level, heading_texts in headings.items():
                all_text += " " + " ".join(heading_texts).lower()

            # Simple word frequency analysis
            words = all_text.split()
            word_count = {}
            total_words = len(words)

            for word in words:
                # Clean word (remove punctuation)
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3:  # Only count words longer than 3 characters
                    word_count[clean_word] = word_count.get(clean_word, 0) + 1

            # Calculate density and get top keywords
            keyword_density = {}
            for word, count in word_count.items():
                density = (count / total_words) * 100
                if density > 0.5:  # Only include words with >0.5% density
                    keyword_density[word] = {
                        'count': count,
                        'density': round(density, 2)
                    }

            # Sort by density
            top_keywords = sorted(
                keyword_density.items(),
                key=lambda x: x[1]['density'],
                reverse=True
            )[:10]

            return {
                'total_words': total_words,
                'unique_words': len(word_count),
                'top_keywords': dict(top_keywords),
                'keyword_diversity': len(word_count) / max(total_words, 1)
            }

        except Exception as e:
            logger.error(f"Error analyzing keyword density: {e}")
            return {'error': str(e)}

    def _generate_seo_recommendations(self, website_data: Dict) -> List[str]:
        """Generate SEO recommendations based on analysis"""
        recommendations = []

        # Title analysis
        title = website_data.get('title', '')
        if not title:
            recommendations.append("Add a title tag to your page")
        elif len(title) < 30:
            recommendations.append("Title tag is too short - aim for 50-60 characters")
        elif len(title) > 60:
            recommendations.append("Title tag is too long - keep it under 60 characters")

        # Description analysis
        description = website_data.get('description', '')
        if not description:
            recommendations.append("Add a meta description to your page")
        elif len(description) < 120:
            recommendations.append("Meta description is too short - aim for 150-160 characters")
        elif len(description) > 160:
            recommendations.append("Meta description is too long - keep it under 160 characters")

        # Heading structure
        headings = website_data.get('heading_structure', {})
        if not headings.get('h1'):
            recommendations.append("Add an H1 heading to your page")
        elif len(headings.get('h1', [])) > 1:
            recommendations.append("Use only one H1 heading per page")

        # Images
        images = website_data.get('images', {})
        if images.get('without_alt_text', 0) > 0:
            recommendations.append(f"Add alt text to {images['without_alt_text']} images")

        # Technical SEO
        if not website_data.get('has_ssl'):
            recommendations.append("Install SSL certificate for HTTPS")

        if not website_data.get('has_robots_txt'):
            recommendations.append("Create a robots.txt file")

        if not website_data.get('has_sitemap'):
            recommendations.append("Create and submit an XML sitemap")

        # Content
        word_count = website_data.get('word_count', 0)
        if word_count < 300:
            recommendations.append("Add more content - aim for at least 300 words")

        # Internal linking
        links = website_data.get('links', {})
        if links.get('internal_links', 0) < 3:
            recommendations.append("Add more internal links to improve site structure")

        # Mobile optimization
        mobile_features = website_data.get('mobile_optimized', {})
        if not mobile_features.get('has_viewport_meta'):
            recommendations.append("Add viewport meta tag for mobile optimization")

        # Structured data
        if not website_data.get('structured_data'):
            recommendations.append("Add structured data markup for better search visibility")

        return recommendations