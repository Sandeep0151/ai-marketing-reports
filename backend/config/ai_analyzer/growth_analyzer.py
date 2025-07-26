# ai_analyzer/growth_analyzer.py
import openai
from django.conf import settings
import json
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class GrowthAnalyzer:
    """
    AI-powered growth recommendations generator

    Analyzes website data to generate actionable growth recommendations
    across multiple areas: technical, content, SEO, social media, and user experience.
    """

    def __init__(self):
        """Initialize the growth analyzer with OpenAI client"""
        self.client = None
        self.openai_available = False

        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                self.openai_available = True
                logger.info("OpenAI client initialized for growth analysis")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_available = False
        else:
            logger.warning("OpenAI API key not provided, using rule-based recommendations")

        # Configuration for recommendation categories
        self.recommendation_categories = [
            'technical',
            'content',
            'seo',
            'social_media',
            'user_experience',
            'conversion'
        ]

        # Priority levels
        self.priority_levels = ['high', 'medium', 'low']

    def generate_recommendations(self, data: Dict) -> List[Dict]:
        """
        Generate comprehensive growth recommendations

        Args:
            data: Dictionary containing all analysis data including:
                - website_data: Basic website information
                - seo_data: SEO performance metrics
                - social_data: Social media presence data
                - reputation_data: Online reputation metrics
                - competitor_data: Competitive analysis
                - trust_score: AI-calculated trust score

        Returns:
            List of recommendation dictionaries with priority, impact, and timeline
        """
        try:
            logger.info("Starting growth recommendations generation")

            # Extract data components
            website_data = data.get('website_data', {})
            seo_data = data.get('seo_data', {})
            social_data = data.get('social_data', {})
            reputation_data = data.get('reputation_data', {})
            competitor_data = data.get('competitor_data', {})
            trust_score = data.get('trust_score', {})

            # Generate recommendations by category
            all_recommendations = []

            # Technical recommendations
            technical_recs = self._generate_technical_recommendations(website_data, seo_data)
            all_recommendations.extend(technical_recs)

            # Content recommendations
            content_recs = self._generate_content_recommendations(website_data, seo_data, competitor_data)
            all_recommendations.extend(content_recs)

            # SEO recommendations
            seo_recs = self._generate_seo_recommendations(website_data, seo_data, competitor_data)
            all_recommendations.extend(seo_recs)

            # Social media recommendations
            social_recs = self._generate_social_recommendations(social_data, website_data)
            all_recommendations.extend(social_recs)

            # User experience recommendations
            ux_recs = self._generate_ux_recommendations(website_data, seo_data)
            all_recommendations.extend(ux_recs)

            # Reputation recommendations
            reputation_recs = self._generate_reputation_recommendations(reputation_data, trust_score)
            all_recommendations.extend(reputation_recs)

            # Use AI to enhance recommendations if available
            if self.openai_available:
                enhanced_recommendations = self._enhance_with_ai(all_recommendations, data)
                if enhanced_recommendations:
                    all_recommendations = enhanced_recommendations

            # Prioritize and rank recommendations
            prioritized_recommendations = self._prioritize_recommendations(all_recommendations)

            logger.info(f"Generated {len(prioritized_recommendations)} growth recommendations")
            return prioritized_recommendations[:12]  # Return top 12 recommendations

        except Exception as e:
            logger.error(f"Error generating growth recommendations: {e}")
            return self._get_fallback_recommendations()

    def _generate_technical_recommendations(self, website_data: Dict, seo_data: Dict) -> List[Dict]:
        """Generate technical improvement recommendations"""
        recommendations = []

        # SSL Certificate
        if not website_data.get('has_ssl'):
            recommendations.append({
                'category': 'technical',
                'title': 'Install SSL Certificate',
                'description': 'Secure your website with HTTPS encryption to protect user data and improve search rankings.',
                'priority': 'high',
                'estimated_impact': 'High - Improves SEO rankings and user trust',
                'effort_required': 'Low - Technical setup, 1-2 hours',
                'timeline': '1-2 days',
                'cost_estimate': 'Free - $100/year',
                'implementation_steps': [
                    'Purchase SSL certificate from hosting provider',
                    'Install and configure SSL certificate',
                    'Update internal links to HTTPS',
                    'Set up 301 redirects from HTTP to HTTPS'
                ]
            })

        # Page Speed Optimization
        page_speed = seo_data.get('page_speed', {})
        performance_score = page_speed.get('performance_score', 0)
        if performance_score < 70:
            recommendations.append({
                'category': 'technical',
                'title': 'Optimize Page Loading Speed',
                'description': f'Current performance score is {performance_score}/100. Improve website speed for better user experience and SEO.',
                'priority': 'high' if performance_score < 50 else 'medium',
                'estimated_impact': 'High - Better user experience, reduced bounce rate, improved SEO',
                'effort_required': 'Medium - Development work required',
                'timeline': '1-2 weeks',
                'cost_estimate': '$500 - $2,000',
                'implementation_steps': [
                    'Optimize and compress images',
                    'Minify CSS, JavaScript, and HTML',
                    'Enable browser caching',
                    'Use Content Delivery Network (CDN)',
                    'Optimize server response time'
                ]
            })

        # Mobile Optimization
        mobile_friendly = seo_data.get('mobile_friendly', {})
        if not mobile_friendly.get('mobile_friendly'):
            recommendations.append({
                'category': 'technical',
                'title': 'Implement Mobile-Responsive Design',
                'description': 'Ensure your website works perfectly on all mobile devices and screen sizes.',
                'priority': 'high',
                'estimated_impact': 'Very High - 60%+ of traffic is mobile',
                'effort_required': 'High - Design and development work',
                'timeline': '2-4 weeks',
                'cost_estimate': '$2,000 - $10,000',
                'implementation_steps': [
                    'Audit current mobile experience',
                    'Design responsive layouts',
                    'Implement responsive CSS framework',
                    'Test across multiple devices',
                    'Optimize mobile page speed'
                ]
            })

        # Robots.txt and Sitemap
        if not seo_data.get('robots_txt'):
            recommendations.append({
                'category': 'technical',
                'title': 'Create Robots.txt File',
                'description': 'Add robots.txt to guide search engine crawlers and improve SEO.',
                'priority': 'low',
                'estimated_impact': 'Medium - Better search engine crawling',
                'effort_required': 'Low - Simple file creation',
                'timeline': '1 day',
                'cost_estimate': 'Free',
                'implementation_steps': [
                    'Create robots.txt file',
                    'Add crawling directives',
                    'Include sitemap reference',
                    'Upload to website root directory'
                ]
            })

        return recommendations

    def _generate_content_recommendations(self, website_data: Dict, seo_data: Dict, competitor_data: Dict) -> List[
        Dict]:
        """Generate content strategy recommendations"""
        recommendations = []

        # Content Volume
        word_count = website_data.get('word_count', 0)
        if word_count < 500:
            recommendations.append({
                'category': 'content',
                'title': 'Expand Content Volume',
                'description': f'Current content is {word_count} words. Add more valuable, informative content to improve SEO and user engagement.',
                'priority': 'high' if word_count < 200 else 'medium',
                'estimated_impact': 'High - Better search rankings and user engagement',
                'effort_required': 'Medium - Content creation required',
                'timeline': '2-4 weeks',
                'cost_estimate': '$1,000 - $5,000',
                'implementation_steps': [
                    'Conduct keyword research',
                    'Create content calendar',
                    'Write comprehensive page content',
                    'Add blog or resources section',
                    'Optimize content for target keywords'
                ]
            })

        # Image Alt Text
        images = website_data.get('images', {})
        images_without_alt = images.get('without_alt_text', 0)
        if images_without_alt > 0:
            recommendations.append({
                'category': 'content',
                'title': f'Add Alt Text to {images_without_alt} Images',
                'description': 'Improve accessibility and SEO by adding descriptive alt text to all images.',
                'priority': 'medium',
                'estimated_impact': 'Medium - Improved accessibility and SEO',
                'effort_required': 'Low - Content editing',
                'timeline': '1-2 days',
                'cost_estimate': '$200 - $500',
                'implementation_steps': [
                    'Audit all images on website',
                    'Write descriptive alt text for each image',
                    'Update image tags with alt attributes',
                    'Implement alt text best practices for future images'
                ]
            })

        # Blog/Content Marketing
        headings = website_data.get('heading_structure', {})
        if len(headings.get('h2', [])) < 3:
            recommendations.append({
                'category': 'content',
                'title': 'Develop Content Marketing Strategy',
                'description': 'Create a blog or resources section to attract organic traffic and establish expertise.',
                'priority': 'medium',
                'estimated_impact': 'High - Long-term organic traffic growth',
                'effort_required': 'High - Ongoing content creation',
                'timeline': '4-8 weeks to establish',
                'cost_estimate': '$2,000 - $10,000',
                'implementation_steps': [
                    'Research target audience and topics',
                    'Create editorial calendar',
                    'Set up blog/resources section',
                    'Write initial content pieces',
                    'Promote content on social media'
                ]
            })

        # Video Content
        if 'video' not in str(website_data).lower():
            recommendations.append({
                'category': 'content',
                'title': 'Add Video Content',
                'description': 'Incorporate video content to improve engagement and time on site.',
                'priority': 'low',
                'estimated_impact': 'Medium - Higher engagement and conversions',
                'effort_required': 'Medium - Video production',
                'timeline': '2-3 weeks',
                'cost_estimate': '$1,000 - $5,000',
                'implementation_steps': [
                    'Plan video content strategy',
                    'Create product demos or explainer videos',
                    'Set up video hosting and embedding',
                    'Optimize videos for SEO',
                    'Add video transcripts for accessibility'
                ]
            })

        return recommendations

    def _generate_seo_recommendations(self, website_data: Dict, seo_data: Dict, competitor_data: Dict) -> List[Dict]:
        """Generate SEO improvement recommendations"""
        recommendations = []

        # Meta Description
        if not website_data.get('description'):
            recommendations.append({
                'category': 'seo',
                'title': 'Add Meta Description',
                'description': 'Write compelling meta descriptions to improve click-through rates from search results.',
                'priority': 'medium',
                'estimated_impact': 'Medium - Higher CTR from search results',
                'effort_required': 'Low - Content writing',
                'timeline': '1-2 days',
                'cost_estimate': '$100 - $500',
                'implementation_steps': [
                    'Research target keywords for each page',
                    'Write unique meta descriptions (150-160 characters)',
                    'Include primary keywords naturally',
                    'Add compelling calls-to-action',
                    'Test and optimize based on performance'
                ]
            })

        # Title Tag Optimization
        title = website_data.get('title', '')
        if not title or len(title) < 30 or len(title) > 60:
            recommendations.append({
                'category': 'seo',
                'title': 'Optimize Title Tags',
                'description': 'Improve title tags for better search engine rankings and click-through rates.',
                'priority': 'high',
                'estimated_impact': 'High - Direct impact on search rankings',
                'effort_required': 'Low - Content optimization',
                'timeline': '1-2 days',
                'cost_estimate': '$200 - $500',
                'implementation_steps': [
                    'Research primary keywords for each page',
                    'Write compelling titles (50-60 characters)',
                    'Include target keywords at the beginning',
                    'Make titles unique for each page',
                    'A/B test title variations'
                ]
            })

        # Structured Data
        if not website_data.get('structured_data'):
            recommendations.append({
                'category': 'seo',
                'title': 'Implement Structured Data Markup',
                'description': 'Add schema markup to help search engines understand your content better and enhance search results.',
                'priority': 'medium',
                'estimated_impact': 'Medium - Enhanced search result appearance',
                'effort_required': 'Medium - Technical implementation',
                'timeline': '1 week',
                'cost_estimate': '$500 - $1,500',
                'implementation_steps': [
                    'Identify relevant schema types for your business',
                    'Implement JSON-LD structured data',
                    'Add organization and local business markup',
                    'Include product/service markup if applicable',
                    'Test with Google\'s Rich Results Tool'
                ]
            })

        # Local SEO (if applicable)
        contact_info = website_data.get('contact_info', {})
        if contact_info.get('has_address'):
            recommendations.append({
                'category': 'seo',
                'title': 'Optimize for Local SEO',
                'description': 'Improve local search visibility with Google My Business and local citations.',
                'priority': 'high',
                'estimated_impact': 'High - Local customer acquisition',
                'effort_required': 'Medium - Local optimization work',
                'timeline': '2-3 weeks',
                'cost_estimate': '$500 - $2,000',
                'implementation_steps': [
                    'Claim and optimize Google My Business listing',
                    'Ensure NAP consistency across directories',
                    'Build local citations and directories',
                    'Collect and manage customer reviews',
                    'Create location-specific content'
                ]
            })

        return recommendations

    def _generate_social_recommendations(self, social_data: Dict, website_data: Dict) -> List[Dict]:
        """Generate social media recommendations"""
        recommendations = []

        if not social_data or 'error' in social_data:
            recommendations.append({
                'category': 'social_media',
                'title': 'Establish Social Media Presence',
                'description': 'Create business profiles on major social media platforms to increase brand awareness.',
                'priority': 'medium',
                'estimated_impact': 'Medium - Brand awareness and traffic',
                'effort_required': 'Medium - Ongoing content management',
                'timeline': '2-3 weeks to establish',
                'cost_estimate': '$1,000 - $3,000',
                'implementation_steps': [
                    'Create business profiles on Facebook, Instagram, LinkedIn',
                    'Optimize profiles with complete business information',
                    'Develop content strategy and posting schedule',
                    'Create initial content and start posting regularly',
                    'Engage with followers and build community'
                ]
            })
            return recommendations

        # Check platform presence
        platform_data = social_data.get('platform_data', {})
        missing_platforms = []

        for platform in ['facebook', 'instagram', 'linkedin']:
            data = platform_data.get(platform, {})
            if not (data.get('account_found') or data.get('page_found') or data.get('channel_found')):
                missing_platforms.append(platform.title())

        if missing_platforms:
            recommendations.append({
                'category': 'social_media',
                'title': f'Expand to {", ".join(missing_platforms[:2])}',
                'description': f'Create business presence on {", ".join(missing_platforms[:2])} to reach wider audiences.',
                'priority': 'medium',
                'estimated_impact': 'Medium - Increased brand awareness and reach',
                'effort_required': 'Medium - Profile setup and content creation',
                'timeline': '2-4 weeks',
                'cost_estimate': '$500 - $2,000',
                'implementation_steps': [
                    f'Create optimized business profiles on {", ".join(missing_platforms[:2])}',
                    'Develop platform-specific content strategy',
                    'Create initial content and posting schedule',
                    'Cross-promote existing social accounts',
                    'Monitor engagement and adjust strategy'
                ]
            })

        # Engagement improvement
        summary = social_data.get('summary', {})
        if summary.get('social_presence_score', 0) < 50:
            recommendations.append({
                'category': 'social_media',
                'title': 'Improve Social Media Engagement',
                'description': 'Enhance content quality and posting consistency to boost follower engagement.',
                'priority': 'medium',
                'estimated_impact': 'Medium - Higher engagement and reach',
                'effort_required': 'Medium - Content strategy development',
                'timeline': '4-6 weeks',
                'cost_estimate': '$1,000 - $5,000',
                'implementation_steps': [
                    'Analyze current content performance',
                    'Develop engaging content themes and formats',
                    'Create consistent posting schedule',
                    'Use interactive content (polls, Q&A, live videos)',
                    'Respond promptly to comments and messages'
                ]
            })

        return recommendations

    def _generate_ux_recommendations(self, website_data: Dict, seo_data: Dict) -> List[Dict]:
        """Generate user experience recommendations"""
        recommendations = []

        # Navigation and Internal Linking
        links = website_data.get('links', {})
        internal_links = links.get('internal_links', 0)
        if internal_links < 5:
            recommendations.append({
                'category': 'user_experience',
                'title': 'Improve Site Navigation and Internal Linking',
                'description': 'Add more internal links and improve navigation to help users find content easily.',
                'priority': 'medium',
                'estimated_impact': 'Medium - Better user experience and SEO',
                'effort_required': 'Medium - Design and content work',
                'timeline': '1-2 weeks',
                'cost_estimate': '$500 - $2,000',
                'implementation_steps': [
                    'Audit current site structure and navigation',
                    'Design intuitive navigation menu',
                    'Add relevant internal links within content',
                    'Create breadcrumb navigation',
                    'Add related content suggestions'
                ]
            })

        # Contact Information Accessibility
        contact_info = website_data.get('contact_info', {})
        if not contact_info.get('has_phone') or not contact_info.get('has_email'):
            recommendations.append({
                'category': 'user_experience',
                'title': 'Improve Contact Information Accessibility',
                'description': 'Make it easier for customers to reach you by prominently displaying contact information.',
                'priority': 'high',
                'estimated_impact': 'High - Better customer communication and trust',
                'effort_required': 'Low - Content addition',
                'timeline': '1 day',
                'cost_estimate': '$100 - $300',
                'implementation_steps': [
                    'Add clear contact information to header/footer',
                    'Create dedicated contact page',
                    'Include multiple contact methods (phone, email, form)',
                    'Add business hours and location if applicable',
                    'Test contact forms for functionality'
                ]
            })

        # Loading Speed (User Experience aspect)
        response_time = website_data.get('response_time', 5.0)
        if response_time > 3.0:
            recommendations.append({
                'category': 'user_experience',
                'title': 'Optimize Website Loading Speed',
                'description': f'Current loading time is {response_time:.1f} seconds. Improve speed for better user experience.',
                'priority': 'high',
                'estimated_impact': 'High - Reduced bounce rate, better conversions',
                'effort_required': 'Medium - Technical optimization',
                'timeline': '1-2 weeks',
                'cost_estimate': '$500 - $2,000',
                'implementation_steps': [
                    'Optimize image sizes and formats',
                    'Minimize HTTP requests',
                    'Enable compression and caching',
                    'Optimize database queries',
                    'Use performance monitoring tools'
                ]
            })

        return recommendations

    def _generate_reputation_recommendations(self, reputation_data: Dict, trust_score: Dict) -> List[Dict]:
        """Generate reputation management recommendations"""
        recommendations = []

        if not reputation_data or 'error' in reputation_data:
            recommendations.append({
                'category': 'reputation',
                'title': 'Implement Online Reputation Management',
                'description': 'Establish presence on review platforms and actively manage your online reputation.',
                'priority': 'medium',
                'estimated_impact': 'High - Customer trust and credibility',
                'effort_required': 'Medium - Ongoing management',
                'timeline': '2-4 weeks to establish',
                'cost_estimate': '$500 - $2,000',
                'implementation_steps': [
                    'Create Google My Business listing',
                    'Set up monitoring for online mentions',
                    'Develop review generation strategy',
                    'Create response templates for reviews',
                    'Implement customer feedback system'
                ]
            })
            return recommendations

        # Review Generation
        summary = reputation_data.get('summary', {})
        total_reviews = summary.get('total_reviews', 0)
        if total_reviews < 10:
            recommendations.append({
                'category': 'reputation',
                'title': 'Implement Review Generation Strategy',
                'description': f'Currently have {total_reviews} reviews. Develop systematic approach to collect customer reviews.',
                'priority': 'high',
                'estimated_impact': 'High - Increased customer trust and conversions',
                'effort_required': 'Medium - Process development and implementation',
                'timeline': '3-4 weeks',
                'cost_estimate': '$1,000 - $3,000',
                'implementation_steps': [
                    'Create customer review request process',
                    'Send follow-up emails after purchases/services',
                    'Add review request prompts on website',
                    'Train staff to request reviews in person',
                    'Monitor and respond to all reviews promptly'
                ]
            })

        # Rating Improvement
        overall_rating = summary.get('overall_rating', 0)
        if overall_rating < 4.0:
            recommendations.append({
                'category': 'reputation',
                'title': 'Improve Customer Satisfaction and Ratings',
                'description': f'Current average rating is {overall_rating}/5. Focus on service improvements to increase ratings.',
                'priority': 'high',
                'estimated_impact': 'Very High - Better reputation drives more customers',
                'effort_required': 'High - Operational improvements required',
                'timeline': '2-3 months',
                'cost_estimate': '$2,000 - $10,000',
                'implementation_steps': [
                    'Analyze negative feedback for common issues',
                    'Implement customer service improvements',
                    'Train staff on customer satisfaction best practices',
                    'Create customer feedback loop and resolution process',
                    'Monitor ratings improvement over time'
                ]
            })

        return recommendations

    def _enhance_with_ai(self, recommendations: List[Dict], data: Dict) -> List[Dict]:
        """Use AI to enhance and personalize recommendations"""
        try:
            # Prepare context for AI
            website_data = data.get('website_data', {})
            trust_score = data.get('trust_score', {})

            company_name = website_data.get('company_name', 'this business')
            domain = website_data.get('domain', 'the website')
            overall_trust = trust_score.get('overall', 5.0)

            # Create prompt for AI enhancement
            prompt = f"""
            As a digital marketing expert, review and enhance these growth recommendations for {company_name} (domain: {domain}).
            Current trust score: {overall_trust}/10

            Existing recommendations:
            {json.dumps([{
                'title': rec['title'],
                'category': rec['category'],
                'priority': rec['priority']
            } for rec in recommendations[:8]], indent=2)}

            Please:
            1. Suggest 2-3 additional high-impact recommendations not in the list
            2. Ensure recommendations are specific to this business
            3. Focus on quick wins and high ROI activities
            4. Consider the current trust score level

            Format as JSON array with same structure: title, description, category, priority, estimated_impact, effort_required, timeline.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )

            ai_recommendations = json.loads(response.choices[0].message.content)

            # Add AI recommendations to existing ones
            for ai_rec in ai_recommendations:
                ai_rec['ai_enhanced'] = True
                recommendations.append(ai_rec)

            logger.info("Successfully enhanced recommendations with AI")
            return recommendations

        except Exception as e:
            logger.error(f"Error enhancing recommendations with AI: {e}")
            return recommendations  # Return original recommendations if AI fails

    def _prioritize_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Prioritize and rank recommendations by impact and urgency"""

        # Define priority weights
        priority_weights = {'high': 3, 'medium': 2, 'low': 1}

        # Define category importance weights
        category_weights = {
            'technical': 1.0,
            'seo': 0.9,
            'user_experience': 0.8,
            'content': 0.7,
            'reputation': 0.6,
            'social_media': 0.5
        }

        # Calculate composite score for each recommendation
        for rec in recommendations:
            priority_score = priority_weights.get(rec.get('priority', 'low'), 1)
            category_score = category_weights.get(rec.get('category', 'other'), 0.5)

            # Add effort bonus (lower effort = higher score)
            effort = rec.get('effort_required', 'medium').lower()
            effort_bonus = 0.3 if 'low' in effort else 0.1 if 'medium' in effort else 0

            composite_score = (priority_score * category_score) + effort_bonus
            rec['composite_score'] = round(composite_score, 2)

        # Sort by composite score (highest first)
        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: x.get('composite_score', 0),
            reverse=True
        )

        return sorted_recommendations

    def _get_fallback_recommendations(self) -> List[Dict]:
        """Fallback recommendations when analysis fails"""
        return [
            {
                'category': 'technical',
                'title': 'Improve Website Security',
                'description': 'Ensure your website has SSL certificate and basic security measures.',
                'priority': 'high',
                'estimated_impact': 'High - User trust and SEO',
                'effort_required': 'Low',
                'timeline': '1-2 days',
                'cost_estimate': 'Free - $100'
            },
            {
                'category': 'seo',
                'title': 'Optimize Page Titles and Descriptions',
                'description': 'Review and improve title tags and meta descriptions for better search visibility.',
                'priority': 'high',
                'estimated_impact': 'High - Search rankings',
                'effort_required': 'Low',
                'timeline': '1 week',
                'cost_estimate': '$200 - $500'
            },
            {
                'category': 'content',
                'title': 'Create Quality Content',
                'description': 'Develop valuable content that addresses your audience\'s needs and questions.',
                'priority': 'medium',
                'estimated_impact': 'High - Long-term growth',
                'effort_required': 'Medium',
                'timeline': '2-4 weeks',
                'cost_estimate': '$1,000 - $5,000'
            }
        ]