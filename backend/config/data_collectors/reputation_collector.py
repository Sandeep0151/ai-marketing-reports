# data_collectors/reputation_collector.py
import requests
import time
import logging
from typing import Dict, List
from django.conf import settings

logger = logging.getLogger(__name__)


class ReputationCollector:
    """
    Collect online reputation data from review platforms

    Note: This is a placeholder implementation that generates realistic sample data.
    In production, you would integrate with actual review platform APIs:
    - Google My Business API
    - Trustpilot API
    - Yelp Fusion API
    - Better Business Bureau (web scraping)
    """

    def __init__(self):
        self.timeout = 10
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MarketingBot/1.0)'
        })

    def collect_reputation_data(self, domain: str, company_name: str) -> Dict:
        """
        Main method to collect reputation data

        Args:
            domain: Website domain (e.g., 'example.com')
            company_name: Company name for review platform search

        Returns:
            Dictionary with reputation metrics and analysis
        """
        try:
            logger.info(f"Collecting reputation data for {domain}")

            # Collect data from each review platform
            platform_data = {
                'google_reviews': self._get_google_reviews(company_name),
                'trustpilot': self._get_trustpilot_data(company_name),
                'yelp': self._get_yelp_data(company_name),
                'bbb': self._get_bbb_data(company_name)
            }

            # Calculate overall reputation metrics
            reputation_summary = self._calculate_reputation_summary(platform_data)

            # Perform sentiment analysis
            sentiment_analysis = self._analyze_sentiment(platform_data)

            result = {
                'domain': domain,
                'company_name': company_name,
                'collection_timestamp': time.time(),
                'platform_data': platform_data,
                'summary': reputation_summary,
                'sentiment_analysis': sentiment_analysis,
                'recommendations': self._generate_recommendations(platform_data, reputation_summary),
                'risk_factors': self._identify_risk_factors(platform_data, reputation_summary),
                'note': 'This is placeholder data - integrate real APIs for production'
            }

            logger.info(f"Reputation data collection completed for {domain}")
            return result

        except Exception as e:
            logger.error(f"Error collecting reputation data for {domain}: {e}")
            return {
                'domain': domain,
                'error': str(e),
                'collection_timestamp': time.time()
            }

    def _get_google_reviews(self, company_name: str) -> Dict:
        """
        Get Google My Business reviews data

        In production, this would use Google My Business API or Google Places API
        """
        # Simulate business listing discovery (80% chance of having Google listing)
        has_listing = self._has_listing_probability(company_name, 'google', 0.8)

        if not has_listing:
            return {
                'business_found': False,
                'recommendation': 'Create and claim Google My Business listing'
            }

        # Generate realistic review data
        review_count = self._generate_review_count('google')
        avg_rating = self._generate_rating('google')

        return {
            'business_found': True,
            'platform': 'google_reviews',
            'business_name': company_name,
            'rating': avg_rating,
            'review_count': review_count,
            'rating_distribution': self._generate_rating_distribution(review_count, avg_rating),
            'claimed_listing': True,
            'response_rate': f"{75 + (hash(company_name) % 25)}%",
            'avg_response_time': '1 day',
            'recent_reviews': self._generate_sample_reviews('google', company_name, 3),
            'business_category': self._guess_business_category(company_name),
            'photos_count': 10 + (hash(company_name) % 40),
            'verified_business': True
        }

    def _get_trustpilot_data(self, company_name: str) -> Dict:
        """
        Get Trustpilot reviews data

        In production, this would use Trustpilot Business API
        """
        # 40% chance of having Trustpilot profile
        has_profile = self._has_listing_probability(company_name, 'trustpilot', 0.4)

        if not has_profile:
            return {
                'profile_found': False,
                'recommendation': 'Create Trustpilot business profile to build trust'
            }

        review_count = self._generate_review_count('trustpilot')
        avg_rating = self._generate_rating('trustpilot')
        trust_score = min(5.0, avg_rating + 0.2)  # Trustpilot trust score is usually slightly higher

        return {
            'profile_found': True,
            'platform': 'trustpilot',
            'company_name': company_name,
            'trust_score': round(trust_score, 1),
            'rating': avg_rating,
            'review_count': review_count,
            'rating_distribution': self._generate_rating_distribution(review_count, avg_rating),
            'claimed_profile': hash(company_name) % 3 == 0,  # 33% have claimed profiles
            'response_rate': f"{60 + (hash(company_name) % 35)}%",
            'recent_reviews': self._generate_sample_reviews('trustpilot', company_name, 3),
            'monthly_review_trend': 'stable',
            'trust_level': self._calculate_trust_level(trust_score),
            'website_verified': True
        }

    def _get_yelp_data(self, company_name: str) -> Dict:
        """
        Get Yelp business data

        In production, this would use Yelp Fusion API
        """
        # 60% chance of having Yelp listing (depends on business type)
        has_listing = self._has_listing_probability(company_name, 'yelp', 0.6)

        if not has_listing:
            return {
                'business_found': False,
                'recommendation': 'Create Yelp business listing if applicable to your industry'
            }

        review_count = self._generate_review_count('yelp')
        avg_rating = self._generate_rating('yelp')

        return {
            'business_found': True,
            'platform': 'yelp',
            'business_name': company_name,
            'rating': avg_rating,
            'review_count': review_count,
            'rating_distribution': self._generate_rating_distribution(review_count, avg_rating),
            'claimed_listing': hash(company_name) % 2 == 0,  # 50% have claimed listings
            'price_range': self._generate_price_range(),
            'categories': [self._guess_business_category(company_name)],
            'recent_reviews': self._generate_sample_reviews('yelp', company_name, 3),
            'photos_count': 15 + (hash(company_name) % 85),
            'check_ins': 25 + (hash(company_name) % 475),
            'tips_count': 5 + (hash(company_name) % 45)
        }

    def _get_bbb_data(self, company_name: str) -> Dict:
        """
        Get Better Business Bureau data

        In production, this would require web scraping BBB website
        """
        # 30% chance of having BBB listing
        has_listing = self._has_listing_probability(company_name, 'bbb', 0.3)

        if not has_listing:
            return {
                'business_found': False,
                'recommendation': 'Consider BBB accreditation for enhanced credibility'
            }

        # Generate BBB rating (A+ to F scale)
        bbb_rating = self._generate_bbb_rating()
        accredited = hash(company_name) % 4 == 0  # 25% are BBB accredited

        return {
            'business_found': True,
            'platform': 'bbb',
            'company_name': company_name,
            'bbb_rating': bbb_rating,
            'accredited': accredited,
            'years_in_business': self._calculate_years_in_business(),
            'complaint_count_3yr': max(0, (hash(company_name) % 20) - 15),  # Most have 0-5 complaints
            'complaint_count_12mo': max(0, (hash(company_name) % 10) - 7),  # Most have 0-3 recent complaints
            'complaints_resolved': '90%' if accredited else f"{70 + (hash(company_name) % 25)}%",
            'business_type': self._guess_business_category(company_name),
            'response_to_complaints': 'Good' if accredited else 'Average'
        }

    def _calculate_reputation_summary(self, platform_data: Dict) -> Dict:
        """Calculate overall reputation metrics"""
        total_reviews = 0
        weighted_rating_sum = 0
        total_weight = 0
        platforms_found = 0

        # Platform weights for overall calculation
        platform_weights = {
            'google_reviews': 0.4,  # Google has highest weight
            'trustpilot': 0.3,
            'yelp': 0.2,
            'bbb': 0.1
        }

        platform_scores = []

        for platform, weight in platform_weights.items():
            data = platform_data.get(platform, {})

            if (data.get('business_found') or data.get('profile_found')):
                platforms_found += 1

                # Get rating (handle different field names)
                rating = data.get('rating', data.get('trust_score', 0))
                review_count = data.get('review_count', 0)

                if rating > 0:
                    weighted_rating_sum += rating * weight
                    total_weight += weight
                    total_reviews += review_count

                    platform_scores.append({
                        'platform': platform,
                        'rating': rating,
                        'review_count': review_count,
                        'weight': weight
                    })

        # Calculate overall rating
        overall_rating = weighted_rating_sum / total_weight if total_weight > 0 else 0

        # Calculate reputation score (0-100)
        reputation_score = self._calculate_reputation_score(overall_rating, total_reviews, platforms_found)

        return {
            'overall_rating': round(overall_rating, 1),
            'total_reviews': total_reviews,
            'platforms_found': platforms_found,
            'reputation_score': round(reputation_score, 1),
            'reputation_level': self._get_reputation_level(reputation_score),
            'platform_scores': platform_scores,
            'review_distribution': self._aggregate_review_distribution(platform_data)
        }

    def _analyze_sentiment(self, platform_data: Dict) -> Dict:
        """Analyze sentiment across all reviews"""
        all_reviews = []

        # Collect all reviews from all platforms
        for platform, data in platform_data.items():
            if data.get('business_found') or data.get('profile_found'):
                reviews = data.get('recent_reviews', [])
                all_reviews.extend(reviews)

        if not all_reviews:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_breakdown': {'positive': 0, 'neutral': 0, 'negative': 0},
                'confidence': 'low'
            }

        # Count sentiments
        positive_count = sum(1 for review in all_reviews if review.get('sentiment') == 'positive')
        negative_count = sum(1 for review in all_reviews if review.get('sentiment') == 'negative')
        neutral_count = len(all_reviews) - positive_count - negative_count

        total_reviews = len(all_reviews)
        positive_pct = (positive_count / total_reviews) * 100
        negative_pct = (negative_count / total_reviews) * 100
        neutral_pct = (neutral_count / total_reviews) * 100

        # Determine overall sentiment
        if positive_pct > 60:
            overall_sentiment = 'positive'
        elif negative_pct > 30:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_breakdown': {
                'positive': round(positive_pct, 1),
                'neutral': round(neutral_pct, 1),
                'negative': round(negative_pct, 1)
            },
            'sentiment_score': round((positive_pct - negative_pct) / 100, 2),
            'total_reviews_analyzed': total_reviews,
            'confidence': 'high' if total_reviews > 10 else 'medium' if total_reviews > 5 else 'low'
        }

    def _generate_recommendations(self, platform_data: Dict, summary: Dict) -> List[str]:
        """Generate reputation management recommendations"""
        recommendations = []

        overall_rating = summary.get('overall_rating', 0)
        total_reviews = summary.get('total_reviews', 0)
        platforms_found = summary.get('platforms_found', 0)
        reputation_score = summary.get('reputation_score', 0)

        # Platform presence recommendations
        missing_platforms = []
        important_platforms = ['google_reviews', 'trustpilot']
        for platform in important_platforms:
            data = platform_data.get(platform, {})
            if not (data.get('business_found') or data.get('profile_found')):
                platform_name = platform.replace('_', ' ').title()
                missing_platforms.append(platform_name)

        if missing_platforms:
            recommendations.append(f"Create business profile on {missing_platforms[0]}")

        # Review volume recommendations
        if total_reviews < 10:
            recommendations.append("Implement review generation strategy - aim for 10+ reviews minimum")
        elif total_reviews < 50:
            recommendations.append("Continue building review volume - target 50+ reviews for strong credibility")

        # Rating improvement recommendations
        if overall_rating < 4.0:
            recommendations.append("Focus on improving customer experience to increase average rating")
        elif overall_rating < 4.5:
            recommendations.append("Address service gaps to achieve excellent rating (4.5+ stars)")

        # Response management recommendations
        low_response_platforms = []
        for platform, data in platform_data.items():
            if data.get('business_found') or data.get('profile_found'):
                response_rate = data.get('response_rate', '0%')
                rate_number = int(response_rate.replace('%', ''))
                if rate_number < 80:
                    platform_name = platform.replace('_', ' ').title()
                    low_response_platforms.append(platform_name)

        if low_response_platforms:
            recommendations.append(f"Improve response rate on {low_response_platforms[0]} (aim for 90%+)")

        # Reputation score specific recommendations
        if reputation_score < 50:
            recommendations.append("Develop comprehensive reputation management strategy")

        return recommendations[:5]  # Return top 5 recommendations

    def _identify_risk_factors(self, platform_data: Dict, summary: Dict) -> List[str]:
        """Identify reputation risk factors"""
        risks = []

        overall_rating = summary.get('overall_rating', 0)
        total_reviews = summary.get('total_reviews', 0)

        # Low rating risk
        if overall_rating < 3.5 and total_reviews > 5:
            risks.append("Below-average ratings may significantly impact customer acquisition")

        # Insufficient reviews risk
        if total_reviews < 5:
            risks.append("Very low review volume limits customer trust and decision-making")

        # Platform absence risk
        google_data = platform_data.get('google_reviews', {})
        if not google_data.get('business_found'):
            risks.append("Missing Google My Business listing severely limits local discoverability")

        # Unclaimed listings risk
        unclaimed_platforms = []
        for platform, data in platform_data.items():
            if data.get('business_found') or data.get('profile_found'):
                if not (data.get('claimed_listing') or data.get('claimed_profile')):
                    platform_name = platform.replace('_', ' ').title()
                    unclaimed_platforms.append(platform_name)

        if unclaimed_platforms:
            risks.append(f"Unclaimed listings on {unclaimed_platforms[0]} may contain inaccurate information")

        # High negative sentiment risk
        # This would be calculated from sentiment analysis
        # For now, simulate based on rating
        if overall_rating < 3.0:
            risks.append("High negative sentiment requires immediate customer service improvements")

        return risks[:4]  # Return top 4 risks

    # Helper methods for generating realistic data
    def _has_listing_probability(self, company_name: str, platform: str, probability: float) -> bool:
        """Determine if company likely has listing on platform"""
        hash_val = hash(f"{company_name}_{platform}")
        return (hash_val % 100) < (probability * 100)

    def _generate_review_count(self, platform: str) -> int:
        """Generate realistic review count for platform"""
        import random

        ranges = {
            'google': (5, 200),  # Google reviews
            'trustpilot': (10, 500),  # Trustpilot reviews
            'yelp': (3, 150),  # Yelp reviews
            'bbb': (0, 20)  # BBB complaints/reviews
        }

        min_val, max_val = ranges.get(platform, (5, 50))
        # Use weighted random that favors smaller numbers (more realistic)
        return int(min_val + (max_val - min_val) * (random.random() ** 1.5))

    def _generate_rating(self, platform: str) -> float:
        """Generate realistic rating for platform"""
        import random

        # Most businesses have ratings between 3.5-4.5
        base_rating = 3.5 + random.random() * 1.0

        # Platform-specific adjustments
        if platform == 'trustpilot':
            base_rating += 0.1  # Trustpilot tends slightly higher
        elif platform == 'yelp':
            base_rating -= 0.1  # Yelp tends slightly lower

        return round(max(1.0, min(5.0, base_rating)), 1)

    def _generate_bbb_rating(self) -> str:
        """Generate BBB letter grade rating"""
        import random
        ratings = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']
        # Weight toward better ratings (most businesses have decent BBB ratings)
        weights = [20, 15, 12, 10, 8, 6, 5, 4, 3, 2, 2, 1]
        return random.choices(ratings, weights=weights)[0]

    def _generate_rating_distribution(self, total_reviews: int, avg_rating: float) -> Dict:
        """Generate realistic star rating distribution"""
        if total_reviews == 0:
            return {'5_star': 0, '4_star': 0, '3_star': 0, '2_star': 0, '1_star': 0}

        # Generate distribution based on average rating
        # Higher avg_rating means more 5-star reviews
        five_star_pct = max(0.2, (avg_rating - 2.5) / 2.5 * 0.6)
        one_star_pct = max(0.05, (5 - avg_rating) / 2.5 * 0.25)

        # Distribute remaining percentage
        remaining = 1 - five_star_pct - one_star_pct
        four_star_pct = remaining * 0.4
        three_star_pct = remaining * 0.35
        two_star_pct = remaining * 0.25

        return {
            '5_star': int(total_reviews * five_star_pct),
            '4_star': int(total_reviews * four_star_pct),
            '3_star': int(total_reviews * three_star_pct),
            '2_star': int(total_reviews * two_star_pct),
            '1_star': int(total_reviews * one_star_pct)
        }

    def _generate_sample_reviews(self, platform: str, company_name: str, count: int) -> List[Dict]:
        """Generate sample reviews for platform"""
        reviews = []

        review_templates = {
            'positive': [
                f"Excellent service from {company_name}! Highly recommend.",
                f"Great experience with {company_name}. Professional and reliable.",
                f"Outstanding customer service at {company_name}. Will use again!"
            ],
            'neutral': [
                f"Decent experience with {company_name}. Average service.",
                f"Okay service from {company_name}. Nothing special but acceptable.",
                f"Mixed experience with {company_name}. Some good, some not so good."
            ],
            'negative': [
                f"Poor service from {company_name}. Would not recommend.",
                f"Disappointing experience with {company_name}. Expected better.",
                f"Had issues with {company_name}. Customer service needs work."
            ]
        }

        sentiments = ['positive', 'positive', 'positive', 'neutral', 'negative']  # Mostly positive

        for i in range(count):
            sentiment = sentiments[i % len(sentiments)]
            rating = {'positive': 5, 'neutral': 3, 'negative': 2}[sentiment]

            review = {
                'rating': rating,
                'text': review_templates[sentiment][i % len(review_templates[sentiment])],
                'sentiment': sentiment,
                'date': f"{7 + (i * 14)} days ago",
                'reviewer_name': f"Customer {chr(65 + i)}",  # Customer A, B, C
                'verified': i < 2,  # First 2 are verified
                'helpful_votes': max(0, 5 - i * 2)
            }

            # Add platform-specific fields
            if platform == 'trustpilot':
                review['verified_purchase'] = i == 0
                review['review_source'] = 'trustpilot'
            elif platform == 'yelp':
                review['check_in'] = i == 0
                review['photos'] = i == 0

            reviews.append(review)

        return reviews

    def _generate_price_range(self) -> str:
        """Generate Yelp price range"""
        import random
        return random.choice(['$', '$$', '$$$', '$$$$'])

        def _calculate_years_in_business(self) -> int:
            """Calculate realistic years in business"""
            import random
            return random.randint(1, 25)

        def _calculate_trust_level(self, trust_score: float) -> str:
            """Calculate Trustpilot trust level"""
            if trust_score >= 4.5:
                return 'Excellent'
            elif trust_score >= 4.0:
                return 'Great'
            elif trust_score >= 3.5:
                return 'Good'
            elif trust_score >= 2.5:
                return 'Average'
            else:
                return 'Poor'

        def _calculate_reputation_score(self, overall_rating: float, total_reviews: int, platforms_found: int) -> float:
            """Calculate overall reputation score (0-100)"""
            if overall_rating == 0:
                return 0

            # Base score from rating (0-70 points)
            rating_score = (overall_rating / 5.0) * 70

            # Volume bonus (0-20 points)
            if total_reviews > 100:
                volume_score = 20
            elif total_reviews > 50:
                volume_score = 15
            elif total_reviews > 20:
                volume_score = 10
            elif total_reviews > 5:
                volume_score = 5
            else:
                volume_score = 0

            # Platform diversity bonus (0-10 points)
            diversity_score = min(platforms_found * 2.5, 10)

            total_score = rating_score + volume_score + diversity_score
            return min(100, total_score)

        def _get_reputation_level(self, reputation_score: float) -> str:
            """Get reputation level description"""
            if reputation_score >= 80:
                return 'Excellent'
            elif reputation_score >= 65:
                return 'Good'
            elif reputation_score >= 50:
                return 'Average'
            elif reputation_score >= 35:
                return 'Below Average'
            else:
                return 'Poor'

        def _aggregate_review_distribution(self, platform_data: Dict) -> Dict:
            """Aggregate rating distribution across all platforms"""
            total_distribution = {'5_star': 0, '4_star': 0, '3_star': 0, '2_star': 0, '1_star': 0}

            for platform, data in platform_data.items():
                if data.get('business_found') or data.get('profile_found'):
                    distribution = data.get('rating_distribution', {})
                    for star_rating, count in distribution.items():
                        if star_rating in total_distribution:
                            total_distribution[star_rating] += count

            return total_distribution

        def _guess_business_category(self, company_name: str) -> str:
            """Guess business category from company name"""
            categories = [
                'Business Services', 'Technology', 'Retail', 'Healthcare',
                'Education', 'Manufacturing', 'Consulting', 'Real Estate'
            ]
            return categories[hash(company_name) % len(categories)]