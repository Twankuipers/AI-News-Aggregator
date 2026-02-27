"""
AI News Aggregator Agent
Fetches the latest AI models, papers, and news from multiple sources and generates email digest.
Includes email and Slack notification support.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Any
import hashlib
import requests
from bs4 import BeautifulSoup
import feedparser
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NewsItem:
    """Represents a single news item from any source."""
    
    def __init__(self, title: str, url: str, source: str, description: str = "", 
                 date: str = "", category: str = ""):
        self.title = title
        self.url = url
        self.source = source
        self.description = description
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.category = category
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID based on URL and title."""
        unique_str = f"{self.url}{self.title}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "description": self.description,
            "date": self.date,
            "category": self.category
        }


class AINewsAggregator:
    """Main aggregator class that fetches, deduplicates, and formats AI news."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.seen_items_path = Path("data/seen_items.json")
        self.seen_items = self._load_seen_items()
        self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file and override with local config and environment variables."""
        # Load base config
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found: {self.config_path}")
            config = self._default_config()
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing config file: {e}")
            config = self._default_config()
        
        # Override with local config file if it exists (for local dev with secrets)
        local_config_path = "config.local.json"
        if os.path.exists(local_config_path):
            try:
                with open(local_config_path, 'r', encoding='utf-8') as f:
                    local_config = json.load(f)
                    # Deep merge local config into base config
                    config = self._deep_merge(config, local_config)
                    logging.info("Loaded local config overrides from config.local.json")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logging.warning(f"Error loading local config: {e}")
        
        # Override with environment variables (for GitHub Actions secrets)
        config = self._apply_env_overrides(config)
        return config
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge override dict into base dict."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Override config with environment variables if they exist (for GitHub Actions)."""
        # Email configuration
        if os.getenv('EMAIL_ENABLED'):
            if 'email_config' not in config:
                config['email_config'] = {}
            config['email_config']['enabled'] = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
            
            if os.getenv('EMAIL_METHOD'):
                config['email_config']['method'] = os.getenv('EMAIL_METHOD')
            
            if os.getenv('EMAIL_SMTP_SERVER'):
                if 'smtp' not in config['email_config']:
                    config['email_config']['smtp'] = {}
                config['email_config']['smtp']['server'] = os.getenv('EMAIL_SMTP_SERVER')
                config['email_config']['smtp']['port'] = int(os.getenv('EMAIL_SMTP_PORT', '587'))
                config['email_config']['smtp']['username'] = os.getenv('EMAIL_USER', '')
                config['email_config']['smtp']['password'] = os.getenv('EMAIL_PASSWORD', '')
            
            if os.getenv('EMAIL_FROM'):
                config['email_config']['from'] = os.getenv('EMAIL_FROM')
            if os.getenv('EMAIL_TO'):
                config['email_config']['to'] = os.getenv('EMAIL_TO')
            
            if os.getenv('SENDGRID_API_KEY'):
                if 'sendgrid' not in config['email_config']:
                    config['email_config']['sendgrid'] = {}
                config['email_config']['sendgrid']['api_key'] = os.getenv('SENDGRID_API_KEY')
            
            if os.getenv('MAILGUN_API_KEY'):
                if 'mailgun' not in config['email_config']:
                    config['email_config']['mailgun'] = {}
                config['email_config']['mailgun']['api_key'] = os.getenv('MAILGUN_API_KEY')
                config['email_config']['mailgun']['domain'] = os.getenv('MAILGUN_DOMAIN', '')
        
        # Slack configuration
        if os.getenv('SLACK_ENABLED'):
            if 'slack_config' not in config:
                config['slack_config'] = {}
            config['slack_config']['enabled'] = os.getenv('SLACK_ENABLED', 'false').lower() == 'true'
            
            if os.getenv('SLACK_WEBHOOK_URL'):
                config['slack_config']['webhook_url'] = os.getenv('SLACK_WEBHOOK_URL')
        
        return config
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "sources": [],
            "keywords": [],
            "max_items_per_source": 10,
            "email_config": {},
            "slack_config": {},
            "schedule": "daily"
        }
    
    def _load_seen_items(self) -> set:
        """Load previously seen item IDs from JSON file."""
        if self.seen_items_path.exists():
            try:
                with open(self.seen_items_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get("seen_ids", []))
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Error loading seen items: {e}")
        return set()
    
    def _save_seen_items(self, new_ids: List[str]):
        """Save seen item IDs to JSON file."""
        self.seen_items.update(new_ids)
        try:
            with open(self.seen_items_path, 'w', encoding='utf-8') as f:
                json.dump({"seen_ids": list(self.seen_items)}, f, indent=2)
        except IOError as e:
            logging.error(f"Error saving seen items: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"agent_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def fetch_arxiv_papers(self) -> List[NewsItem]:
        """Fetch latest AI/ML papers from ArXiv."""
        news_items = []
        categories = [
            ("cs.AI", "Artificial Intelligence"),
            ("cs.LG", "Machine Learning")
        ]
        
        for cat_id, cat_name in categories:
            try:
                logging.info(f"Fetching ArXiv {cat_name} papers...")
                url = f"https://arxiv.org/list/{cat_id}/recent"
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all paper entries
                paper_list = soup.find('dl')
                if not paper_list:
                    continue
                
                # Extract papers (dt contains arxiv ID, dd contains details)
                dts = paper_list.find_all('dt')
                dds = paper_list.find_all('dd')
                
                max_papers = self.config.get('max_items_per_source', 10)
                count = 0
                
                for dt, dd in zip(dts, dds):
                    if count >= max_papers:
                        break
                    
                    # Get arXiv ID
                    arxiv_link = dt.find('a', title='Abstract')
                    if not arxiv_link:
                        continue
                    
                    arxiv_id = arxiv_link.text.strip().replace('arXiv:', '')
                    paper_url = f"https://arxiv.org/abs/{arxiv_id}"
                    
                    # Get title and authors
                    title_div = dd.find('div', class_='list-title')
                    if title_div:
                        title = title_div.text.replace('Title:', '').strip()
                    else:
                        continue
                    
                    # Get abstract
                    abstract_div = dd.find('p', class_='mathjax')
                    description = abstract_div.text.strip() if abstract_div else ""
                    
                    # Limit description length
                    if len(description) > 300:
                        description = description[:300] + "..."
                    
                    news_item = NewsItem(
                        title=title,
                        url=paper_url,
                        source=f"ArXiv {cat_name}",
                        description=description,
                        date=datetime.now().strftime("%Y-%m-%d"),
                        category="Research Papers"
                    )
                    news_items.append(news_item)
                    count += 1
                
                logging.info(f"Fetched {count} papers from ArXiv {cat_name}")
                
            except Exception as e:
                logging.error(f"Error fetching ArXiv {cat_name} papers: {e}")
        
        return news_items
    
    def fetch_huggingface_updates(self) -> List[NewsItem]:
        """Fetch latest updates from Hugging Face blog and models."""
        news_items = []
        
        try:
            logging.info("Fetching Hugging Face blog...")
            url = "https://huggingface.co/blog"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find blog post articles - get more to find recent ones
            articles = soup.find_all('article', limit=15)
            
            for article in articles:
                try:
                    # Find title and link
                    title_link = article.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    if href.startswith('/'):
                        post_url = f"https://huggingface.co{href}"
                    else:
                        post_url = href
                    
                    # Try to extract date from article
                    post_date = datetime.now().strftime("%Y-%m-%d")
                    date_elem = article.find('time')
                    if date_elem:
                        date_str = date_elem.get_text(strip=True)
                        # Try to parse common date formats
                        for fmt in ["%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%d/%m/%Y"]:
                            try:
                                parsed_date = datetime.strptime(date_str, fmt)
                                post_date = parsed_date.strftime("%Y-%m-%d")
                                break
                            except:
                                continue
                    
                    # Filter to only recent posts (last 2 days)
                    try:
                        post_datetime = datetime.strptime(post_date, "%Y-%m-%d")
                        days_old = (datetime.now() - post_datetime).days
                        if days_old > 2:
                            continue
                    except:
                        pass
                    
                    # Find description
                    desc_elem = article.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    if len(description) > 250:
                        description = description[:250] + "..."
                    
                    news_item = NewsItem(
                        title=title,
                        url=post_url,
                        source="Hugging Face Blog",
                        description=description,
                        date=post_date,
                        category="Models & Tools"
                    )
                    news_items.append(news_item)
                    
                except Exception as e:
                    logging.warning(f"Error parsing HF blog article: {e}")
                    continue
            
            logging.info(f"Fetched {len(news_items)} Hugging Face blog posts")
            
        except Exception as e:
            logging.error(f"Error fetching Hugging Face blog: {e}")
        
        return news_items
    
    def fetch_github_trending(self) -> List[NewsItem]:
        """Fetch trending AI/ML repositories from GitHub."""
        news_items = []
        try:
            logging.info("Fetching GitHub trending repos...")
            url = "https://github.com/trending/python?since=daily"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find repository articles
            repos = soup.find_all('article', class_='Box-row', limit=10)
            
            ai_keywords = ['ai', 'ml', 'machine-learning', 'deep-learning', 'llm', 
                          'neural', 'transformers', 'gpt', 'model', 'learning']
            
            for repo in repos:
                try:
                    # Get repo name and link
                    h2 = repo.find('h2')
                    if not h2:
                        continue
                    
                    link = h2.find('a')
                    if not link:
                        continue
                    
                    repo_path = link.get('href', '').strip()
                    repo_url = f"https://github.com{repo_path}"
                    repo_name = repo_path.strip('/')
                    
                    # Get description
                    desc_elem = repo.find('p', class_='col-9')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Filter for AI/ML repos
                    search_text = f"{repo_name} {description}".lower()
                    if not any(keyword in search_text for keyword in ai_keywords):
                        continue
                    
                    # Get stars today
                    stars_elem = repo.find('span', class_='d-inline-block float-sm-right')
                    stars_today = stars_elem.get_text(strip=True) if stars_elem else "N/A"
                    
                    if description:
                        description = f"{description} | ⭐ {stars_today}"
                    
                    news_item = NewsItem(
                        title=repo_name,
                        url=repo_url,
                        source="GitHub Trending",
                        description=description,
                        date=datetime.now().strftime("%Y-%m-%d"),
                        category="Open Source"
                    )
                    news_items.append(news_item)
                    
                except Exception as e:
                    logging.warning(f"Error parsing GitHub repo: {e}")
                    continue
            
            logging.info(f"Fetched {len(news_items)} GitHub trending repos")
            
        except Exception as e:
            logging.error(f"Error fetching GitHub trending: {e}")
        
        return news_items
    
    def fetch_company_blogs(self) -> List[NewsItem]:
        """Fetch latest posts from AI company blogs."""
        news_items = []
        
        # OpenAI blog via RSS
        try:
            logging.info("Fetching OpenAI blog...")
            feed_url = "https://openai.com/blog/rss.xml"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    days_old = (datetime.now() - pub_date).days
                    
                    if days_old <= 30:
                        description = entry.get('summary', '')
                        description = re.sub('<[^<]+?>', '', description)
                        if len(description) > 250:
                            description = description[:250] + "..."
                        
                        news_item = NewsItem(
                            title=entry.title,
                            url=entry.link,
                            source="OpenAI Blog",
                            description=description,
                            date=pub_date.strftime("%Y-%m-%d"),
                            category="Company News"
                        )
                        news_items.append(news_item)
                except:
                    continue
            
            logging.info(f"Fetched {len(news_items)} OpenAI blog posts")
        except Exception as e:
            logging.error(f"Error fetching OpenAI blog: {e}")
        
        # Google AI Blog
        try:
            logging.info("Fetching Google blog...")
            url = "https://blog.google/innovation-and-ai/models-and-research/"
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for articles
            found = 0
            selectors = [
                soup.find_all('a', class_=lambda x: x and 'card' in x.lower()),
                soup.find_all('a', class_=lambda x: x and 'post' in x.lower()),
                soup.find_all('a', class_=lambda x: x and 'article' in x.lower()),
                soup.find_all('a')
            ]
            
            for selector_results in selectors:
                if not selector_results:
                    continue
                    
                for link in selector_results[:30]:
                    try:
                        href = link.get('href', '')
                        title = link.get_text(strip=True)
                        
                        # Skip if not a full URL or not Google blog
                        if not href or not title:
                            continue
                        if len(title) < 5 or len(title) > 350:
                            continue
                        if not href.startswith('https://blog.google'):
                            continue
                        if any(item.url == href for item in news_items):
                            continue
                        
                        news_item = NewsItem(
                            title=title,
                            url=href,
                            source="Google AI Blog",
                            category="Company News"
                        )
                        news_items.append(news_item)
                        found += 1
                        if found >= 3:
                            break
                    except:
                        continue
                        
                if found >= 3:
                    break
            
            logging.info(f"Fetched {found} Google blog posts")
        except Exception as e:
            logging.warning(f"Error fetching Google blog: {e}")
        
        # Anthropic News
        try:
            logging.info("Fetching Anthropic news...")
            url = "https://www.anthropic.com/news"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links
            found = 0
            for article in soup.find_all('a'):
                try:
                    href = article.get('href', '')
                    if not href or not href.startswith('http'):
                        continue
                    if 'anthropic.com' not in href:
                        continue
                    
                    title = article.get_text(strip=True)
                    if len(title) < 10 or len(title) > 200:
                        continue
                    
                    news_item = NewsItem(
                        title=title,
                        url=href,
                        source="Anthropic News",
                        category="Company News"
                    )
                    news_items.append(news_item)
                    found += 1
                    if found >= 3:
                        break
                except:
                    continue
            
            logging.info(f"Fetched {found} Anthropic news posts")
        except Exception as e:
            logging.warning(f"Error fetching Anthropic news: {e}")
        
        return news_items
    
    def aggregate_news(self) -> List[NewsItem]:
        """Aggregate news from all sources and deduplicate."""
        all_news = []
        
        # Fetch from all sources
        all_news.extend(self.fetch_arxiv_papers())
        all_news.extend(self.fetch_huggingface_updates())
        all_news.extend(self.fetch_github_trending())
        all_news.extend(self.fetch_company_blogs())
        
        # Deduplicate against seen items
        new_news = [item for item in all_news if item.id not in self.seen_items]
        
        # Save new item IDs
        if new_news:
            self._save_seen_items([item.id for item in new_news])
        
        # Apply keyword filtering if configured
        if self.config.get("keywords"):
            new_news = self._filter_by_keywords(new_news)
        
        # Limit items per source
        max_items = self.config.get("max_items_per_source", 10)
        new_news = self._limit_per_source(new_news, max_items)
        
        logging.info(f"Aggregated {len(new_news)} new items")
        return new_news
    
    def _filter_by_keywords(self, items: List[NewsItem]) -> List[NewsItem]:
        """Filter news items by configured keywords."""
        keywords = [kw.lower() for kw in self.config.get("keywords", [])]
        if not keywords:
            return items
        
        filtered = []
        for item in items:
            text = f"{item.title} {item.description}".lower()
            if any(kw in text for kw in keywords):
                filtered.append(item)
        
        return filtered
    
    def _limit_per_source(self, items: List[NewsItem], max_items: int) -> List[NewsItem]:
        """Limit number of items per source."""
        source_counts = {}
        limited_items = []
        
        for item in items:
            count = source_counts.get(item.source, 0)
            if count < max_items:
                limited_items.append(item)
                source_counts[item.source] = count + 1
        
        return limited_items
    
    def generate_email_html(self, news_items: List[NewsItem]) -> str:
        """Generate HTML email content from news items."""
        today = datetime.now().strftime("%B %d, %Y")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .news-item {{
            margin: 20px 0;
            padding: 15px;
            border-left: 3px solid #ecf0f1;
            background-color: #fafafa;
        }}
        .news-item h3 {{
            margin: 0 0 10px 0;
            color: #2980b9;
        }}
        .news-item a {{
            color: #3498db;
            text-decoration: none;
        }}
        .news-item a:hover {{
            text-decoration: underline;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .description {{
            margin: 10px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI News Digest - {today}</h1>
        <p>Your daily roundup of the latest in AI models, research papers, and industry news.</p>
"""
        
        # Group items by source
        sources = {}
        for item in news_items:
            if item.source not in sources:
                sources[item.source] = []
            sources[item.source].append(item)
        
        # Generate sections for each source
        for source, items in sources.items():
            html += f"\n        <h2>{source}</h2>\n"
            for item in items:
                html += f"""
        <div class="news-item">
            <h3><a href="{item.url}" target="_blank">{item.title}</a></h3>
            <div class="description">{item.description}</div>
            <div class="meta">
                📅 {item.date}
                {f'| 🏷️ {item.category}' if item.category else ''}
            </div>
        </div>
"""
        
        html += """
        <div class="footer">
            <p>Generated by AI News Aggregator Agent</p>
            <p>To customize your news sources or keywords, edit config.json</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_email_text(self, news_items: List[NewsItem]) -> str:
        """Generate plain text email content from news items."""
        today = datetime.now().strftime("%B %d, %Y")
        
        text = f"""
AI NEWS DIGEST - {today}
{'=' * 60}

Your daily roundup of the latest in AI models, research papers, and industry news.

"""
        
        # Group items by source
        sources = {}
        for item in news_items:
            if item.source not in sources:
                sources[item.source] = []
            sources[item.source].append(item)
        
        # Generate sections for each source
        for source, items in sources.items():
            text += f"\n{source.upper()}\n{'-' * 60}\n\n"
            for item in items:
                text += f"• {item.title}\n"
                text += f"  {item.url}\n"
                if item.description:
                    text += f"  {item.description}\n"
                text += f"  Date: {item.date}"
                if item.category:
                    text += f" | Category: {item.category}"
                text += "\n\n"
        
        text += f"""
{'=' * 60}
Generated by AI News Aggregator Agent
To customize your news sources or keywords, edit config.json
"""
        return text
    
    def save_digest(self, news_items: List[NewsItem]):
        """Save HTML and text digests to output folder."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Save HTML version
        html_content = self.generate_email_html(news_items)
        html_path = output_dir / f"digest_{today}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"HTML digest saved to {html_path}")
        
        # Save text version
        text_content = self.generate_email_text(news_items)
        text_path = output_dir / f"digest_{today}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        logging.info(f"Text digest saved to {text_path}")
        
        return html_content, text_content
    
    def send_notifications(self, news_items: List[NewsItem], html_content: str):
        """Send email and/or Slack notifications."""
        
        # Send email if configured
        if self.config.get("email_config", {}).get("enabled"):
            self._send_email(html_content, news_items)
        
        # Send Slack if configured
        if self.config.get("slack_config", {}).get("enabled"):
            self._send_slack_message(news_items)
    
    def _send_email(self, html_content: str, news_items: List[NewsItem]):
        """Send email digest."""
        email_config = self.config.get("email_config", {})
        method = email_config.get("method", "file")
        
        if method == "smtp":
            self._send_via_smtp(email_config, html_content, news_items)
        elif method == "api":
            self._send_via_api(email_config, html_content, news_items)
        else:
            logging.info("Email method not configured for sending")
    
    def _send_via_smtp(self, config: Dict, html_content: str, news_items: List[NewsItem]):
        """Send email via SMTP."""
        try:
            smtp_config = config.get("smtp", {})
            host = smtp_config.get("host")
            port = smtp_config.get("port", 587)
            username = smtp_config.get("username")
            password = smtp_config.get("password")
            from_email = smtp_config.get("from_email")
            to_email = smtp_config.get("to_email")
            
            if not all([host, username, password, from_email, to_email]):
                logging.error("SMTP config incomplete")
                return
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🤖 AI News Digest - {datetime.now().strftime('%B %d, %Y')}"
            msg["From"] = from_email
            msg["To"] = to_email
            
            # Add text and HTML parts
            text_content = self.generate_email_text(news_items)
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            server = smtplib.SMTP(host, port)
            server.starttls()
            server.login(username, password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
            
            logging.info(f"Email sent to {to_email}")
            print(f"✓ Email sent to {to_email}")
            
        except Exception as e:
            logging.error(f"Error sending email via SMTP: {e}")
    
    def _send_via_api(self, config: Dict, html_content: str, news_items: List[NewsItem]):
        """Send email via SendGrid or Mailgun API."""
        try:
            api_config = config.get("api", {})
            provider = api_config.get("provider", "sendgrid")
            api_key = api_config.get("api_key")
            from_email = api_config.get("from_email")
            to_email = api_config.get("to_email")
            
            if not all([api_key, from_email, to_email]):
                logging.error("API config incomplete")
                return
            
            if provider.lower() == "sendgrid":
                self._send_via_sendgrid(api_key, from_email, to_email, html_content, news_items)
            elif provider.lower() == "mailgun":
                self._send_via_mailgun(api_config, from_email, to_email, html_content, news_items)
            else:
                logging.error(f"Unknown API provider: {provider}")
        
        except Exception as e:
            logging.error(f"Error sending email via API: {e}")
    
    def _send_via_sendgrid(self, api_key: str, from_email: str, to_email: str, html_content: str, news_items: List[NewsItem]):
        """Send via SendGrid API."""
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            text_content = self.generate_email_text(news_items)
            
            data = {
                "personalizations": [{
                    "to": [{"email": to_email}]
                }],
                "from": {"email": from_email},
                "subject": f"🤖 AI News Digest - {datetime.now().strftime('%B %d, %Y')}",
                "content": [
                    {"type": "text/plain", "value": text_content},
                    {"type": "text/html", "value": html_content}
                ]
            }
            
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 202:
                logging.info(f"Email sent via SendGrid to {to_email}")
                print(f"✓ Email sent via SendGrid to {to_email}")
            else:
                logging.error(f"SendGrid error: {response.text}")
        
        except Exception as e:
            logging.error(f"Error sending via SendGrid: {e}")
    
    def _send_via_mailgun(self, config: Dict, from_email: str, to_email: str, html_content: str, news_items: List[NewsItem]):
        """Send via Mailgun API."""
        try:
            api_key = config.get("api_key")
            domain = config.get("domain")
            
            if not domain:
                logging.error("Mailgun domain not configured")
                return
            
            url = f"https://api.mailgun.net/v3/{domain}/messages"
            text_content = self.generate_email_text(news_items)
            
            data = {
                "from": from_email,
                "to": to_email,
                "subject": f"🤖 AI News Digest - {datetime.now().strftime('%B %d, %Y')}",
                "text": text_content,
                "html": html_content
            }
            
            response = requests.post(url, auth=("api", api_key), data=data)
            if response.status_code == 200:
                logging.info(f"Email sent via Mailgun to {to_email}")
                print(f"✓ Email sent via Mailgun to {to_email}")
            else:
                logging.error(f"Mailgun error: {response.text}")
        
        except Exception as e:
            logging.error(f"Error sending via Mailgun: {e}")
    
    def _send_slack_message(self, news_items: List[NewsItem]):
        """Send Slack notification."""
        try:
            slack_config = self.config.get("slack_config", {})
            webhook_url = slack_config.get("webhook_url")
            
            if not webhook_url:
                logging.error("Slack webhook URL not configured")
                return
            
            if not news_items:
                payload = {
                    "text": f"🤖 *AI News Digest* - {datetime.now().strftime('%B %d, %Y')}\n\nNo new items today.",
                    "mrkdwn": True
                }
                response = requests.post(webhook_url, json=payload)
                if response.status_code == 200:
                    logging.info("Slack notification sent (no new items)")
                    print("✓ Slack notification sent (no new items)")
                else:
                    logging.error(f"Slack error: {response.text}")
                return

            # Group items by source
            sources = {}
            for item in news_items:
                if item.source not in sources:
                    sources[item.source] = []
                sources[item.source].append(item)
            
            # Build message
            text = f"🤖 *AI News Digest* - {datetime.now().strftime('%B %d, %Y')}\n\n"
            
            for source, items in sources.items():
                text += f"*{source}*\n"
                for item in items[:3]:  # Show first 3 items per source
                    text += f"• <{item.url}|{item.title}>\n"
                text += "\n"
            
            payload = {
                "text": text,
                "mrkdwn": True
            }
            
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                logging.info("Slack notification sent")
                print("✓ Slack notification sent")
            else:
                logging.error(f"Slack error: {response.text}")
        
        except Exception as e:
            logging.error(f"Error sending Slack message: {e}")
    
    def run(self):
        """Main execution method."""
        logging.info("Starting AI News Aggregator...")
        
        try:
            # Aggregate news from all sources
            news_items = self.aggregate_news()
            
            if not news_items:
                logging.info("No new items found")
                print("No new AI news items found today.")
                if self.config.get("slack_config", {}).get("enabled"):
                    self._send_slack_message([])
                return
            
            # Generate and save digest
            html_content, text_content = self.save_digest(news_items)
            
            # Send notifications
            self.send_notifications(news_items, html_content)
            
            logging.info(f"Successfully processed {len(news_items)} news items")
            print(f"✓ Digest generated with {len(news_items)} news items")
            print(f"  Check output/digest_{datetime.now().strftime('%Y-%m-%d')}.html")
            
        except Exception as e:
            logging.error(f"Error during execution: {e}", exc_info=True)
            raise


def main():
    """Entry point for the script."""
    aggregator = AINewsAggregator()
    aggregator.run()


if __name__ == "__main__":
    main()
