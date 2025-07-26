# data_collectors/competitor_collector.py
import requests
import time
import logging
from typing import Dict, List
from django.conf import settings

logger = logging.getLogger(__name__)


class CompetitorCollector:
    """
    Collect competitor analysis data

    Note: This is a placeholder implementation that generates realistic sample data.
    In production, you would integrate with competitive intelligence APIs:
    - SEMrush API
    - Ahrefs API
    - SimilarWeb API
    - SerpAPI for search results analysis
    """

    def __init__(self):
        self.timeout = 10
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MarketingBot/1.0)'
        })

    def collect_competitor_data(self, domain: str, keywords: List[str]) -> Dict:
        """
        Main method to collect competitor analysis data

        Args:
            domain: Target website domain (e.g., 'example.com')
            keywords: List of keywords for competitor discovery

        Returns:
            Dictionary with competitor analysis data
        """
        try:
            logger.info(f"Collecting competitor data for {domain}")

            # Discover competitors using multiple methods
            competitors = self._discover_competitors(domain, keywords)

            # Analyze market position
            market_analysis = self._analyze_market_position(domain, competitors)

            # Identify competitive gaps and opportunities
            competitive_gaps = self._identify_competitive_gaps(domain, competitors)
            opportunities = self._identify_opportunities(domain, competitors)

            # Compare SEO metrics
            seo_comparison = self._compare_seo_metrics(domain, competitors)

            # Analyze content strategies
            content_analysis = self._analyze_content_strategies(domain, competitors)

            result = {
                'domain': domain,
                'keywords_analyzed': keywords[:5],  # Top 5 keywords used for analysis
                'collection_timestamp': time.time(),
                'competitors': competitors,
                'competitor_count': len(competitors),
                'market_analysis': market_analysis,
                'competitive_gaps': competitive_gaps,
                'opportunities': opportunities,
                'seo_comparison': seo_comparison,
                'content_analysis': content_analysis,
                'competitive_strategy': self._generate_competitive_strategy(domain, competitors),
                'recommendations': self._generate_recommendations(domain, competitors, competitive_gaps),
                'note': 'This is placeholder data - integrate real APIs for production'
            }

            logger.info(f"Competitor data collection completed for {domain}")
            return result

        except Exception as e:
            logger.error(f"Error collecting competitor data for {domain}: {e}")
            return {
                'domain': domain,
                'error': str(e),
                'collection_timestamp': time.time()
            }

    def _discover_competitors(self, domain: str, keywords: List[str]) -> List[Dict]:
        """
        Discover competitors through multiple methods

        In production, this would:
        1. Use SEMrush/Ahrefs to find keyword competitors
        2. Use SimilarWeb for traffic-based competitors
        3. Analyze search results for target keywords
        4. Find industry-specific competitors
        """
        competitors = []

        # Method 1: Keyword-based competitors
        keyword_competitors = self._find_keyword_competitors(domain, keywords)
        competitors.extend(keyword_competitors)

        # Method 2: Industry-based competitors
        industry_competitors = self._find_industry_competitors(domain)
        competitors.extend(industry_competitors)

        # Method 3: Similar domain competitors
        similar_competitors = self._find_similar_domain_competitors(domain)
        competitors.extend(similar_competitors)

        # Remove duplicates and rank by relevance
        unique_competitors = self._deduplicate_competitors(competitors)
        ranked_competitors = self._rank_competitors(unique_competitors, domain)

        return ranked_competitors[:8]  # Return top 8 competitors

    def _find_keyword_competitors(self, domain: str, keywords: List[str]) -> List[Dict]:
        """Find competitors ranking for the same keywords"""
        competitors = []

        if not keywords:
            return competitors

        # Generate realistic competitor domains based on keywords
        industry_hint = self._extract_industry_from_keywords(keywords)

        competitor_patterns = [
            f"{industry_hint}pro.com",
            f"best{industry_hint}.com",
            f"{industry_hint}solutions.com",
            f"top{industry_hint}.com",
            f"{industry_hint}experts.com"
        ]

        for i, pattern in enumerate(competitor_patterns[:4]):
            competitor_domain = pattern.lower()

            # Generate realistic metrics
            common_keywords = min(len(keywords), 2 + i)
            estimated_traffic = 5000 + (hash(competitor_domain) % 45000)

            competitor = {
                'domain': competitor_domain,
                'discovery_method': 'keyword_analysis',
                'common_keywords': common_keywords,
                'keyword_overlap_score': 30 + (hash(competitor_domain) % 50),
                'estimated_monthly_traffic': estimated_traffic,
                'competition_level': ['high', 'medium', 'low'][hash(competitor_domain) % 3],
                'ranking_keywords': keywords[:common_keywords] if keywords else []
            }
            competitors.append(competitor)

        return competitors

    def _find_industry_competitors(self, domain: str) -> List[Dict]:
        """Find competitors in the same industry"""
        competitors = []

        # Guess industry from domain
        industry = self._guess_industry_from_domain(domain)

        # Generate industry leader domains
        industry_patterns = [
            f"leading{industry.lower()}.com",
            f"{industry.lower()}leader.com",
            f"premier{industry.lower()}.com"
        ]

        for pattern in industry_patterns[:2]:
            competitor_domain = pattern
            estimated_traffic = 15000 + (hash(competitor_domain) % 85000)

            competitor = {
                'domain': competitor_domain,
                'discovery_method': 'industry_analysis',
                'industry': industry,
                'estimated_monthly_traffic': estimated_traffic,
                'market_position': ['leader', 'challenger', 'follower'][hash(competitor_domain) % 3],
                'brand_strength': ['strong', 'medium', 'weak'][hash(competitor_domain) % 3]
            }
            competitors.append(competitor)

        return competitors

    def _find_similar_domain_competitors(self, domain: str) -> List[Dict]:
        """Find competitors with similar domain characteristics"""
        competitors = []

        # Extract base name from domain
        base_name = domain.split('.')[0]

        similar_patterns = [
            f"{base_name}plus.com",
            f"{base_name}pro.com",
            f"my{base_name}.com"
        ]

        for pattern in similar_patterns[:2]:
            competitor_domain = pattern
            estimated_traffic = 8000 + (hash(competitor_domain) % 35000)

            competitor = {
                'domain': competitor_domain,
                'discovery_method': 'similar_domains',
                'similarity_score': 60 + (hash(competitor_domain) % 35),
                'estimated_monthly_traffic': estimated_traffic,
                'domain_strength': self._calculate_domain_strength(competitor_domain)
            }
            competitors.append(competitor)

        return competitors

    def _deduplicate_competitors(self, competitors: List[Dict]) -> List[Dict]:
        """Remove duplicate competitors"""
        seen_domains = set()
        unique_competitors = []

        for competitor in competitors:
            domain = competitor.get('domain', '')
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                unique_competitors.append(competitor)

        return unique_competitors

    def _rank_competitors(self, competitors: List[Dict], target_domain: str) -> List[Dict]:
        """Rank competitors by relevance and competitive threat"""
        for competitor in competitors:
            relevance_score = self._calculate_relevance_score(competitor, target_domain)
            threat_level = self._calculate_threat_level(competitor)

            competitor['relevance_score'] = relevance_score
            competitor['threat_level'] = threat_level
            competitor['competitive_strength'] = self._assess_competitive_strength(competitor)

        # Sort by relevance score (highest first)
        return sorted(competitors, key=lambda x: x.get('relevance_score', 0), reverse=True)

    def _calculate_relevance_score(self, competitor: Dict, target_domain: str) -> float:
        """Calculate how relevant this competitor is"""
        score = 0.0

        # Traffic weight (40% of score)
        traffic = competitor.get('estimated_monthly_traffic', 0)
        if traffic > 50000:
            score += 40
        elif traffic > 20000:
            score += 30
        elif traffic > 10000:
            score += 20
        elif traffic > 5000:
            score += 10

        # Keyword overlap weight (30% of score)
        keyword_overlap = competitor.get('keyword_overlap_score', 0)
        score += keyword_overlap * 0.3

        # Similarity weight (20% of score)
        similarity = competitor.get('similarity_score', 50)
        score += similarity * 0.2

        # Discovery method weight (10% of score)
        method = competitor.get('discovery_method', '')
        if method == 'keyword_analysis':
            score += 10
        elif method == 'industry_analysis':
            score += 8
        elif method == 'similar_domains':
            score += 6

        return round(score, 1)

    def _calculate_threat_level(self, competitor: Dict) -> str:
        """Calculate competitive threat level"""
        relevance = competitor.get('relevance_score', 0)
        traffic = competitor.get('estimated_monthly_traffic', 0)

        if relevance > 70 and traffic > 30000:
            return 'high'
        elif relevance > 50 or traffic > 15000:
            return 'medium'
        else:
            return 'low'

    def _assess_competitive_strength(self, competitor: Dict) -> str:
        """Assess overall competitive strength"""
        traffic = competitor.get('estimated_monthly_traffic', 0)
        market_position = competitor.get('market_position', 'follower')

        if traffic > 50000 or market_position == 'leader':
            return 'strong'
        elif traffic > 20000 or market_position == 'challenger':
            return 'medium'
        else:
            return 'weak'

    def _analyze_market_position(self, domain: str, competitors: List[Dict]) -> Dict:
        """Analyze market position relative to competitors"""
        if not competitors:
            return {
                'market_size_estimate': 100000,
                'competitive_intensity': 'low',
                'market_position': 'unknown'
            }

        # Calculate market metrics
        total_competitor_traffic = sum(c.get('estimated_monthly_traffic', 0) for c in competitors)
        avg_competitor_traffic = total_competitor_traffic / len(competitors) if competitors else 0

        high_threat_count = sum(1 for c in competitors if c.get('threat_level') == 'high')

        # Determine competitive intensity
        if high_threat_count >= 3:
            competitive_intensity = 'high'
        elif high_threat_count >= 1:
            competitive_intensity = 'medium'
        else:
            competitive_intensity = 'low'

        return {
            'total_competitors_found': len(competitors),
            'average_competitor_traffic': round(avg_competitor_traffic, 0),
            'total_addressable_market': total_competitor_traffic,
            'competitive_intensity': competitive_intensity,
            'high_threat_competitors': high_threat_count,
            'market_leaders': [c['domain'] for c in competitors if c.get('market_position') == 'leader'][:3],
            'key_success_factors': [
                'SEO optimization',
                'Content quality',
                'User experience',
                'Brand recognition'
            ]
        }

    def _identify_competitive_gaps(self, domain: str, competitors: List[Dict]) -> List[str]:
        """Identify gaps where target domain is behind competitors"""
        gaps = []

        # Analyze based on competitor data
        if competitors:
            avg_traffic = sum(c.get('estimated_monthly_traffic', 0) for c in competitors) / len(competitors)

            # Traffic gap
            if avg_traffic > 20000:
                gaps.append("Traffic volume significantly below competitor average")

            # Keyword gaps
            total_keywords = sum(c.get('common_keywords', 0) for c in competitors)
            if total_keywords > 10:
                gaps.append("Missing opportunities in competitor keyword targeting")

            # Market position gaps
            leaders = [c for c in competitors if c.get('market_position') == 'leader']
            if leaders:
                gaps.append("Brand recognition and market leadership gaps")

        # Add common competitive gaps
        common_gaps = [
            "Content marketing strategy could be enhanced",
            "Social media presence needs strengthening",
            "SEO optimization opportunities exist",
            "Local search presence could be improved",
            "Mobile user experience optimization needed"
        ]

        # Select 3-4 relevant gaps
        selected_gaps = gaps + common_gaps[:4 - len(gaps)]
        return selected_gaps[:4]

    def _identify_opportunities(self, domain: str, competitors: List[Dict]) -> List[str]:
        """Identify market opportunities"""
        opportunities = [
            "Underserved keywords with commercial intent",
            "Content gaps in competitor strategies",
            "Local market expansion possibilities",
            "Emerging social media platforms",
            "Partnership and collaboration potential",
            "Niche market segments with less competition",
            "Technology adoption advantages",
            "Customer service differentiation opportunities"
        ]

        # Return 4-5 relevant opportunities
        return opportunities[:5]

    def _compare_seo_metrics(self, domain: str, competitors: List[Dict]) -> Dict:
        """Compare SEO metrics with competitors"""
        if not competitors:
            return {'note': 'No competitors found for SEO comparison'}

        # Calculate competitor averages
        avg_traffic = sum(c.get('estimated_monthly_traffic', 0) for c in competitors) / len(competitors)
        top_competitor_traffic = max(c.get('estimated_monthly_traffic', 0) for c in competitors)

        # Generate realistic metrics for target domain
        estimated_domain_traffic = 3000 + (hash(domain) % 15000)

        return {
            'traffic_comparison': {
                'your_estimated_traffic': estimated_domain_traffic,
                'competitor_average': round(avg_traffic, 0),
                'top_competitor': top_competitor_traffic,
                'traffic_gap': round(avg_traffic - estimated_domain_traffic, 0)
            },
            'keyword_analysis': {
                'total_competitor_keywords': sum(c.get('common_keywords', 0) for c in competitors),
                'keyword_opportunities': len(competitors) * 3,  # Estimate
                'competition_difficulty': 'medium'
            },
            'domain_authority_estimate': {
                'your_domain': 35 + (hash(domain) % 30),
                'competitor_average': 45 + (hash(domain[:3]) % 25),
                'improvement_needed': True
            },
            'content_volume_comparison': {
                'estimated_pages': 15 + (hash(domain) % 85),
                'competitor_average_pages': 50 + (hash(domain) % 150),
                'content_gap': True
            }
        }

    def _analyze_content_strategies(self, domain: str, competitors: List[Dict]) -> Dict:
        """Analyze competitor content strategies"""
        return {
            'content_types_analysis': {
                'blog_content': 'competitors_ahead',
                'product_pages': 'competitive_parity',
                'case_studies': 'opportunity_area',
                'video_content': 'underutilized',
                'downloadable_resources': 'limited_presence'
            },
            'content_quality_indicators': {
                'average_word_count': 600 + (hash(domain) % 400),
                'competitor_average_word_count': 800 + (hash(domain) % 600),
                'content_freshness': 'needs_improvement',
                'multimedia_usage': 'below_average'
            },
            'content_gaps_identified': [
                'How-to guides and tutorials',
                'Industry trend analysis and insights',
                'Customer success stories and testimonials',
                'Comparison and review content',
                'Interactive tools and calculators'
            ],
            'content_opportunities': [
                'Long-form educational content',
                'Video marketing expansion',
                'Podcast or webinar series',
                'User-generated content campaigns',
                'Expert interview series'
            ]
        }

    def _generate_competitive_strategy(self, domain: str, competitors: List[Dict]) -> Dict:
        """Generate comprehensive competitive strategy"""
        if not competitors:
            return {'strategy': 'Focus on basic SEO and content development'}

        high_threat_competitors = [c for c in competitors if c.get('threat_level') == 'high']

        return {
            'immediate_actions': [
                'Analyze top 3 competitor content strategies',
                'Identify and target competitor keyword gaps',
                'Optimize page loading speed to match leaders',
                'Enhance social media presence to competitive levels'
            ],
            'short_term_strategy': [
                'Develop unique value proposition to differentiate',
                'Build comprehensive content marketing program',
                'Improve local SEO and geographic targeting',
                'Implement advanced analytics and tracking'
            ],
            'long_term_positioning': [
                'Establish thought leadership in niche areas',
                'Build strategic partnerships for market expansion',
                'Invest in emerging technologies and trends',
                'Develop proprietary tools or resources'
            ],
            'defensive_strategies': [
                'Monitor competitor content and keyword strategies',
                'Protect and strengthen brand keyword rankings',
                'Maintain customer loyalty and retention programs',
                'Quick response system for competitive moves'
            ],
            'competitive_advantages_to_leverage': [
                'Faster customer service response times',
                'Specialized industry knowledge and expertise',
                'Local market presence and relationships',
                'Agility and ability to adapt quickly'
            ],
            'focus_areas': [
                'Content marketing excellence',
                'Technical SEO optimization',
                'User experience improvements',
                'Brand awareness building'
            ]
        }

    def _generate_recommendations(self, domain: str, competitors: List[Dict], gaps: List[str]) -> List[str]:
        """Generate actionable competitive recommendations"""
        recommendations = []

        if not competitors:
            recommendations.extend([
                "Conduct comprehensive competitor research using SEMrush or Ahrefs",
                "Identify key industry players and analyze their strategies",
                "Focus on fundamental SEO and content optimization"
            ])
            return recommendations

        # Traffic-based recommendations
        avg_traffic = sum(c.get('estimated_monthly_traffic', 0) for c in competitors) / len(competitors)
        if avg_traffic > 20000:
            recommendations.append("Implement aggressive SEO strategy to close traffic gap")

        # Keyword-based recommendations
        total_competitor_keywords = sum(c.get('common_keywords', 0) for c in competitors)
        if total_competitor_keywords > 15:
            recommendations.append("Target competitor keyword gaps for quick ranking wins")

        # Threat-based recommendations
        high_threats = [c for c in competitors if c.get('threat_level') == 'high']
        if high_threats:
            top_threat = high_threats[0]['domain']
            recommendations.append(f"Study and benchmark against top competitor: {top_threat}")

        # Gap-based recommendations
        if gaps:
            primary_gap = gaps[0]
            recommendations.append(f"Priority focus: {primary_gap.lower()}")

        # Content recommendations
        recommendations.append("Develop content calendar to match competitor publishing frequency")

        # Generic strategic recommendations
        recommendations.extend([
            "Monitor competitor social media and content strategies monthly",
            "Set up Google Alerts for competitor brand mentions and activities"
        ])

        return recommendations[:6]  # Return top 6 recommendations

    # Helper methods
    def _extract_industry_from_keywords(self, keywords: List[str]) -> str:
        """Extract industry hint from keywords"""
        if not keywords:
            return 'business'

        # Simple industry detection based on keywords
        keyword_text = ' '.join(keywords).lower()

        if any(term in keyword_text for term in ['tech', 'software', 'app', 'digital']):
            return 'tech'
        elif any(term in keyword_text for term in ['health', 'medical', 'care']):
            return 'health'
        elif any(term in keyword_text for term in ['food', 'restaurant', 'dining']):
            return 'food'
        elif any(term in keyword_text for term in ['finance', 'money', 'loan', 'bank']):
            return 'finance'
        else:
            return 'business'

    def _guess_industry_from_domain(self, domain: str) -> str:
        """Guess industry from domain name"""
        domain_lower = domain.lower()

        if any(term in domain_lower for term in ['tech', 'software', 'app', 'digital', 'web']):
            return 'Technology'
        elif any(term in domain_lower for term in ['health', 'medical', 'care', 'wellness']):
            return 'Healthcare'
        elif any(term in domain_lower for term in ['finance', 'money', 'loan', 'bank', 'invest']):
            return 'Finance'
        elif any(term in domain_lower for term in ['shop', 'store', 'retail', 'buy']):
            return 'Retail'
        elif any(term in domain_lower for term in ['food', 'restaurant', 'cafe', 'dining']):
            return 'Food'
        elif any(term in domain_lower for term in ['real', 'property', 'home', 'house']):
            return 'RealEstate'
        else:
            return 'Business'

    def _calculate_domain_strength(self, domain: str) -> str:
        """Calculate domain strength based on domain characteristics"""
        # Simple heuristic based on domain name
        score = 0

        # Short domains are typically stronger
        if len(domain) < 10:
            score += 2
        elif len(domain) < 15:
            score += 1

        # .com domains are typically stronger
        if domain.endswith('.com'):
            score += 2

        # No hyphens or numbers is better
        if '-' not in domain and not any(char.isdigit() for char in domain):
            score += 1

        # Simple hash-based variation
        score += (hash(domain) % 3)

        if score >= 5:
            return 'strong'
        elif score >= 3:
            return 'medium'
        else:
            return 'weak'