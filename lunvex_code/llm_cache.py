"""LLM response caching system for improved performance and cost reduction."""

import hashlib
import json
import os
import time
from collections import OrderedDict
from dataclasses import dataclass, asdict
from typing import Any, Optional, Tuple, Dict, List
import pickle


@dataclass
class LLMCacheEntry:
    """Entry in the LLM cache."""
    
    response: Dict[str, Any]  # Serialized LLM response
    timestamp: float
    access_count: int = 0
    token_count: int = 0  # Total tokens used (for statistics)


class LLMCache:
    """LRU cache for LLM responses with TTL."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize the LLM cache.
        
        Args:
            max_size: Maximum number of responses to cache
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, LLMCacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.tokens_saved = 0  # Total tokens saved by cache hits
        
    def _generate_cache_key(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Generate a unique cache key for an LLM request.
        
        Args:
            model: LLM model name
            messages: List of messages
            tools: Optional list of tools
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            MD5 hash of the request parameters
        """
        # Create a deterministic representation of the request
        request_data = {
            "model": model,
            "messages": messages,
            "tools": tools if tools else [],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # Convert to JSON string with sorted keys for consistency
        request_json = json.dumps(request_data, sort_keys=True, default=str)
        
        # Generate MD5 hash
        return hashlib.md5(request_json.encode()).hexdigest()
    
    def _is_cache_valid(self, entry: LLMCacheEntry) -> bool:
        """Check if a cache entry is still valid."""
        # Check TTL
        if time.time() - entry.timestamp > self.ttl_seconds:
            return False
        return True
    
    def get(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        **kwargs
    ) -> Optional[Tuple[Dict[str, Any], bool]]:
        """
        Get LLM response from cache if available and valid.
        
        Args:
            model: LLM model name
            messages: List of messages
            tools: Optional list of tools
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (response_data, from_cache) or None if not in cache
        """
        cache_key = self._generate_cache_key(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            if self._is_cache_valid(entry):
                # Update access count and move to end (most recently used)
                entry.access_count += 1
                self.cache.move_to_end(cache_key)
                self.hits += 1
                self.tokens_saved += entry.token_count
                return entry.response, True
            else:
                # Remove invalid entry
                del self.cache[cache_key]
        
        self.misses += 1
        return None
    
    def put(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        response: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        token_count: int = 0,
        **kwargs
    ) -> None:
        """
        Add LLM response to cache.
        
        Args:
            model: LLM model name
            messages: List of messages
            response: LLM response data
            tools: Optional list of tools
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            token_count: Total tokens used in the response
            **kwargs: Additional parameters
        """
        cache_key = self._generate_cache_key(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Create cache entry
        entry = LLMCacheEntry(
            response=response,
            timestamp=time.time(),
            access_count=0,
            token_count=token_count
        )
        
        # Add to cache
        self.cache[cache_key] = entry
        
        # Enforce max size (LRU eviction)
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)  # Remove least recently used
    
    def invalidate(self, pattern: Optional[str] = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            pattern: Optional pattern to match against cache keys
            
        Returns:
            Number of entries invalidated
        """
        if pattern is None:
            # Invalidate all entries
            count = len(self.cache)
            self.cache.clear()
            return count
        
        # Invalidate entries matching pattern
        keys_to_remove = []
        for key in self.cache:
            if pattern in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        return len(keys_to_remove)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.tokens_saved = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "tokens_saved": self.tokens_saved,
            "current_size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "oldest_entry": min((e.timestamp for e in self.cache.values()), default=0),
            "most_accessed": max((e.access_count for e in self.cache.values()), default=0),
        }
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save cache to file.
        
        Args:
            filepath: Path to save cache
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'cache': self.cache,
                    'hits': self.hits,
                    'misses': self.misses,
                    'tokens_saved': self.tokens_saved,
                }, f)
            return True
        except Exception:
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Load cache from file.
        
        Args:
            filepath: Path to load cache from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                return False
            
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.cache = data.get('cache', OrderedDict())
                self.hits = data.get('hits', 0)
                self.misses = data.get('misses', 0)
                self.tokens_saved = data.get('tokens_saved', 0)
            
            # Clean up expired entries
            current_time = time.time()
            keys_to_remove = []
            for key, entry in self.cache.items():
                if current_time - entry.timestamp > self.ttl_seconds:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.cache[key]
            
            return True
        except Exception:
            return False


# Global LLM cache instance
_llm_cache: Optional[LLMCache] = None


def get_llm_cache() -> LLMCache:
    """Get or create the global LLM cache instance."""
    global _llm_cache
    
    if _llm_cache is None:
        # Configure from environment variables
        max_size = int(os.getenv("LUNVEX_LLM_CACHE_MAX_SIZE", "100"))
        ttl_seconds = int(os.getenv("LUNVEX_LLM_CACHE_TTL_SECONDS", "3600"))
        
        _llm_cache = LLMCache(max_size=max_size, ttl_seconds=ttl_seconds)
        
        # Try to load from persistent storage
        cache_dir = os.path.expanduser("~/.lunvex-code")
        cache_file = os.path.join(cache_dir, "llm_cache.pkl")
        if os.path.exists(cache_dir):
            _llm_cache.load_from_file(cache_file)
    
    return _llm_cache


def configure_llm_cache(max_size: int = 100, ttl_seconds: int = 3600) -> None:
    """Configure the global LLM cache."""
    global _llm_cache
    
    if _llm_cache is None:
        _llm_cache = LLMCache(max_size=max_size, ttl_seconds=ttl_seconds)
    else:
        _llm_cache.max_size = max_size
        _llm_cache.ttl_seconds = ttl_seconds
    
    # Save configuration
    save_llm_cache()


def save_llm_cache() -> bool:
    """Save the global LLM cache to persistent storage."""
    cache = get_llm_cache()
    
    cache_dir = os.path.expanduser("~/.lunvex-code")
    cache_file = os.path.join(cache_dir, "llm_cache.pkl")
    
    try:
        os.makedirs(cache_dir, exist_ok=True)
        return cache.save_to_file(cache_file)
    except Exception:
        return False