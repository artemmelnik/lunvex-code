"""Demo script for LLM cache functionality."""

import os
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from lunvex_code.llm_cache import get_llm_cache, configure_llm_cache, save_llm_cache
from lunvex_code.llm import LunVexClient

console = Console()


def demo_basic_cache_operations():
    """Demo basic cache operations."""
    console.print(Panel("🧠 LLM Cache Demo - Basic Operations", style="bold blue"))
    
    # Configure cache with small TTL for demo
    configure_llm_cache(max_size=5, ttl_seconds=10)
    cache = get_llm_cache()
    
    console.print("\n1. Creating test messages...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    console.print("2. Simulating cache miss (first request)...")
    # Simulate cache miss
    result = cache.get(model="test-model", messages=messages)
    if result is None:
        console.print("   [yellow]Cache miss[/yellow] - would make API call")
    
    console.print("3. Adding response to cache...")
    # Simulate API response
    response_data = {
        "content": "The capital of France is Paris.",
        "usage": {"total_tokens": 20}
    }
    
    cache.put(
        model="test-model",
        messages=messages,
        response=response_data,
        token_count=20
    )
    
    console.print("4. Simulating cache hit (second request)...")
    result = cache.get(model="test-model", messages=messages)
    if result is not None:
        cached_response, from_cache = result
        if from_cache:
            console.print(f"   [green]Cache hit![/green] Response: {cached_response['content']}")
    
    # Show statistics
    stats = cache.get_stats()
    console.print(f"\n📊 Cache Statistics:")
    console.print(f"   Hits: {stats['hits']}")
    console.print(f"   Misses: {stats['misses']}")
    console.print(f"   Hit Rate: {stats['hit_rate']:.1%}")
    console.print(f"   Tokens Saved: {stats['tokens_saved']}")
    
    return cache


def demo_cache_ttl():
    """Demo TTL expiration."""
    console.print(Panel("⏰ LLM Cache Demo - TTL Expiration", style="bold blue"))
    
    # Configure cache with very short TTL
    configure_llm_cache(max_size=5, ttl_seconds=2)
    cache = get_llm_cache()
    cache.clear()  # Start fresh
    
    messages = [{"role": "user", "content": "What is 2+2?"}]
    response_data = {"content": "2+2=4", "usage": {"total_tokens": 10}}
    
    console.print("1. Adding response with 2-second TTL...")
    cache.put(
        model="test-model",
        messages=messages,
        response=response_data,
        token_count=10
    )
    
    console.print("2. Immediate cache hit...")
    result = cache.get(model="test-model", messages=messages)
    if result is not None:
        console.print("   [green]Cache hit[/green] (expected)")
    
    console.print("3. Waiting 3 seconds for TTL to expire...")
    time.sleep(3)
    
    console.print("4. Cache after TTL expiration...")
    result = cache.get(model="test-model", messages=messages)
    if result is None:
        console.print("   [yellow]Cache miss[/yellow] (TTL expired)")
    
    stats = cache.get_stats()
    console.print(f"\n📊 Final Statistics:")
    console.print(f"   Hits: {stats['hits']}")
    console.print(f"   Misses: {stats['misses']}")


def demo_cache_invalidation():
    """Demo cache invalidation."""
    console.print(Panel("🗑️ LLM Cache Demo - Invalidation", style="bold blue"))
    
    cache = get_llm_cache()
    cache.clear()
    
    console.print("1. Adding multiple cache entries...")
    for i in range(3):
        messages = [{"role": "user", "content": f"Question {i}"}]
        response_data = {"content": f"Answer {i}", "usage": {"total_tokens": 15}}
        
        cache.put(
            model=f"model-{i}",
            messages=messages,
            response=response_data,
            token_count=15
        )
    
    stats = cache.get_stats()
    console.print(f"   Cache size: {stats['current_size']} entries")
    
    console.print("2. Invalidating all entries...")
    count = cache.invalidate()
    console.print(f"   Invalidated {count} entries")
    
    stats = cache.get_stats()
    console.print(f"   Cache size after invalidation: {stats['current_size']} entries")
    
    console.print("3. Adding entries with specific patterns...")
    cache.put(
        model="weather-model",
        messages=[{"role": "user", "content": "Weather in London"}],
        response={"content": "Sunny, 20°C"},
        token_count=12
    )
    
    cache.put(
        model="math-model",
        messages=[{"role": "user", "content": "Calculate 5*5"}],
        response={"content": "25"},
        token_count=8
    )
    
    console.print("4. Invalidating by pattern 'weather-'...")
    count = cache.invalidate(pattern="weather-")
    console.print(f"   Invalidated {count} entries matching 'weather-'")
    
    stats = cache.get_stats()
    console.print(f"   Remaining cache size: {stats['current_size']} entries")


def demo_cache_statistics():
    """Demo cache statistics visualization."""
    console.print(Panel("📈 LLM Cache Demo - Statistics", style="bold blue"))
    
    cache = get_llm_cache()
    cache.clear()
    
    # Simulate some cache activity
    console.print("Simulating cache activity...")
    
    for i in range(10):
        messages = [{"role": "user", "content": f"Query {i % 3}"}]  # Only 3 unique queries
        response_data = {"content": f"Response for query {i % 3}", "usage": {"total_tokens": 20}}
        
        # Some will be cache hits, some misses
        result = cache.get(model="demo-model", messages=messages)
        
        if result is None:
            # Cache miss - add to cache
            cache.put(
                model="demo-model",
                messages=messages,
                response=response_data,
                token_count=20
            )
    
    # Get statistics
    stats = cache.get_stats()
    
    # Create a table
    table = Table(title="LLM Cache Statistics", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Cache Hits", str(stats['hits']))
    table.add_row("Cache Misses", str(stats['misses']))
    table.add_row("Total Requests", str(stats['total_requests']))
    table.add_row("Hit Rate", f"{stats['hit_rate']:.1%}")
    table.add_row("Tokens Saved", f"{stats['tokens_saved']:,}")
    table.add_row("Current Size", f"{stats['current_size']}/{stats['max_size']}")
    table.add_row("TTL", f"{stats['ttl_seconds']}s ({stats['ttl_seconds']/3600:.1f}h)")
    
    console.print(table)
    
    # Calculate cost savings (assuming $0.14 per 1M tokens for DeepSeek)
    tokens_per_dollar = 1_000_000 / 0.14
    dollars_saved = stats['tokens_saved'] / tokens_per_dollar
    
    console.print(f"\n💰 Estimated Cost Savings: ${dollars_saved:.4f}")
    console.print(f"   (Based on DeepSeek pricing: $0.14 per 1M tokens)")


def demo_cli_commands():
    """Demo CLI commands for cache management."""
    console.print(Panel("🖥️ LLM Cache Demo - CLI Commands", style="bold blue"))
    
    console.print("Available CLI commands:")
    console.print("\n1. [bold]Show LLM cache statistics[/bold]")
    console.print("   [dim]$ lunvex-code llm-cache-stats[/dim]")
    
    console.print("\n2. [bold]Clear LLM cache[/bold]")
    console.print("   [dim]$ lunvex-code clear-llm-cache[/dim]")
    
    console.print("\n3. [bold]Configure LLM cache[/bold]")
    console.print("   [dim]$ lunvex-code configure-llm-cache --max-size 200 --ttl-seconds 7200[/dim]")
    
    console.print("\n4. [bold]Environment variables for configuration[/bold]")
    console.print("   [dim]export LUNVEX_LLM_CACHE_MAX_SIZE=200[/dim]")
    console.print("   [dim]export LUNVEX_LLM_CACHE_TTL_SECONDS=7200[/dim]")
    
    console.print("\n5. [bold]Using cache tools from AI assistant[/bold]")
    console.print('   [dim]lunvex-code run "show llm cache statistics"[/dim]')
    console.print('   [dim]lunvex-code run "clear the llm cache"[/dim]')
    console.print('   [dim]lunvex-code run "configure llm cache with max size 500"[/dim]')


def demo_integration_with_llm_client():
    """Demo integration with LLM client."""
    console.print(Panel("🔗 LLM Cache Demo - Integration with LLM Client", style="bold blue"))
    
    console.print("The LLM cache is automatically integrated with LunVexClient:")
    console.print("\n1. [bold]Automatic caching[/bold]")
    console.print("   • All chat() calls use cache by default")
    console.print("   • Cache key includes: model, messages, tools, temperature, max_tokens")
    
    console.print("\n2. [bold]Cache control[/bold]")
    console.print("   • Disable cache: client.chat(..., use_cache=False)")
    console.print("   • Manual cache management via tools")
    
    console.print("\n3. [bold]Example workflow[/bold]")
    console.print("   ```python")
    console.print("   from lunvex_code.llm import LunVexClient")
    console.print("   ")
    console.print("   client = LunVexClient()")
    console.print("   messages = [{'role': 'user', 'content': 'Hello'}]")
    console.print("   ")
    console.print("   # First call - cache miss, makes API request")
    console.print("   response1 = client.chat(messages)")
    console.print("   ")
    console.print("   # Second call - cache hit, returns cached response")
    console.print("   response2 = client.chat(messages)  # Same parameters")
    console.print("   ```")
    
    console.print("\n4. [bold]Benefits[/bold]")
    console.print("   • Reduced API costs")
    console.print("   • Faster response times")
    console.print("   • Consistent responses for identical queries")
    console.print("   • Offline capability for cached queries")


def main():
    """Run all demos."""
    console.print(Panel("🚀 LLM Response Cache System Demo", style="bold green", width=80))
    console.print("This demo shows the new LLM response caching system for LunVex Code.")
    console.print("The system caches LLM responses to reduce API costs and improve performance.\n")
    
    # Run demos
    demo_basic_cache_operations()
    console.print("\n" + "="*80 + "\n")
    
    demo_cache_ttl()
    console.print("\n" + "="*80 + "\n")
    
    demo_cache_invalidation()
    console.print("\n" + "="*80 + "\n")
    
    demo_cache_statistics()
    console.print("\n" + "="*80 + "\n")
    
    demo_cli_commands()
    console.print("\n" + "="*80 + "\n")
    
    demo_integration_with_llm_client()
    
    console.print(Panel("✅ Demo Complete!", style="bold green", width=80))
    console.print("\nThe LLM cache system is now ready to use!")
    console.print("Try it out with: [dim]lunvex-code llm-cache-stats[/dim]")


if __name__ == "__main__":
    main()