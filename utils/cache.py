"""
CacheManager: Redis-like caching for Project Synapse
Manages prediction cache and solution storage
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class CacheManager:
    """
    Simple in-memory cache manager for Project Synapse
    Simulates Redis functionality for demonstration purposes
    """
    
    def __init__(self):
        self.cache = {}
        self.expiry_times = {}
        self.access_times = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set a key-value pair with optional TTL (time to live)
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
        
        Returns:
            bool: True if successful
        """
        try:
            # Serialize value to JSON for storage
            serialized_value = self._serialize_value(value)
            
            # Store in cache
            self.cache[key] = serialized_value
            
            # Set expiry time
            if ttl > 0:
                self.expiry_times[key] = time.time() + ttl
            else:
                self.expiry_times[key] = None
            
            # Record access time
            self.access_times[key] = time.time()
            
            # Update stats
            self.stats['sets'] += 1
            
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        try:
            # Check if key exists
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            # Check if expired
            if self._is_expired(key):
                self.delete(key)
                self.stats['misses'] += 1
                return None
            
            # Get value and deserialize
            serialized_value = self.cache[key]
            value = self._deserialize_value(serialized_value)
            
            # Update access time
            self.access_times[key] = time.time()
            
            # Update stats
            self.stats['hits'] += 1
            
            return value
            
        except Exception as e:
            print(f"Cache get error: {e}")
            self.stats['misses'] += 1
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache
        
        Args:
            key: Cache key to delete
        
        Returns:
            bool: True if successful
        """
        try:
            if key in self.cache:
                del self.cache[key]
                del self.expiry_times[key]
                del self.access_times[key]
                self.stats['deletes'] += 1
                return True
            return False
            
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists and is not expired
        
        Args:
            key: Cache key to check
        
        Returns:
            bool: True if key exists and is valid
        """
        if key not in self.cache:
            return False
        
        if self._is_expired(key):
            self.delete(key)
            return False
        
        return True
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiry time for an existing key
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
        
        Returns:
            bool: True if successful
        """
        if key not in self.cache:
            return False
        
        if ttl > 0:
            self.expiry_times[key] = time.time() + ttl
        else:
            self.expiry_times[key] = None
        
        return True
    
    def ttl(self, key: str) -> int:
        """
        Get remaining time to live for a key
        
        Args:
            key: Cache key
        
        Returns:
            int: Remaining TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        if key not in self.cache:
            return -2
        
        if self.expiry_times[key] is None:
            return -1
        
        remaining = int(self.expiry_times[key] - time.time())
        return max(0, remaining)
    
    def keys(self, pattern: str = "*") -> List[str]:
        """
        Get all keys matching a pattern
        
        Args:
            pattern: Pattern to match (supports simple wildcards)
        
        Returns:
            List of matching keys
        """
        try:
            import fnmatch
            matching_keys = []
            
            for key in self.cache.keys():
                if fnmatch.fnmatch(key, pattern):
                    # Check if not expired
                    if not self._is_expired(key):
                        matching_keys.append(key)
                    else:
                        # Clean up expired key
                        self.delete(key)
            
            return matching_keys
            
        except ImportError:
            # Fallback without fnmatch
            return list(self.cache.keys())
    
    def get_all_keys(self) -> List[str]:
        """
        Get all valid (non-expired) keys
        
        Returns:
            List of all valid keys
        """
        valid_keys = []
        expired_keys = []
        
        for key in self.cache.keys():
            if self._is_expired(key):
                expired_keys.append(key)
            else:
                valid_keys.append(key)
        
        # Clean up expired keys
        for key in expired_keys:
            self.delete(key)
        
        return valid_keys
    
    def clear(self) -> bool:
        """
        Clear all cache entries
        
        Returns:
            bool: True if successful
        """
        try:
            self.cache.clear()
            self.expiry_times.clear()
            self.access_times.clear()
            return True
            
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def size(self) -> int:
        """
        Get current cache size (excluding expired entries)
        
        Returns:
            int: Number of valid cache entries
        """
        # Clean up expired entries first
        self._cleanup_expired()
        return len(self.cache)
    
    def info(self) -> Dict[str, Any]:
        """
        Get cache information and statistics
        
        Returns:
            Dict containing cache information
        """
        # Clean up expired entries first
        self._cleanup_expired()
        
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'total_keys': len(self.cache),
            'expired_keys': len([k for k in self.expiry_times.values() if k and k < time.time()]),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'deletes': self.stats['deletes'],
            'hit_rate_percent': round(hit_rate, 2),
            'memory_usage_mb': self._estimate_memory_usage(),
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time())
        }
    
    def _is_expired(self, key: str) -> bool:
        """Check if a key is expired"""
        if key not in self.expiry_times:
            return False
        
        expiry_time = self.expiry_times[key]
        if expiry_time is None:
            return False
        
        return time.time() > expiry_time
    
    def _cleanup_expired(self):
        """Remove all expired keys from cache"""
        expired_keys = []
        
        for key, expiry_time in self.expiry_times.items():
            if expiry_time and time.time() > expiry_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value to JSON string for storage"""
        try:
            return json.dumps(value, default=self._json_serializer)
        except Exception as e:
            print(f"Serialization error: {e}")
            return json.dumps(str(value))
    
    def _deserialize_value(self, serialized_value: str) -> Any:
        """Deserialize JSON string back to original value"""
        try:
            return json.loads(serialized_value)
        except Exception as e:
            print(f"Deserialization error: {e}")
            return serialized_value
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        try:
            import sys
            
            total_size = 0
            for key, value in self.cache.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(value)
            
            # Convert to MB
            return round(total_size / (1024 * 1024), 2)
            
        except Exception:
            # Fallback estimation
            return round(len(self.cache) * 0.001, 2)  # Rough estimate
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset cache statistics"""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def set_with_tags(self, key: str, value: Any, tags: List[str], ttl: int = 3600) -> bool:
        """
        Set a key with tags for easier management
        
        Args:
            key: Cache key
            value: Value to cache
            tags: List of tags for the key
            ttl: Time to live in seconds
        
        Returns:
            bool: True if successful
        """
        # Store the value
        success = self.set(key, value, ttl)
        
        if success:
            # Store tags separately
            tag_key = f"tags:{key}"
            self.set(tag_key, tags, ttl)
        
        return success
    
    def get_by_tag(self, tag: str) -> List[Any]:
        """
        Get all values that have a specific tag
        
        Args:
            tag: Tag to search for
        
        Returns:
            List of values with the specified tag
        """
        tagged_values = []
        
        for key in self.cache.keys():
            if key.startswith("tags:"):
                continue
            
            tag_key = f"tags:{key}"
            if tag_key in self.cache:
                tags = self.get(tag_key)
                if tags and tag in tags:
                    value = self.get(key)
                    if value is not None:
                        tagged_values.append(value)
        
        return tagged_values
    
    def delete_by_tag(self, tag: str) -> int:
        """
        Delete all keys that have a specific tag
        
        Args:
            tag: Tag to search for
        
        Returns:
            int: Number of keys deleted
        """
        deleted_count = 0
        
        for key in list(self.cache.keys()):
            if key.startswith("tags:"):
                continue
            
            tag_key = f"tags:{key}"
            if tag_key in self.cache:
                tags = self.get(tag_key)
                if tags and tag in tags:
                    if self.delete(key):
                        deleted_count += 1
                    # Also delete the tag entry
                    self.delete(tag_key)
        
        return deleted_count 