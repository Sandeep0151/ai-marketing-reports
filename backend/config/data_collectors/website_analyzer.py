# data_collectors/website_analyzer.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import json
import re
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class WebsiteAnalyzer:
    """Comprehensive website analysis"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MarketingBot/1.0; +https://marketingbot.com/bot)'
        })
        self.timeout = 15

    def analyze_website(self, url: str) -> Dict:
        """Perform comprehensive website analysis"""
        try:
            logger.info(f"Starting website analysis for {url}")

            # Basic page analysis
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')

            analysis = {
                'url': url,
                'final_url': response.url,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),

                # Basic page info
                'title': self._get_title(soup),
                'description': self._get_meta_description(soup),
                'keywords': self._get_meta_keywords(soup),
                'canonical_url': self._get_canonical_url(soup),

                # Technical analysis
                'has_ssl': url.startswith('https://'),
                'has_robots_txt': self._check_robots_txt(url),
                'has_sitemap': self._check_sitemap(url),
                'has_favicon': self._check_favicon(soup, url),

                # Content analysis
                'word_count': self._get_word_count(soup),
                'heading_structure': self._analyze_headings(soup),
                'images': self._analyze_images(soup, url),
                'links': self._analyze_links(soup, url),

                # SEO elements
                'meta_tags': self._get_all_meta_tags(soup),
                'structured_data': self._detect_structured_data(soup),
                'social_tags': self._get_social_meta_tags(soup),

                # Performance indicators
                'page_size': len(response.content),
                'external_resources': self._count_external_resources(soup),

                # Contact and business info
                'contact_info': self._extract_contact_info(soup),
                'social_links': self._find_social_links(soup),
                'company_name': self._extract_company_name(soup),

                # Technology detection
                'technologies': self._detect_technologies(response, soup),

                # Accessibility
                'accessibility_features': self._check_accessibility(soup),

                # Mobile optimization
                'mobile_optimized': self._check_mobile_optimization(soup),

                'analysis_timestamp': time.time()
            }

            logger.info(f"Website analysis completed for {url}")
            return analysis

        except requests.RequestException as e:
            logger.error(f"Request error analyzing {url}: {e}")
            return {'error': f"Request error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error analyzing website {url}: {e}")
            return {'error': str(e)}

    def _get_title(self, soup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ''

    def _get_meta_description(self, soup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': re.compile(r'^description$', re.I)})
        return meta_desc.get('content', '').strip() if meta_desc else ''

    def _get_meta_keywords(self, soup) -> str:
        """Extract meta keywords"""
        meta_keywords = soup.find('meta', attrs={'name': re.compile(r'^keywords$', re.I)})
        return meta_keywords.get('content', '').strip() if meta_keywords else ''

    def _get_canonical_url(self, soup) -> str:
        """Extract canonical URL"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        return canonical.get('href', '') if canonical else ''

    def _check_robots_txt(self, url: str) -> bool:
        """Check if robots.txt exists"""
        try:
            robots_url = urljoin(url, '/robots.txt')
            response = self.session.head(robots_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def _check_sitemap(self, url: str) -> bool:
        """Check if sitemap.xml exists"""
        try:
            sitemap_url = urljoin(url, '/sitemap.xml')
            response = self.session.head(sitemap_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def _check_favicon(self, soup, url: str) -> bool:
        """Check if favicon exists"""
        # Check for favicon link in HTML
        favicon_link = soup.find('link', attrs={'rel': re.compile(r'icon', re.I)})
        if favicon_link:
            return True

        # Check default favicon location
        try:
            favicon_url = urljoin(url, '/favicon.ico')
            response = self.session.head(favicon_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def _get_word_count(self, soup) -> int:
        """Count words in page content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        words = text.split()
        return len(words)

    def _analyze_headings(self, soup) -> Dict:
        """Analyze heading structure"""
        headings = {}
        for i in range(1, 7):
            tag_name = f'h{i}'
            heading_tags = soup.find_all(tag_name)
            headings[tag_name] = [h.get_text().strip() for h in heading_tags]

        return headings

    def _analyze_images(self, soup, base_url: str) -> Dict:
        """Analyze images on the page"""
        images = soup.find_all('img')

        image_analysis = {
            'total_count': len(images),
            'with_alt_text': 0,
            'without_alt_text': 0,
            'external_images': 0,
            'images_info': []
        }

        for img in images[:20]:  # Analyze first 20 images
            alt_text = img.get('alt', '').strip()
            src = img.get('src', '')

            if alt_text:
                image_analysis['with_alt_text'] += 1
            else:
                image_analysis['without_alt_text'] += 1

            # Check if external image
            if src.startswith(('http://', 'https://')) and base_url not in src:
                image_analysis['external_images'] += 1

            image_analysis['images_info'].append({
                'src': src[:100],  # Truncate long URLs
                'alt': alt_text,
                'has_alt': bool(alt_text)
            })

        return image_analysis

    def _analyze_links(self, soup, base_url: str) -> Dict:
        """Analyze links on the page"""
        links = soup.find_all('a', href=True)
        parsed_base = urlparse(base_url)

        link_analysis = {
            'total_count': len(links),
            'internal_links': 0,
            'external_links': 0,
            'email_links': 0,
            'phone_links': 0,
            'social_links': 0,
            'external_domains': set()
        }

        social_domains = [
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'tiktok.com', 'snapchat.com', 'pinterest.com'
        ]

        for link in links:
            href = link.get('href', '').strip()

            if href.startswith('mailto:'):
                link_analysis['email_links'] += 1
            elif href.startswith('tel:'):
                link_analysis['phone_links'] += 1
            elif href.startswith(('http://', 'https://')):
                parsed_href = urlparse(href)
                if parsed_href.netloc == parsed_base.netloc:
                    link_analysis['internal_links'] += 1
                else:
                    link_analysis['external_links'] += 1
                    link_analysis['external_domains'].add(parsed_href.netloc)

                    # Check if social media link
                    if any(social in parsed_href.netloc for social in social_domains):
                        link_analysis['social_links'] += 1
            else:
                # Relative links are internal
                link_analysis['internal_links'] += 1

        link_analysis['external_domains'] = list(link_analysis['external_domains'])[:10]
        return link_analysis

    def _get_all_meta_tags(self, soup) -> List[Dict]:
        """Get all meta tags"""
        meta_tags = []
        for meta in soup.find_all('meta'):
            tag_info = {'tag': str(meta)}

            if meta.get('name'):
                tag_info['name'] = meta.get('name')
            if meta.get('property'):
                tag_info['property'] = meta.get('property')
            if meta.get('content'):
                tag_info['content'] = meta.get('content')

            meta_tags.append(tag_info)

        return meta_tags

    def _detect_structured_data(self, soup) -> List[str]:
        """Detect structured data (JSON-LD, microdata, etc.)"""
        structured_data = []

        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    structured_data.append(f"JSON-LD: {data['@type']}")
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and '@type' in item:
                            structured_data.append(f"JSON-LD: {item['@type']}")
            except:
                pass

        # Microdata
        microdata_items = soup.find_all(attrs={'itemtype': True})
        for item in microdata_items:
            itemtype = item.get('itemtype', '')
            if itemtype:
                structured_data.append(f"Microdata: {itemtype.split('/')[-1]}")

        return list(set(structured_data))

    def _get_social_meta_tags(self, soup) -> Dict:
        """Extract social media meta tags (Open Graph, Twitter Cards)"""
        social_tags = {
            'open_graph': {},
            'twitter': {},
            'other': {}
        }

        for meta in soup.find_all('meta'):
            property_attr = meta.get('property', '')
            name_attr = meta.get('name', '')
            content = meta.get('content', '')

            if property_attr.startswith('og:'):
                social_tags['open_graph'][property_attr] = content
            elif name_attr.startswith('twitter:'):
                social_tags['twitter'][name_attr] = content
            elif any(attr in [property_attr, name_attr] for attr in ['article:', 'fb:', 'music:', 'video:']):
                social_tags['other'][property_attr or name_attr] = content

        return social_tags

    def _count_external_resources(self, soup) -> Dict:
        """Count external resources"""
        resources = {
            'stylesheets': 0,
            'scripts': 0,
            'fonts': 0,
            'images': 0
        }

        # External stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href.startswith(('http://', 'https://')) or href.startswith('//'):
                resources['stylesheets'] += 1

        # External scripts
        for script in soup.find_all('script', src=True):
            src = script.get('src', '')
            if src.startswith(('http://', 'https://')) or src.startswith('//'):
                resources['scripts'] += 1

        return resources

    def _extract_contact_info(self, soup) -> Dict:
        """Extract contact information"""
        text = soup.get_text().lower()

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)

        # Phone pattern (basic)
        phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        phones = re.findall(phone_pattern, text)

        return {
            'has_email': bool(emails) or 'email' in text or '@' in text,
            'has_phone': bool(phones) or any(keyword in text for keyword in ['phone', 'call', 'tel']),
            'has_address': any(keyword in text for keyword in ['address', 'location', 'street', 'city']),
            'emails_found': emails[:3],  # First 3 emails
            'phones_found': phones[:3],  # First 3 phones
        }

    def _find_social_links(self, soup) -> Dict:
        """Find social media links"""
        social_platforms = {
            'facebook': ['facebook.com', 'fb.com'],
            'twitter': ['twitter.com', 'x.com'],
            'instagram': ['instagram.com'],
            'linkedin': ['linkedin.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'tiktok': ['tiktok.com'],
            'pinterest': ['pinterest.com'],
            'snapchat': ['snapchat.com'],
        }

        social_links = {}

        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            for platform, domains in social_platforms.items():
                if any(domain in href for domain in domains) and platform not in social_links:
                    social_links[platform] = link.get('href')

        return social_links

    def _extract_company_name(self, soup) -> str:
        """Try to extract company name"""
        # Try different sources
        sources = [
            soup.find('meta', attrs={'property': 'og:site_name'}),
            soup.find('meta', attrs={'name': 'application-name'}),
            soup.find('title'),
        ]

        for source in sources:
            if source and source.get('content'):
                return source.get('content').strip()
            elif source and source.text:
                # For title tag, try to extract company name
                title = source.text.strip()
                # Remove common separators and take the part that might be company name
                parts = re.split(r'[|\-–—]', title)
                if len(parts) > 1:
                    return parts[-1].strip()
                return title

        return ''

    def _detect_technologies(self, response, soup) -> List[str]:
        """Detect technologies used"""
        technologies = []

        # Check headers
        server = response.headers.get('server', '').lower()
        if 'nginx' in server:
            technologies.append('Nginx')
        elif 'apache' in server:
            technologies.append('Apache')

        # Check for common frameworks/libraries
        page_text = str(soup).lower()

        tech_patterns = {
            'WordPress': ['wp-content', 'wp-includes'],
            'Shopify': ['shopify', 'cdn.shopify.com'],
            'React': ['react', '__reactInternalInstance'],
            'jQuery': ['jquery'],
            'Bootstrap': ['bootstrap'],
            'Google Analytics': ['google-analytics.com', 'gtag'],
            'Google Tag Manager': ['googletagmanager.com'],
        }

        for tech, patterns in tech_patterns.items():
            if any(pattern in page_text for pattern in patterns):
                technologies.append(tech)

        return technologies

    def _check_accessibility(self, soup) -> Dict:
        """Check basic accessibility features"""
        accessibility = {
            'has_lang_attribute': bool(soup.find('html', lang=True)),
            'has_skip_links': bool(soup.find('a', href='#main') or soup.find('a', href='#content')),
            'images_with_alt': 0,
            'images_without_alt': 0,
            'has_aria_labels': bool(soup.find(attrs={'aria-label': True})),
        }

        # Check images
        for img in soup.find_all('img'):
            if img.get('alt') is not None:
                accessibility['images_with_alt'] += 1
            else:
                accessibility['images_without_alt'] += 1

        return accessibility

    def _check_mobile_optimization(self, soup) -> Dict:
        """Check mobile optimization features"""
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})

        mobile_features = {
            'has_viewport_meta': bool(viewport_meta),
            'viewport_content': viewport_meta.get('content', '') if viewport_meta else '',
            'has_responsive_images': bool(soup.find('img', attrs={'srcset': True})),
            'has_media_queries': False,  # Would need to parse CSS files
        }

        return mobile_features