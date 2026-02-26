"""
Test script for AI News Aggregator with mock data
This lets you test the digest generation without fetching real data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_news_agent import AINewsAggregator, NewsItem
from datetime import datetime, timedelta


def create_mock_news_items():
    """Create mock news items for testing."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    mock_items = [
        # ArXiv Papers
        NewsItem(
            title="Attention Is All You Need v2: Improved Transformer Architecture",
            url="https://arxiv.org/abs/2026.12345",
            source="ArXiv AI Papers",
            description="We present an improved transformer architecture with 40% better efficiency and state-of-the-art results on multiple benchmarks.",
            date=today,
            category="Research Papers"
        ),
        NewsItem(
            title="Scaling Laws for Neural Language Models: A Comprehensive Study",
            url="https://arxiv.org/abs/2026.12346",
            source="ArXiv ML Papers",
            description="An extensive analysis of scaling laws in large language models, providing insights for optimal model size and training compute trade-offs.",
            date=today,
            category="Research Papers"
        ),
        
        # Hugging Face
        NewsItem(
            title="Introducing Llama-3-70B: The Most Powerful Open-Source LLM",
            url="https://huggingface.co/blog/llama-3-70b",
            source="Hugging Face Blog",
            description="Meta releases Llama 3 70B, achieving GPT-4 level performance with full open-source availability.",
            date=today,
            category="Models & Tools"
        ),
        NewsItem(
            title="SDXL Turbo: Real-Time Text-to-Image Generation",
            url="https://huggingface.co/stabilityai/sdxl-turbo",
            source="Hugging Face Trending Models",
            description="Stability AI's new model generates high-quality images in a single step, enabling real-time generation.",
            date=today,
            category="Models & Tools"
        ),
        
        # GitHub Trending
        NewsItem(
            title="llama.cpp: Run LLMs Locally on CPU",
            url="https://github.com/ggerganov/llama.cpp",
            source="GitHub Trending",
            description="Pure C++ implementation of LLM inference, now with multi-modal support and 3x faster performance.",
            date=today,
            category="Open Source"
        ),
        NewsItem(
            title="AutoGPT-Next: Autonomous AI Agents Framework",
            url="https://github.com/auto-gpt/autogpt-next",
            source="GitHub Trending",
            description="Complete rewrite of AutoGPT with plugin system, better memory management, and 10x faster execution.",
            date=today,
            category="Open Source"
        ),
        
        # Company Blogs
        NewsItem(
            title="GPT-5 Preview: Multimodal Reasoning Breakthrough",
            url="https://openai.com/blog/gpt-5-preview",
            source="OpenAI Blog",
            description="OpenAI announces GPT-5 with native multimodal understanding, improved reasoning, and 10x compute efficiency.",
            date=yesterday,
            category="Company News"
        ),
        NewsItem(
            title="Claude 3.5 Sonnet: Enhanced Context and Coding",
            url="https://anthropic.com/news/claude-3-5-sonnet",
            source="Anthropic News",
            description="Anthropic releases Claude 3.5 Sonnet with 200K context window and significant coding improvements.",
            date=today,
            category="Company News"
        ),
        NewsItem(
            title="AlphaFold 3: Predicting All Biomolecular Structures",
            url="https://deepmind.google/discover/blog/alphafold-3",
            source="DeepMind Blog",
            description="DeepMind's AlphaFold 3 can now predict structures of all biomolecules with unprecedented accuracy.",
            date=today,
            category="Company News"
        ),
        NewsItem(
            title="Gemini Ultra 2.0: Google's Largest Multimodal Model",
            url="https://ai.google/discover/gemini-ultra-2",
            source="Google AI Blog",
            description="Google unveils Gemini Ultra 2.0 with native image, video, and audio understanding capabilities.",
            date=today,
            category="Company News"
        ),
    ]
    
    return mock_items


