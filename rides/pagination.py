from rest_framework.pagination import LimitOffsetPagination
from django.core.cache import cache
import hashlib


class CachedCountLimitOffsetPagination(LimitOffsetPagination):
    """
    LimitOffset pagination with cached count for better performance on large tables.

    The count is cached for 5 minutes to avoid expensive COUNT(*) queries on every request.
    Cache key is based on the queryset's SQL to ensure accuracy when filters change.
    """
    default_limit = 20
    max_limit = 100

    def get_count(self, queryset):
        """
        Get the total count, using cache when available.
        Cache expires after 5 minutes (300 seconds).
        """
        # Generate cache key based on the queryset's SQL
        query_str = str(queryset.query)
        cache_key = f'pagination_count_{hashlib.md5(query_str.encode()).hexdigest()}'

        # Try to get from cache
        count = cache.get(cache_key)

        if count is None:
            # Cache miss - calculate count
            count = super().get_count(queryset)
            # Cache for 5 minutes
            cache.set(cache_key, count, 300)

        return count
