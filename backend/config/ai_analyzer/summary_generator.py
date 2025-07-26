# ai_analyzer/summary_generator.py
import openai
from django.conf import settings
import json
import time
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """
    Advanced AI-powered executive summary generator for marketing reports

    This class generates comprehensive executive summaries using multiple approaches:
    1. AI-powered text generation with OpenAI
    2. Statistical analysis of website data
    3. Intelligent insight extraction
    4. Performance benchmarking
    """

    def __init__(self):
        """Initialize the summary generator with OpenAI client and configuration"""
        self.client = None
        self.openai_available = False

        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                self.openai_available = True
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_available = False
        else:
            logger.warning("OpenAI API key not provided, using fallback summary generation")

        # Configuration for summary generation
        self.config = {
            'max_summary_length': 250,
            'max_insights': 6,
            'max_highlights': 5,
            'max_improvements': 5,
            'openai_model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 300
        }

        # Industry benchmarks for comparison
        self.benchmarks = {
            'excellent_trust_score': 8.5,
            'good_trust_score': 7.0,
            'average_trust_score': 5.5,
            'min_word_count': 300,
            'good_word_count': 800,
            'excellent_word_count': 1500,
            'min_page_speed': 60,
            'good_page_speed': 80,
            'excellent_page_speed': 90,
            'min_social_platforms': 2,
            'good_social_platforms': 4,
            'excellent_social_platforms': 6
        }

    def generate_summary(self, data: Dict) -> Dict:
        """
        Generate a comprehensive executive summary from website analysis data

        Args:
            data: Dictionary containing all analysis data including:
                - website_data: Basic website information and technical analysis
                - seo_data: SEO performance metrics
                - social_data: Social media presence data
                - reputation_data: Online reputation metrics
                - competitor_data: Competitive analysis
                - trust_score: AI-calculated trust score
                - growth_opportunities: List of improvement recommendations

        Returns:
            Dictionary containing complete executive summary with metrics and insights
        """
        try:
            start_time = time.time()
            logger.info("Starting executive summary generation")

            # Extract and validate input data
            website_data = data.get('website_data', {})
            seo_data = data.get('seo_data', {})
            social_data = data.get('social_data', {})
            reputation_data = data.get('reputation_data', {})
            competitor_data = data.get('competitor_data', {})
            trust_score = data.get('trust_score', {})
            growth_opportunities = data.get('growth_opportunities', [])

            # Calculate key performance metrics
            key_metrics = self._calculate_comprehensive_metrics(data)

            # Generate AI-powered summary text
            summary_text = self._generate_intelligent_summary_text(data, key_metrics)

            # Extract actionable insights
            key_insights = self._extract_strategic_insights(data, key_metrics)

            # Identify performance highlights
            performance_highlights = self._identify_performance_highlights(data, key_metrics)

            # Determine improvement priorities
            improvement_areas = self._prioritize_improvement_areas(data, key_metrics)

            # Assess competitive positioning
            competitive_position = self._analyze_competitive_position(data, key_metrics)

            # Calculate overall performance score
            overall_performance = self._calculate_overall_performance_score(key_metrics)

            # Generate month-over-month comparison (simulated for now)
            month_over_month = self._generate_month_over_month_analysis(key_metrics)

            # Create comprehensive summary object
            summary = {
                # Key headline metrics
                'organic_traffic_change': key_metrics.get('traffic_change', '+0%'),
                'ai_visibility': trust_score.get('overall', 5.0),
                'avg_rating': key_metrics.get('avg_rating', 0.0),
                'overall_performance_score': overall_performance,

                # AI-generated content
                'summary_text': summary_text,
                'key_insights': key_insights,
                'performance_highlights': performance_highlights,
                'areas_for_improvement': improvement_areas,

                # Strategic analysis
                'competitive_position': competitive_position,
                'growth_potential': self._assess_growth_potential(data, key_metrics),
                'risk_factors': self._identify_risk_factors(data, key_metrics),
                'market_opportunities': self._identify_market_opportunities(data, key_metrics),

                # Detailed metrics
                'detailed_metrics': key_metrics,
                'month_over_month': month_over_month,
                'benchmarking': self._benchmark_against_industry(key_metrics),

                # Metadata
                'generated_at': time.time(),
                'generation_time_seconds': round(time.time() - start_time, 2),
                'ai_enhanced': self.openai_available,
                'data_sources_count': self._count_data_sources(data),
                'confidence_score': self._calculate_confidence_score(data)
            }

            logger.info(f"Executive summary generated successfully in {summary['generation_time_seconds']}s")
            return summary

        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return self._generate_emergency_fallback_summary(data)

    def _calculate_comprehensive_metrics(self, data: Dict) -> Dict:
        """
        Calculate comprehensive performance metrics from all data sources

        Returns:
            Dictionary with detailed performance metrics
        """
        website_data = data.get('website_data', {})
        seo_data = data.get('seo_data', {})
        social_data = data.get('social_data', {})
        reputation_data = data.get('reputation_data', {})
        trust_score = data.get('trust_score', {})

        # Technical performance metrics
        page_speed_data = seo_data.get('page_speed', {})
        mobile_data = seo_data.get('mobile_friendly', {})

        # Content metrics
        word_count = website_data.get('word_count', 0)
        images_data = website_data.get('images', {})
        links_data = website_data.get('links', {})

        # Social presence metrics
        social_links = website_data.get('social_links', {})
        social_platforms_count = len(social_links)

        # Trust and security metrics
        trust_overall = trust_score.get('overall', 5.0)
        has_ssl = website_data.get('has_ssl', False)

        metrics = {
            # Performance scores (0-100)
            'page_speed_score': page_speed_data.get('performance_score', 0),
            'seo_score': page_speed_data.get('seo_score', 0),
            'accessibility_score': page_speed_data.get('accessibility_score', 0),
            'best_practices_score': page_speed_data.get('best_practices_score', 0),

            # Mobile optimization
            'mobile_friendly': mobile_data.get('mobile_friendly', False),
            'mobile_score': 100 if mobile_data.get('mobile_friendly') else 0,

            # Content quality indicators
            'content_volume_score': self._calculate_content_volume_score(word_count),
            'content_structure_score': self._calculate_content_structure_score(website_data),
            'image_optimization_score': self._calculate_image_optimization_score(images_data),

            # SEO fundamentals
            'technical_seo_score': self._calculate_technical_seo_score(website_data, seo_data),
            'on_page_seo_score': self._calculate_on_page_seo_score(website_data),

            # Social presence
            'social_presence_score': self._calculate_social_presence_score(social_platforms_count),
            'social_platforms_count': social_platforms_count,

            # Trust and security
            'trust_score': trust_overall,
            'security_score': self._calculate_security_score(website_data),

            # User experience
            'user_experience_score': self._calculate_user_experience_score(website_data, seo_data),
            'loading_speed_score': self._convert_loading_time_to_score(website_data.get('response_time', 5.0)),

            # Raw metrics for reference
            'word_count': word_count,
            'response_time_seconds': website_data.get('response_time', 0),
            'internal_links_count': links_data.get('internal_links', 0),
            'external_links_count': links_data.get('external_links', 0),
            'images_with_alt': images_data.get('with_alt_text', 0),
            'images_without_alt': images_data.get('without_alt_text', 0),

            # Calculated compound metrics
            'overall_technical_health': 0,  # Will be calculated below
            'overall_content_quality': 0,  # Will be calculated below
            'overall_user_experience': 0,  # Will be calculated below

            # Placeholder for historical data (would come from database in production)
            'traffic_change': '+0%',  # Would need historical data
            'avg_rating': reputation_data.get('overall_rating', 0) if reputation_data else 0,
            'social_engagement_rate': 0,  # Would need social API data

            # Competitive metrics (placeholders)
            'market_position_percentile': min(trust_overall * 10, 100),
            'competitive_advantage_score': self._calculate_competitive_advantage(data)
        }

        # Calculate compound scores
        metrics['overall_technical_health'] = self._calculate_weighted_average([
            (metrics['page_speed_score'], 0.3),
            (metrics['mobile_score'], 0.25),
            (metrics['security_score'], 0.25),
            (metrics['technical_seo_score'], 0.2)
        ])

        metrics['overall_content_quality'] = self._calculate_weighted_average([
            (metrics['content_volume_score'], 0.3),
            (metrics['content_structure_score'], 0.3),
            (metrics['on_page_seo_score'], 0.25),
            (metrics['image_optimization_score'], 0.15)
        ])

        metrics['overall_user_experience'] = self._calculate_weighted_average([
            (metrics['loading_speed_score'], 0.3),
            (metrics['mobile_score'], 0.25),
            (metrics['accessibility_score'], 0.25),
            (metrics['user_experience_score'], 0.2)
        ])

        return metrics

    def _generate_intelligent_summary_text(self, data: Dict, metrics: Dict) -> str:
        """
        Generate intelligent summary text using AI or advanced templating
        """
        if self.openai_available:
            return self._generate_ai_powered_summary(data, metrics)
        else:
            return self._generate_template_based_summary(data, metrics)

    def _generate_ai_powered_summary(self, data: Dict, metrics: Dict) -> str:
        """
        Generate summary using OpenAI GPT with intelligent prompting
        """
        try:
            website_data = data.get('website_data', {})
            trust_score = data.get('trust_score', {})

            company_name = website_data.get('company_name') or website_data.get('domain', 'This website')
            domain = website_data.get('domain', 'the analyzed website')

            # Create detailed context for AI
            context = {
                'company': company_name,
                'domain': domain,
                'trust_score': trust_score.get('overall', 5.0),
                'page_speed': metrics.get('page_speed_score', 0),
                'mobile_friendly': metrics.get('mobile_friendly', False),
                'ssl_enabled': website_data.get('has_ssl', False),
                'social_platforms': metrics.get('social_platforms_count', 0),
                'content_quality': metrics.get('content_volume_score', 0),
                'technical_health': metrics.get('overall_technical_health', 0),
                'user_experience': metrics.get('overall_user_experience', 0),
                'word_count': metrics.get('word_count', 0),
                'seo_score': metrics.get('seo_score', 0)
            }

            # Create intelligent prompt
            prompt = f"""
            As a senior digital marketing analyst, write a professional executive summary for a comprehensive marketing report.

            COMPANY: {context['company']}
            DOMAIN: {context['domain']}

            KEY METRICS:
            • Trust Score: {context['trust_score']}/10
            • Page Speed: {context['page_speed']}/100
            • Mobile Friendly: {"Yes" if context['mobile_friendly'] else "No"}
            • SSL Security: {"Enabled" if context['ssl_enabled'] else "Disabled"}
            • Social Platforms: {context['social_platforms']} active
            • Content Volume: {context['word_count']} words
            • Technical Health: {context['technical_health']}/100
            • User Experience: {context['user_experience']}/100
            • SEO Score: {context['seo_score']}/100

            REQUIREMENTS:
            1. Write 2-3 sentences maximum (under 200 words)
            2. Lead with the company's strongest performance area
            3. Mention 1-2 specific metrics with numbers
            4. Include 1 key improvement opportunity
            5. Use confident, professional tone
            6. Make it actionable and specific
            7. Avoid generic marketing speak

            Focus on business impact and growth opportunities. Be specific about the data.
            """

            response = self.client.chat.completions.create(
                model=self.config['openai_model'],
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert digital marketing analyst known for creating clear, actionable executive summaries that drive business decisions."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature']
            )

            summary_text = response.choices[0].message.content.strip()

            # Validate and clean the response
            if len(summary_text) > self.config['max_summary_length']:
                # Truncate if too long
                sentences = summary_text.split('. ')
                summary_text = '. '.join(sentences[:2]) + '.'

            logger.info("AI-powered summary generated successfully")
            return summary_text

        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return self._generate_template_based_summary(data, metrics)

    def _generate_template_based_summary(self, data: Dict, metrics: Dict) -> str:
        """
        Generate summary using intelligent templates when AI is not available
        """
        website_data = data.get('website_data', {})
        trust_score = data.get('trust_score', {})

        company_name = website_data.get('company_name') or website_data.get('domain', 'This website')
        trust_score_val = trust_score.get('overall', 5.0)
        page_speed = metrics.get('page_speed_score', 0)
        social_count = metrics.get('social_platforms_count', 0)

        # Determine performance level
        if trust_score_val >= self.benchmarks['excellent_trust_score']:
            performance_level = "exceptional"
            performance_desc = "industry-leading"
        elif trust_score_val >= self.benchmarks['good_trust_score']:
            performance_level = "strong"
            performance_desc = "above-average"
        elif trust_score_val >= self.benchmarks['average_trust_score']:
            performance_level = "moderate"
            performance_desc = "competitive"
        else:
            performance_level = "developing"
            performance_desc = "emerging"

        # Identify top strength
        strengths = []
        if page_speed >= self.benchmarks['excellent_page_speed']:
            strengths.append("exceptional loading performance")
        elif website_data.get('has_ssl'):
            strengths.append("strong security foundation")
        elif social_count >= self.benchmarks['good_social_platforms']:
            strengths.append("comprehensive social media presence")
        elif metrics.get('content_volume_score', 0) >= 80:
            strengths.append("rich content volume")
        else:
            strengths.append("solid technical foundation")

        top_strength = strengths[0] if strengths else "established online presence"

        # Identify top improvement opportunity
        improvements = []
        if page_speed < self.benchmarks['min_page_speed']:
            improvements.append("page speed optimization")
        elif not website_data.get('has_ssl'):
            improvements.append("SSL security implementation")
        elif social_count < self.benchmarks['min_social_platforms']:
            improvements.append("social media expansion")
        elif metrics.get('word_count', 0) < self.benchmarks['min_word_count']:
            improvements.append("content development")
        else:
            improvements.append("mobile optimization")

        top_improvement = improvements[0] if improvements else "continued optimization"

        # Generate summary based on performance level
        summary_templates = {
            "exceptional": f"{company_name} demonstrates {performance_desc} digital performance with a trust score of {trust_score_val}/10, highlighted by {top_strength}. The website maintains strong technical fundamentals across {social_count} social platforms. Strategic focus on {top_improvement} will further enhance market leadership position.",

            "strong": f"{company_name} shows {performance_desc} digital presence with a {trust_score_val}/10 trust score, particularly excelling in {top_strength}. Current performance indicates solid market positioning with {social_count} active social channels. Implementing {top_improvement} represents the highest-impact improvement opportunity.",

            "moderate": f"{company_name} maintains a {performance_desc} digital foundation with a {trust_score_val}/10 trust score and demonstrates {top_strength}. With presence across {social_count} social platforms, the brand shows growth potential. Prioritizing {top_improvement} will drive significant performance improvements.",

            "developing": f"{company_name} is building its digital presence with a {trust_score_val}/10 trust score and shows promise in {top_strength}. Current {social_count}-platform social presence provides growth opportunities. Implementing {top_improvement} is critical for competitive positioning and user engagement."
        }

        return summary_templates.get(performance_level, summary_templates["moderate"])

    def _extract_strategic_insights(self, data: Dict, metrics: Dict) -> List[str]:
        """
        Extract strategic insights based on comprehensive data analysis
        """
        insights = []
        website_data = data.get('website_data', {})
        trust_score = data.get('trust_score', {})

        # Trust score insights with specific recommendations
        trust_val = trust_score.get('overall', 5.0)
        if trust_val >= 8.5:
            insights.append(
                f"Exceptional trust score of {trust_val}/10 positions the brand as highly credible, providing strong competitive advantage for customer acquisition")
        elif trust_val >= 7.0:
            insights.append(
                f"Strong trust score of {trust_val}/10 indicates solid customer confidence with opportunities to reach industry-leading levels")
        elif trust_val >= 5.5:
            insights.append(
                f"Moderate trust score of {trust_val}/10 suggests mixed signals to potential customers, requiring strategic reputation management")
        else:
            insights.append(
                f"Trust score of {trust_val}/10 indicates significant credibility challenges that may impact conversion rates and customer acquisition")

        # Technical performance insights
        page_speed = metrics.get('page_speed_score', 0)
        if page_speed >= 90:
            insights.append(
                f"Outstanding page speed performance ({page_speed}/100) enhances user experience and supports strong SEO rankings")
        elif page_speed >= 70:
            insights.append(
                f"Good page speed ({page_speed}/100) provides competitive advantage, with optimization potential for mobile performance")
        elif page_speed < 50:
            insights.append(
                f"Page speed score ({page_speed}/100) significantly below industry standards, likely impacting user engagement and search rankings")

        # Mobile optimization insights
        if metrics.get('mobile_friendly'):
            insights.append(
                "Mobile-responsive design aligns with mobile-first indexing requirements and growing mobile traffic trends")
        else:
            insights.append(
                "Missing mobile optimization represents critical risk given 60%+ mobile traffic share across most industries")

        # Content strategy insights
        word_count = metrics.get('word_count', 0)
        content_score = metrics.get('content_volume_score', 0)
        if content_score >= 80:
            insights.append(
                f"Rich content volume ({word_count} words) supports comprehensive SEO strategy and user education")
        elif word_count < 300:
            insights.append(
                f"Limited content volume ({word_count} words) constrains SEO potential and user engagement opportunities")

        # Security insights
        if website_data.get('has_ssl'):
            insights.append(
                "SSL security implementation meets modern standards and supports user trust and search engine requirements")
        else:
            insights.append(
                "Missing SSL certificate creates security warnings that directly impact user trust and search engine rankings")

        # Social presence strategic insights
        social_count = metrics.get('social_platforms_count', 0)
        if social_count >= 4:
            insights.append(
                f"Strong social media presence across {social_count} platforms creates multiple customer touchpoints for brand building")
        elif social_count <= 1:
            insights.append(
                f"Limited social presence ({social_count} platforms) misses significant opportunities for audience engagement and brand awareness")

        # Return top insights based on priority
        return insights[:self.config['max_insights']]

    def _identify_performance_highlights(self, data: Dict, metrics: Dict) -> List[str]:
        """
        Identify and highlight top-performing areas
        """
        highlights = []

        # Check each performance area against benchmarks
        performance_areas = [
            ('page_speed_score', 'Page Performance', 'excellent_page_speed', '/100'),
            ('trust_score', 'Trust Score', 'excellent_trust_score', '/10'),
            ('mobile_score', 'Mobile Optimization', 'good_page_speed', '%'),
            ('security_score', 'Security Implementation', 'good_page_speed', '/100'),
            ('social_presence_score', 'Social Media Presence', 'good_page_speed', '/100'),
            ('content_volume_score', 'Content Quality', 'good_page_speed', '/100'),
            ('technical_seo_score', 'Technical SEO', 'good_page_speed', '/100'),
            ('accessibility_score', 'Accessibility', 'good_page_speed', '/100')
        ]

        for metric_key, display_name, benchmark_key, unit in performance_areas:
            score = metrics.get(metric_key, 0)
            benchmark = self.benchmarks.get(benchmark_key, 80)

            if score >= benchmark:
                highlights.append(f"Excellent {display_name} ({score}{unit})")
            elif score >= benchmark * 0.8:  # Good performance (80% of excellent)
                highlights.append(f"Strong {display_name} ({score}{unit})")

        # Special highlights for specific achievements
        website_data = data.get('website_data', {})

        if website_data.get('structured_data'):
            highlights.append(
                f"Advanced SEO with {len(website_data['structured_data'])} structured data implementations")

        if metrics.get('internal_links_count', 0) > 10:
            highlights.append(f"Well-structured internal linking ({metrics['internal_links_count']} internal links)")

        if metrics.get('images_with_alt', 0) > metrics.get('images_without_alt', 0):
            highlights.append("Good accessibility with comprehensive image alt text implementation")

        return highlights[:self.config['max_highlights']]

    def _prioritize_improvement_areas(self, data: Dict, metrics: Dict) -> List[str]:
        """
        Prioritize improvement areas based on impact and effort analysis
        """
        improvements = []
        website_data = data.get('website_data', {})

        # High-impact, low-effort improvements (Priority 1)
        if not website_data.get('has_ssl'):
            improvements.append("🔒 Implement SSL certificate (High Impact, Low Effort) - Critical for security and SEO")

        if metrics.get('page_speed_score', 0) < 60:
            improvements.append(
                "⚡ Optimize page loading speed (High Impact, Medium Effort) - Improve user experience and rankings")

        if not metrics.get('mobile_friendly'):
            improvements.append(
                "📱 Implement mobile-responsive design (High Impact, High Effort) - Essential for 60%+ mobile users")

        # Medium-impact improvements (Priority 2)
        if metrics.get('word_count', 0) < 500:
            improvements.append("📝 Expand content volume (Medium Impact, Medium Effort) - Enhance SEO and user value")

        if metrics.get('images_without_alt', 0) > 0:
            improvements.append(
                f"🖼️ Add alt text to {metrics['images_without_alt']} images (Medium Impact, Low Effort) - Improve accessibility and SEO")

        if metrics.get('social_platforms_count', 0) < 3:
            improvements.append(
                "📲 Expand social media presence (Medium Impact, Medium Effort) - Increase brand awareness")

        # Technical improvements (Priority 3)
        if not website_data.get('structured_data'):
            improvements.append(
                "🏷️ Implement structured data markup (Medium Impact, Medium Effort) - Enhance search appearance")

        if metrics.get('internal_links_count', 0) < 5:
            improvements.append(
                "🔗 Improve internal linking structure (Low Impact, Low Effort) - Better site navigation and SEO")

        # Advanced improvements (Priority 4)
        if metrics.get('accessibility_score', 0) < 80:
            improvements.append(
                "♿ Enhance accessibility features (Medium Impact, Medium Effort) - Expand audience reach")

        return improvements[:self.config['max_improvements']]

    def _analyze_competitive_position(self, data: Dict, metrics: Dict) -> Dict:
        """
        Analyze competitive positioning with strategic recommendations
        """
        trust_score = data.get('trust_score', {})
        overall_score = trust_score.get('overall', 5.0)

        # Calculate percentile based on trust score
        percentile = min(overall_score * 10, 100)

        # Determine competitive position
        if overall_score >= 8.5:
            position = "market_leader"
            description = "Industry-leading digital presence with comprehensive competitive advantages"
            strategy = "Maintain leadership through continuous innovation and emerging technology adoption"
            market_share_potential = "High - Well-positioned for market expansion"
        elif overall_score >= 7.0:
            position = "strong_competitor"
            description = "Strong competitive position with opportunities for market leadership"
            strategy = "Focus on differentiating strengths while addressing key gaps to achieve market leadership"
            market_share_potential = "Good - Ready for aggressive growth strategies"
        elif overall_score >= 5.5:
            position = "average_performer"
            description = "Competitive parity with industry average, requiring strategic improvements"
            strategy = "Implement comprehensive digital strategy focusing on high-impact improvements"
            market_share_potential = "Moderate - Need strategic improvements for growth"
        else:
            position = "challenger"
            description = "Below industry standards, requiring comprehensive digital transformation"
            strategy = "Prioritize fundamental improvements in trust, performance, and user experience"
            market_share_potential = "Limited - Focus on foundational improvements first"

        # Calculate competitive advantages and disadvantages
        strengths = []
        weaknesses = []

        if metrics.get('page_speed_score', 0) >= 80:
            strengths.append("Superior website performance")
        elif metrics.get('page_speed_score', 0) < 60:
            weaknesses.append("Below-average website performance")

        if metrics.get('trust_score', 0) >= 8:
            strengths.append("Exceptional brand credibility")
        elif metrics.get('trust_score', 0) < 6:
            weaknesses.append("Limited brand credibility")

        if metrics.get('social_platforms_count', 0) >= 4:
            strengths.append("Comprehensive social media presence")
        elif metrics.get('social_platforms_count', 0) <= 1:
            weaknesses.append("Insufficient social media engagement")

        return {
            'position': position,
            'description': description,
            'percentile': round(percentile, 1),
            'competitive_score': overall_score,
            'strategy_recommendation': strategy,
            'market_share_potential': market_share_potential,
            'competitive_advantages': strengths[:3],
            'competitive_disadvantages': weaknesses[:3],
            'benchmark_comparison': {
                'above_industry_average': overall_score > 5.5,
                'performance_gap': round(8.0 - overall_score, 1),  # Gap to excellent performance
                'improvement_potential': f"{round((8.0 - overall_score) * 10, 1)}% improvement opportunity"
            }
        }

    # Helper methods for score calculations
    def _calculate_content_volume_score(self, word_count: int) -> float:
        """Calculate content volume score based on word count"""
        if word_count >= self.benchmarks['excellent_word_count']:
            return 100.0
        elif word_count >= self.benchmarks['good_word_count']:
            return 80.0
        elif word_count >= self.benchmarks['min_word_count']:
            return 60.0
        else:
            return max(20.0, (word_count / self.benchmarks['min_word_count']) * 60)

    def _calculate_content_structure_score(self, website_data: Dict) -> float:
        """Calculate content structure quality score"""
        score = 0.0
        headings = website_data.get('heading_structure', {})

        # H1 presence and uniqueness
        h1_count = len(headings.get('h1', []))
        if h1_count == 1:
            score += 30.0  # Perfect H1 structure
        elif h1_count == 0:
            score += 0.0  # Missing H1
        else:
            score += 10.0  # Multiple H1s (not ideal)

        # H2 structure
        h2_count = len(headings.get('h2', []))
        if h2_count >= 3:
            score += 25.0
        elif h2_count >= 1:
            score += 15.0

        # H3 and deeper structure
        h3_count = len(headings.get('h3', []))
        if h3_count >= 2:
            score += 20.0
        elif h3_count >= 1:
            score += 10.0

        # Title and description presence
        if website_data.get('title'):
            score += 15.0
        if website_data.get('description'):
            score += 10.0

        return min(score, 100.0)

    def _calculate_image_optimization_score(self, images_data: Dict) -> float:
        """Calculate image optimization score"""
        if not images_data:
            return 50.0  # No images to optimize

        total_images = images_data.get('total_count', 0)
        if total_images == 0:
            return 50.0

        with_alt = images_data.get('with_alt_text', 0)
        alt_percentage = (with_alt / total_images) * 100

        return min(alt_percentage, 100.0)

    def _calculate_technical_seo_score(self, website_data: Dict, seo_data: Dict) -> float:
        """Calculate technical SEO score"""
        score = 0.0

        # SSL certificate (20 points)
        if website_data.get('has_ssl'):
            score += 20.0

        # Robots.txt (15 points)
        if seo_data.get('robots_txt'):
            score += 15.0

        # Sitemap (15 points)
        if seo_data.get('sitemap_xml'):
            score += 15.0

        # Canonical URL (10 points)
        if website_data.get('canonical_url'):
            score += 10.0

        # Structured data (20 points)
        structured_data = website_data.get('structured_data', [])
        if structured_data:
            score += min(len(structured_data) * 5, 20.0)

        # Meta tags (20 points)
        if website_data.get('title'):
            score += 10.0
        if website_data.get('description'):
            score += 10.0

        return min(score, 100.0)

    def _calculate_on_page_seo_score(self, website_data: Dict) -> float:
        """Calculate on-page SEO score"""
        score = 0.0

        # Title optimization (25 points)
        title = website_data.get('title', '')
        if title:
            title_length = len(title)
            if 30 <= title_length <= 60:
                score += 25.0
            elif title_length > 0:
                score += 15.0

        # Meta description (25 points)
        description = website_data.get('description', '')
        if description:
            desc_length = len(description)
            if 120 <= desc_length <= 160:
                score += 25.0
            elif desc_length > 0:
                score += 15.0

        # Heading structure (30 points)
        headings = website_data.get('heading_structure', {})
        if headings.get('h1'):
            score += 15.0
        if headings.get('h2'):
            score += 10.0
        if headings.get('h3'):
            score += 5.0

        # Internal linking (20 points)
        links = website_data.get('links', {})
        internal_links = links.get('internal_links', 0)
        if internal_links >= 10:
            score += 20.0
        elif internal_links >= 5:
            score += 15.0
        elif internal_links >= 1:
            score += 10.0

        return min(score, 100.0)

    def _calculate_social_presence_score(self, social_count: int) -> float:
        """Calculate social media presence score"""
        if social_count >= self.benchmarks['excellent_social_platforms']:
            return 100.0
        elif social_count >= self.benchmarks['good_social_platforms']:
            return 80.0
        elif social_count >= self.benchmarks['min_social_platforms']:
            return 60.0
        elif social_count >= 1:
            return 40.0
        else:
            return 0.0

    def _calculate_security_score(self, website_data: Dict) -> float:
        """Calculate security score"""
        score = 0.0

        # SSL certificate (50 points)
        if website_data.get('has_ssl'):
            score += 50.0

        # Secure headers and best practices (would need more detailed analysis)
        # For now, base on available data

        # No mixed content (10 points) - assume good if SSL is present
        if website_data.get('has_ssl'):
            score += 10.0

        # Modern protocols (10 points) - assume good for HTTPS sites
        if website_data.get('has_ssl'):
            score += 10.0

        # Contact information availability (security through transparency) (20 points)
        contact_info = website_data.get('contact_info', {})
        if contact_info.get('has_email'):
            score += 10.0
        if contact_info.get('has_phone'):
            score += 10.0

        # Privacy policy indicators (10 points)
        # This would need content analysis - placeholder
        score += 10.0  # Assume present for now

        return min(score, 100.0)

    def _calculate_user_experience_score(self, website_data: Dict, seo_data: Dict) -> float:
        """Calculate user experience score"""
        score = 0.0

        # Mobile friendliness (30 points)
        mobile_data = seo_data.get('mobile_friendly', {})
        if mobile_data.get('mobile_friendly'):
            score += 30.0

        # Loading speed (25 points)
        response_time = website_data.get('response_time', 5.0)
        if response_time < 1.0:
            score += 25.0
        elif response_time < 2.0:
            score += 20.0
        elif response_time < 3.0:
            score += 15.0
        elif response_time < 5.0:
            score += 10.0

        # Navigation structure (20 points)
        links = website_data.get('links', {})
        internal_links = links.get('internal_links', 0)
        if internal_links >= 10:
            score += 20.0
        elif internal_links >= 5:
            score += 15.0
        elif internal_links >= 2:
            score += 10.0

        # Content accessibility (15 points)
        accessibility = website_data.get('accessibility_features', {})
        if accessibility.get('has_lang_attribute'):
            score += 5.0
        if accessibility.get('images_with_alt', 0) > 0:
            score += 10.0

        # Contact accessibility (10 points)
        contact_info = website_data.get('contact_info', {})
        if contact_info.get('has_email') or contact_info.get('has_phone'):
            score += 10.0

        return min(score, 100.0)

    def _convert_loading_time_to_score(self, response_time: float) -> float:
        """Convert loading time to a 0-100 score"""
        if response_time <= 1.0:
            return 100.0
        elif response_time <= 2.0:
            return 85.0
        elif response_time <= 3.0:
            return 70.0
        elif response_time <= 4.0:
            return 55.0
        elif response_time <= 5.0:
            return 40.0
        else:
            return max(10.0, 40.0 - (response_time - 5.0) * 5)

    def _calculate_competitive_advantage(self, data: Dict) -> float:
        """Calculate competitive advantage score"""
        trust_score = data.get('trust_score', {})
        website_data = data.get('website_data', {})

        # Base score from trust score
        base_score = trust_score.get('overall', 5.0) * 10

        # Bonus points for differentiating factors
        bonus = 0.0

        # Advanced technology implementation
        technologies = website_data.get('technologies', [])
        modern_tech = ['React', 'Vue', 'Angular', 'Next.js']
        if any(tech in technologies for tech in modern_tech):
            bonus += 10.0

        # Comprehensive social presence
        social_count = len(website_data.get('social_links', {}))
        if social_count >= 5:
            bonus += 10.0

        # Advanced SEO implementation
        if website_data.get('structured_data'):
            bonus += 10.0

        return min(base_score + bonus, 100.0)

    def _calculate_weighted_average(self, weighted_scores: List[tuple]) -> float:
        """Calculate weighted average from list of (score, weight) tuples"""
        if not weighted_scores:
            return 0.0

        total_weighted = sum(score * weight for score, weight in weighted_scores)
        total_weights = sum(weight for _, weight in weighted_scores)

        if total_weights == 0:
            return 0.0

        return round(total_weighted / total_weights, 1)

    def _assess_growth_potential(self, data: Dict, metrics: Dict) -> Dict:
        """Assess growth potential based on current performance and gaps"""
        trust_score = metrics.get('trust_score', 5.0)
        gaps = []
        potential_impact = 0.0

        # Identify high-impact growth opportunities
        if metrics.get('page_speed_score', 0) < 80:
            gaps.append("Performance optimization")
            potential_impact += 1.5

        if not metrics.get('mobile_friendly'):
            gaps.append("Mobile optimization")
            potential_impact += 2.0

        if metrics.get('social_platforms_count', 0) < 3:
            gaps.append("Social media expansion")
            potential_impact += 1.0

        if metrics.get('content_volume_score', 0) < 70:
            gaps.append("Content development")
            potential_impact += 1.2

        # Calculate growth potential score
        max_potential = 10.0
        current_score = trust_score
        growth_ceiling = min(max_potential, current_score + potential_impact)
        growth_percentage = ((growth_ceiling - current_score) / current_score) * 100

        return {
            'current_score': current_score,
            'potential_score': round(growth_ceiling, 1),
            'growth_percentage': round(growth_percentage, 1),
            'primary_growth_drivers': gaps[:3],
            'estimated_timeline': self._estimate_improvement_timeline(gaps),
            'investment_level': self._estimate_investment_level(gaps)
        }

    def _identify_risk_factors(self, data: Dict, metrics: Dict) -> List[str]:
        """Identify potential risk factors that could impact performance"""
        risks = []
        website_data = data.get('website_data', {})

        # Security risks
        if not website_data.get('has_ssl'):
            risks.append("🔒 Security Risk: Missing SSL certificate may deter users and impact search rankings")

        # Performance risks
        if metrics.get('page_speed_score', 0) < 50:
            risks.append("⚡ Performance Risk: Slow loading times significantly impact user experience and conversions")

        # Mobile risks
        if not metrics.get('mobile_friendly'):
            risks.append("📱 Mobile Risk: Non-responsive design alienates 60%+ of mobile users")

        # Content risks
        if metrics.get('word_count', 0) < 200:
            risks.append("📝 Content Risk: Insufficient content limits SEO potential and user engagement")

        # Reputation risks
        if metrics.get('trust_score', 5.0) < 4.0:
            risks.append("⭐ Reputation Risk: Low trust score may significantly impact customer acquisition")

        # Technical risks
        if not website_data.get('has_robots_txt') and not website_data.get('has_sitemap'):
            risks.append("🔧 Technical Risk: Missing fundamental SEO infrastructure")

        return risks[:4]  # Return top 4 risks

    def _identify_market_opportunities(self, data: Dict, metrics: Dict) -> List[str]:
        """Identify market opportunities based on analysis"""
        opportunities = []
        website_data = data.get('website_data', {})

        # Content opportunities
        if metrics.get('content_volume_score', 0) < 80:
            opportunities.append(
                "📝 Content Marketing: Develop comprehensive content strategy to capture long-tail keywords")

        # Social opportunities
        if metrics.get('social_platforms_count', 0) < 4:
            opportunities.append("📲 Social Expansion: Establish presence on untapped platforms for audience growth")

        # Technical opportunities
        if not website_data.get('structured_data'):
            opportunities.append("🏷️ Rich Snippets: Implement structured data for enhanced search appearance")

        # Performance opportunities
        if metrics.get('page_speed_score', 0) < 90:
            opportunities.append("⚡ Performance Edge: Optimize for superior loading speeds to outperform competitors")

        # Local opportunities (if applicable)
        contact_info = website_data.get('contact_info', {})
        if contact_info.get('has_address'):
            opportunities.append("📍 Local SEO: Leverage location-based optimization for regional dominance")

        return opportunities[:4]

    def _calculate_overall_performance_score(self, metrics: Dict) -> float:
        """Calculate overall performance score from all metrics"""
        # Weight the most important factors
        weighted_scores = [
            (metrics.get('trust_score', 5.0) * 10, 0.25),  # Trust score (convert to 0-100)
            (metrics.get('page_speed_score', 0), 0.20),
            (metrics.get('overall_user_experience', 0), 0.15),
            (metrics.get('social_presence_score', 0), 0.10),
            (metrics.get('security_score', 0), 0.15),
            (metrics.get('content_volume_score', 0), 0.10),
            (metrics.get('technical_seo_score', 0), 0.05)
        ]

        return self._calculate_weighted_average(weighted_scores)

    def _generate_month_over_month_analysis(self, metrics: Dict) -> Dict:
        """Generate month-over-month analysis (simulated for now)"""
        # In production, this would compare with historical data
        # For now, generate realistic simulated changes
        import random

        return {
            'traffic_change': '+0%',  # Would need historical data
            'trust_score_change': '+0.0',
            'page_speed_change': '+0%',
            'social_growth': '+0%',
            'note': 'Historical data required for month-over-month comparison',
            'trending_up': [],
            'trending_down': [],
            'stable_metrics': ['trust_score', 'page_speed', 'social_presence']
        }

    def _benchmark_against_industry(self, metrics: Dict) -> Dict:
        """Benchmark performance against industry standards"""
        benchmarks = {}

        # Performance benchmarking
        for metric, value in metrics.items():
            if metric.endswith('_score'):
                if value >= 90:
                    benchmark = 'Excellent - Top 10%'
                elif value >= 80:
                    benchmark = 'Good - Top 25%'
                elif value >= 60:
                    benchmark = 'Average - Industry Standard'
                elif value >= 40:
                    benchmark = 'Below Average - Improvement Needed'
                else:
                    benchmark = 'Poor - Immediate Action Required'

                benchmarks[metric] = {
                    'score': value,
                    'benchmark': benchmark,
                    'percentile': min(value, 100)
                }

        return benchmarks

    def _count_data_sources(self, data: Dict) -> int:
        """Count the number of data sources used in analysis"""
        sources = 0
        if data.get('website_data'):
            sources += 1
        if data.get('seo_data'):
            sources += 1
        if data.get('social_data'):
            sources += 1
        if data.get('reputation_data'):
            sources += 1
        if data.get('competitor_data'):
            sources += 1
        return sources

    def _calculate_confidence_score(self, data: Dict) -> float:
        """Calculate confidence score based on data completeness"""
        total_sources = 5  # website, seo, social, reputation, competitor
        available_sources = self._count_data_sources(data)

        base_confidence = (available_sources / total_sources) * 100

        # Adjust based on data quality
        website_data = data.get('website_data', {})
        if website_data.get('error'):
            base_confidence -= 20

        # Bonus for AI enhancement
        if self.openai_available:
            base_confidence += 5

        return max(0, min(100, base_confidence))

    def _estimate_improvement_timeline(self, gaps: List[str]) -> str:
        """Estimate timeline for implementing improvements"""
        if len(gaps) <= 2:
            return "2-4 weeks"
        elif len(gaps) <= 4:
            return "1-2 months"
        else:
            return "2-3 months"

    def _estimate_investment_level(self, gaps: List[str]) -> str:
        """Estimate investment level required for improvements"""
        high_effort_items = ['Mobile optimization', 'Performance optimization']

        if any(item in gaps for item in high_effort_items):
            return "Medium to High"
        elif len(gaps) > 3:
            return "Medium"
        else:
            return "Low to Medium"

    def _generate_emergency_fallback_summary(self, data: Dict) -> Dict:
        """Generate basic summary when all else fails"""
        website_data = data.get('website_data', {})
        trust_score = data.get('trust_score', {})

        return {
            'organic_traffic_change': '+0%',
            'ai_visibility': trust_score.get('overall', 5.0),
            'avg_rating': 0,
            'overall_performance_score': 50.0,
            'summary_text': f"Analysis completed for {website_data.get('domain', 'the website')}. Basic performance metrics have been evaluated with opportunities for improvement identified.",
            'key_insights': ["Website analysis completed successfully", "Performance metrics calculated",
                             "Improvement opportunities identified"],
            'performance_highlights': ["Analysis completed"],
            'areas_for_improvement': ["Detailed analysis required", "Performance optimization needed"],
            'competitive_position': {
                'position': 'average_performer',
                'description': 'Standard digital presence',
                'percentile': 50.0
            },
            'generated_at': time.time(),
            'ai_enhanced': False,
            'note': 'Basic fallback summary - limited data available'
        }