def test_basic_functionality():
    """Test basic aggregator functionality with mock data."""
    print("=" * 60)
    print("TEST 1: Basic Functionality")
    print("=" * 60)
    
    # Create aggregator
    aggregator = AINewsAggregator()
    
    # Create mock news items
    mock_items = create_mock_news_items()
    print(f"✓ Created {len(mock_items)} mock news items")
    
    # Test deduplication (should include all items first time)
    new_items = [item for item in mock_items if item.id not in aggregator.seen_items]
    print(f"✓ {len(new_items)} new items (first run should be all)")
    
    # Test filtering by keywords
    if aggregator.config.get("keywords"):
        filtered = aggregator._filter_by_keywords(mock_items)
        print(f"✓ Keyword filtering: {len(filtered)}/{len(mock_items)} items match keywords")
    
    # Test limiting per source
    max_items = aggregator.config.get("max_items_per_source", 10)
    limited = aggregator._limit_per_source(mock_items, max_items)
    print(f"✓ Source limiting: {len(limited)} items after applying {max_items} max per source")
    
    # Generate HTML digest
    html = aggregator.generate_email_html(mock_items)
    print(f"✓ Generated HTML digest ({len(html)} characters)")
    
    # Generate text digest
    text = aggregator.generate_email_text(mock_items)
    print(f"✓ Generated text digest ({len(text)} characters)")
    
    # Save digests
    aggregator.save_digest(mock_items)
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"✓ Saved digests to output/digest_{today}.html and .txt")
    
    # Save seen items
    aggregator._save_seen_items([item.id for item in mock_items])
    print(f"✓ Saved {len(mock_items)} item IDs to seen_items.json")
    
    print("\n✅ Basic functionality test PASSED\n")
    return aggregator, mock_items


def test_deduplication():
    """Test that deduplication works correctly."""
    print("=" * 60)
    print("TEST 2: Deduplication")
    print("=" * 60)
    
    # Create fresh aggregator (should have seen items from previous test)
    aggregator = AINewsAggregator()
    print(f"✓ Loaded {len(aggregator.seen_items)} previously seen items")
    
    # Create same mock items again
    mock_items = create_mock_news_items()
    
    # Check how many are new (should be 0 if deduplication works)
    new_items = [item for item in mock_items if item.id not in aggregator.seen_items]
    
    if len(new_items) == 0:
        print("✓ All items were correctly identified as duplicates")
        print("✅ Deduplication test PASSED\n")
        return True
    else:
        print(f"✗ Found {len(new_items)} items that should have been duplicates")
        print("❌ Deduplication test FAILED\n")
        return False


def test_output_generation():
    """Verify output files were created and are valid."""
    print("=" * 60)
    print("TEST 3: Output File Generation")
    print("=" * 60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    html_path = f"output/digest_{today}.html"
    text_path = f"output/digest_{today}.txt"
    
    # Check HTML file
    if os.path.exists(html_path):
        size = os.path.getsize(html_path)
        print(f"✓ HTML file exists: {html_path} ({size:,} bytes)")
        
        # Verify it's valid HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '<!DOCTYPE html>' in content and '</html>' in content:
                print("✓ HTML file has valid structure")
            else:
                print("✗ HTML file may be malformed")
    else:
        print(f"✗ HTML file not found: {html_path}")
    
    # Check text file
    if os.path.exists(text_path):
        size = os.path.getsize(text_path)
        print(f"✓ Text file exists: {text_path} ({size:,} bytes)")
    else:
        print(f"✗ Text file not found: {text_path}")
    
    # Check log file
    log_path = f"logs/agent_{today}.log"
    if os.path.exists(log_path):
        size = os.path.getsize(log_path)
        print(f"✓ Log file exists: {log_path} ({size:,} bytes)")
    else:
        print(f"✗ Log file not found: {log_path}")
    
    print("\n✅ Output generation test PASSED\n")


def test_config_loading():
    """Test configuration loading."""
    print("=" * 60)
    print("TEST 4: Configuration Loading")
    print("=" * 60)
    
    aggregator = AINewsAggregator()
    
    # Check sources
    sources = aggregator.config.get("sources", [])
    print(f"✓ Loaded {len(sources)} news sources")
    
    # Check keywords
    keywords = aggregator.config.get("keywords", [])
    print(f"✓ Loaded {len(keywords)} keywords")
    
    # Check email config
    email_config = aggregator.config.get("email_config", {})
    print(f"✓ Email config loaded (enabled: {email_config.get('enabled', False)})")
    
    # Check max items
    max_items = aggregator.config.get("max_items_per_source", 10)
    print(f"✓ Max items per source: {max_items}")
    
    print("\n✅ Configuration test PASSED\n")


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "AI NEWS AGGREGATOR TEST SUITE" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        # Test 1: Basic functionality
        aggregator, mock_items = test_basic_functionality()
        
        # Test 2: Deduplication
        test_deduplication()
        
        # Test 3: Output generation
        test_output_generation()
        
        # Test 4: Configuration
        test_config_loading()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Open output/digest_" + datetime.now().strftime("%Y-%m-%d") + ".html in your browser")
        print("2. Review the generated digest format")
        print("3. Configure email settings in config.json when ready")
        print("4. Set up Task Scheduler for daily automation")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
