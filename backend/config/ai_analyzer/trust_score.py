# ai_analyzer/trust_score.py
import logging
from typing import Dict
import json

logger = logging.getLogger(__name__)


class TrustScoreCalculator:
    """Calculate trust score based on various website factors"""

    def __init__(self):
        self.max_score = 10.0
        self.weights = {
            'legitimacy': 0.25,
            'transparency': 0.15,
            'customer_feedback': 0.20,
            'service_quality': 0.15,
            'responsiveness': 0.10,
            'innovation': 0.05,
            'web_presence': 0.10
        }

    def calculate_trust_score(self, data: Dict) -> Dict:
        """Calculate comprehensive trust score"""
        try:
            website_data = data.get('website_data', {})
            seo_data = data.get('seo_data', {})
            social_data = data.get('social_data', {})
            reputation_data = data.get('reputation_data', {})

            scores = {
                'legitimacy': self._calculate_legitimacy(website_data, seo_data),
                'transparency': self._calculate_transparency(website_data),
                'customer_feedback': self._calculate_customer_feedback(reputation_data),
                'service_quality': self._calculate_service_quality(website_data, seo_data),
                'responsiveness': self._calculate_responsiveness(website_data, seo_data),
                'innovation': self._calculate_innovation(website_data, seo_data),
                'web_presence': self._calculate_web_presence(website_data, social_data, seo_data)
            }

            # Calculate weighted overall score
            overall_score = sum(
                scores[category] * self.weights[category]
                for category in scores
            )

            # Generate recommendations
            recommendations = self._generate_trust_recommendations(scores, data)

            return {
                'overall': round(min(overall_score, self.max_score), 1),
                'breakdown': {k: round(v, 1) for k, v in scores.items()},
                'factors': self._get_factor_explanations(scores),
                'recommendations': recommendations,
                'calculation_details': {
                    'weights_used': self.weights,
                    'max_possible_score': self.max_score
                }
            }

        except Exception as e:
            logger.error(f"Error calculating trust score: {e}")
            return {
                'overall': 5.0,
                'breakdown': {},
                'error': str(e)
            }

    def _calculate_legitimacy(self, website_data: Dict, seo_data: Dict) -> float:
        """Calculate legitimacy score based on technical and legal indicators"""
        score = 0.0
        max_score = 10.0

        # SSL certificate (2 points)
        if website_data.get('has_ssl'):
            score += 2.0

        # Contact information (2 points)
        contact_info = website_data.get('contact_info', {})
        if contact_info.get('has_email'):
            score += 1.0
        if contact_info.get('has_phone'):
            score += 1.0

        # Privacy policy and terms (1.5 points)
        page_text = str(website_data).lower()
        if 'privacy policy' in page_text or 'privacy' in page_text:
            score += 0.75
        if 'terms of service' in page_text or 'terms' in page_text:
            score += 0.75

        # Professional domain and age indicators (2 points)
        if website_data.get('has_favicon'):
            score += 0.5
        if website_data.get('canonical_url'):
            score += 0.5
        if seo_data.get('robots_txt'):
            score += 0.5
        if seo_data.get('sitemap_xml'):
            score += 0.5

        # Structured data (business registration info) (1.5 points)
        structured_data = website_data.get('structured_data', [])
        if any('organization' in str(data).lower() for data in structured_data):
            score += 1.0
        if any('localbusiness' in str(data).lower() for data in structured_data):
            score += 0.5

        # Professional email addresses (1 point)
        emails = contact_info.get('emails_found', [])
        if any(not email.endswith(('gmail.com', 'yahoo.com', 'hotmail.com')) for email in emails):
            score += 1.0

        return min(score, max_score)

    def _calculate_transparency(self, website_data: Dict) -> float:
        """Calculate transparency score"""
        score = 0.0
        max_score = 10.0

        contact_info = website_data.get('contact_info', {})

        # Contact information availability (4 points)
        if contact_info.get('has_email'):
            score += 1.5
        if contact_info.get('has_phone'):
            score += 1.5
        if contact_info.get('has_address'):
            score += 1.0

        # About/Company information (3 points)
        if website_data.get('company_name'):
            score += 1.5

        headings = website_data.get('heading_structure', {})
        about_indicators = ['about', 'company', 'team', 'who we are']
        page_text = str(headings).lower()
        if any(indicator in page_text for indicator in about_indicators):
            score += 1.5

        # Social media presence (2 points)
        social_links = website_data.get('social_links', {})
        score += min(len(social_links) * 0.4, 2.0)

        # Clear navigation and structure (1 point)
        if headings.get('h1') and headings.get('h2'):
            score += 1.0

        return min(score, max_score)

    def _calculate_customer_feedback(self, reputation_data: Dict) -> float:
        """Calculate customer feedback score"""
        score = 5.0  # Default neutral score
        max_score = 10.0

        # This would be enhanced with actual review data
        # For now, return a placeholder calculation

        if reputation_data:
            # Placeholder logic for when reputation data is available
            avg_rating = reputation_data.get('average_rating', 0)
            if avg_rating > 0:
                score = min(avg_rating * 2, max_score)  # Convert 5-star to 10-point scale

        return min(score, max_score)

    def _calculate_service_quality(self, website_data: Dict, seo_data: Dict) -> float:
        """Calculate service quality indicators"""
        score = 0.0
        max_score = 10.0

        # Website performance (3 points)
        page_speed = seo_data.get('page_speed', {})
        performance_score = page_speed.get('performance_score', 0)
        if performance_score > 0:
            score += (performance_score / 100) * 3.0

        # Content quality (3 points)
        word_count = website_data.get('word_count', 0)
        if word_count > 500:
            score += 1.5
        elif word_count > 200:
            score += 1.0

        headings = website_data.get('heading_structure', {})
        if len(headings.get('h2', [])) >= 3:
            score += 1.0
        if len(headings.get('h3', [])) >= 2:
            score += 0.5

        # Mobile optimization (2 points)
        mobile_friendly = seo_data.get('mobile_friendly', {})
        if mobile_friendly.get('mobile_friendly'):
            score += 2.0
        elif website_data.get('mobile_optimized', {}).get('has_viewport_meta'):
            score += 1.0

        # Accessibility (2 points)
        accessibility = website_data.get('accessibility_features', {})
        if accessibility.get('has_lang_attribute'):
            score += 0.5
        if accessibility.get('images_with_alt', 0) > accessibility.get('images_without_alt', 0):
            score += 1.0
        if accessibility.get('has_aria_labels'):
            score += 0.5

        return min(score, max_score)

    def _calculate_responsiveness(self, website_data: Dict, seo_data: Dict) -> float:
        """Calculate responsiveness indicators"""
        score = 5.0  # Default score
        max_score = 10.0

        # Page load time (5 points)
        response_time = website_data.get('response_time', 5.0)
        if response_time < 1.0:
            score += 2.5
        elif response_time < 2.0:
            score += 2.0
        elif response_time < 3.0:
            score += 1.0
        elif response_time > 5.0:
            score -= 2.0

        # Mobile responsiveness (3 points)
        mobile_features = website_data.get('mobile_optimized', {})
        if mobile_features.get('has_viewport_meta'):
            score += 1.5
        if mobile_features.get('has_responsive_images'):
            score += 1.5

        # Modern technologies (2 points)
        technologies = website_data.get('technologies', [])
        modern_tech = ['React', 'Vue', 'Angular', 'Bootstrap']
        if any(tech in technologies for tech in modern_tech):
            score += 2.0

        return min(score, max_score)

    def _calculate_innovation(self, website_data: Dict, seo_data: Dict) -> float:
        """Calculate innovation indicators"""
        score = 5.0  # Default score
        max_score = 10.0

        # Modern technologies (3 points)
        technologies = website_data.get('technologies', [])
        modern_frameworks = ['React', 'Vue', 'Angular', 'Next.js', 'Gatsby']
        if any(framework in technologies for framework in modern_frameworks):
            score += 2.0

        # Advanced SEO features (3 points)
        structured_data = website_data.get('structured_data', [])
        if structured_data:
            score += 1.5

        social_tags = website_data.get('social_tags', {})
        if social_tags.get('open_graph') or social_tags.get('twitter'):
            score += 1.5

        # Progressive features (2 points)
        if 'Service Worker' in str(website_data).lower():
            score += 1.0
        if website_data.get('has_ssl'):
            score += 1.0

        # Analytics and tracking (2 points)
        if 'Google Analytics' in technologies:
            score += 1.0
        if 'Google Tag Manager' in technologies:
            score += 1.0

        return min(score, max_score)

    def _calculate_web_presence(self, website_data: Dict, social_data: Dict, seo_data: Dict) -> float:
        """Calculate web presence score"""
        score = 0.0
        max_score = 10.0

        # Social media presence (4 points)
        social_links = website_data.get('social_links', {})
        score += min(len(social_links) * 0.8, 4.0)

        # SEO optimization (3 points)
        seo_score = seo_data.get('page_speed', {}).get('seo_score', 0)
        if seo_score > 0:
            score += (seo_score / 100) * 3.0

        # Content richness (2 points)
        word_count = website_data.get('word_count', 0)
        if word_count > 1000:
            score += 2.0
        elif word_count > 500:
            score += 1.0

        # External linking and references (1 point)
        external_links = website_data.get('links', {}).get('external_links', 0)
        if external_links > 5:
            score += 1.0
        elif external_links > 2:
            score += 0.5

        return min(score, max_score)

    def _get_factor_explanations(self, scores: Dict) -> Dict:
        """Provide explanations for each trust factor"""
        explanations = {
            'legitimacy': self._explain_legitimacy_score(scores['legitimacy']),
            'transparency': self._explain_transparency_score(scores['transparency']),
            'customer_feedback': self._explain_feedback_score(scores['customer_feedback']),
            'service_quality': self._explain_quality_score(scores['service_quality']),
            'responsiveness': self._explain_responsiveness_score(scores['responsiveness']),
            'innovation': self._explain_innovation_score(scores['innovation']),
            'web_presence': self._explain_presence_score(scores['web_presence'])
        }
        return explanations

    def _explain_legitimacy_score(self, score: float) -> str:
        """Explain legitimacy score"""
        if score >= 8:
            return "Excellent - Strong indicators of business legitimacy"
        elif score >= 6:
            return "Good - Most legitimacy indicators present"
        elif score >= 4:
            return "Fair - Some legitimacy concerns"
        else:
            return "Poor - Multiple legitimacy issues detected"

    def _explain_transparency_score(self, score: float) -> str:
        """Explain transparency score"""
        if score >= 8:
            return "Excellent - Highly transparent with comprehensive contact info"
        elif score >= 6:
            return "Good - Adequate transparency and contact information"
        elif score >= 4:
            return "Fair - Limited transparency, could improve contact info"
        else:
            return "Poor - Lacks transparency and contact information"

    def _explain_feedback_score(self, score: float) -> str:
        """Explain customer feedback score"""
        if score >= 8:
            return "Excellent - Outstanding customer reviews and feedback"
        elif score >= 6:
            return "Good - Positive customer feedback overall"
        elif score >= 4:
            return "Fair - Mixed customer feedback"
        else:
            return "Poor - Negative or lacking customer feedback"

    def _explain_quality_score(self, score: float) -> str:
        """Explain service quality score"""
        if score >= 8:
            return "Excellent - High-quality website and user experience"
        elif score >= 6:
            return "Good - Quality website with minor improvement areas"
        elif score >= 4:
            return "Fair - Average quality with several improvement opportunities"
        else:
            return "Poor - Multiple quality and user experience issues"

    def _explain_responsiveness_score(self, score: float) -> str:
        """Explain responsiveness score"""
        if score >= 8:
            return "Excellent - Fast loading and highly responsive"
        elif score >= 6:
            return "Good - Acceptable performance and responsiveness"
        elif score >= 4:
            return "Fair - Moderate performance issues"
        else:
            return "Poor - Slow loading and responsiveness problems"

    def _explain_innovation_score(self, score: float) -> str:
        """Explain innovation score"""
        if score >= 8:
            return "Excellent - Uses modern technologies and innovative features"
        elif score >= 6:
            return "Good - Some modern features and technologies"
        elif score >= 4:
            return "Fair - Standard technology stack"
        else:
            return "Poor - Outdated technologies and limited innovation"

    def _explain_presence_score(self, score: float) -> str:
        """Explain web presence score"""
        if score >= 8:
            return "Excellent - Strong online presence across multiple channels"
        elif score >= 6:
            return "Good - Solid web presence with room for growth"
        elif score >= 4:
            return "Fair - Limited web presence"
        else:
            return "Poor - Weak online presence and visibility"

    def _generate_trust_recommendations(self, scores: Dict, data: Dict) -> list[str]:
        """Generate recommendations to improve trust score"""
        recommendations = []

        # Legitimacy recommendations
        if scores['legitimacy'] < 7:
            website_data = data.get('website_data', {})
            if not website_data.get('has_ssl'):
                recommendations.append("Install SSL certificate for HTTPS encryption")

            contact_info = website_data.get('contact_info', {})
            if not contact_info.get('has_email'):
                recommendations.append("Add clear contact email address")
            if not contact_info.get('has_phone'):
                recommendations.append("Provide phone number for customer contact")

        # Transparency recommendations
        if scores['transparency'] < 7:
            recommendations.append("Add comprehensive About Us page")
            recommendations.append("Include team member information and photos")
            recommendations.append("Provide detailed company address and location")

        # Service quality recommendations
        if scores['service_quality'] < 7:
            seo_data = data.get('seo_data', {})
            page_speed = seo_data.get('page_speed', {})
            if page_speed.get('performance_score', 0) < 70:
                recommendations.append("Improve website loading speed and performance")

            mobile_friendly = seo_data.get('mobile_friendly', {})
            if not mobile_friendly.get('mobile_friendly'):
                recommendations.append("Optimize website for mobile devices")

        # Innovation recommendations
        if scores['innovation'] < 6:
            recommendations.append("Implement structured data markup for better SEO")
            recommendations.append("Add social media meta tags (Open Graph, Twitter Cards)")
            recommendations.append("Consider upgrading to modern web technologies")

        # Web presence recommendations
        if scores['web_presence'] < 7:
            website_data = data.get('website_data', {})
            social_links = website_data.get('social_links', {})
            if len(social_links) < 3:
                recommendations.append("Establish presence on major social media platforms")
            recommendations.append("Create more comprehensive, valuable content")

        return recommendations[:8]  # Return top 8 recommendations