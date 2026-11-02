"""
Cache Service — High-Performance In-Memory Layout Cache for Smart AI Panchayat.
Pre-renders and caches deterministic page component trees to make navigation
between all pages (Home, About, Dashboard, Planning, Insights, Reports, Contact)
instantaneous (< 1ms) without blocking the Flask/Dash server thread.
"""

from collections import OrderedDict
import inspect
import threading

# Max cache entries to prevent memory growth
MAX_CACHE_SIZE = 128

_cache_lock = threading.Lock()
_layout_cache = OrderedDict()


DATASET_VERSION = "v2.1-multi-state"
MODEL_VERSION = "champion_hist_gradient_boosting_v1"

def make_cache_key(
    feature,
    state_id=None,
    district_id=None,
    panchayat_id=None,
    financial_year="2026-27",
    dataset_version=DATASET_VERSION,
    model_version=MODEL_VERSION,
    state=None,
    district=None,
    panchayat=None,
    lang="en",
    extra=None
):
    """
    Generate an immutable, collision-free hashable key for every location-dependent cached result.
    Guarantees strict data isolation across states, districts, and panchayats.
    """
    def _clean_geo(v):
        if not v:
            return "ALL"
        s = str(v).strip()
        u = s.upper()
        if u in ("ALL", "NONE", "", "NULL", "UNDEFINED") or u.startswith("ALL ") or "ALL DISTRICTS" in u or "ALL PANCHAYATS" in u or "ALL STATES" in u:
            return "ALL"
        return s

    s_val = _clean_geo(state_id if state_id and str(state_id).strip().upper() != "ALL" else (state or "ALL"))
    d_val = _clean_geo(district_id if district_id and str(district_id).strip().upper() != "ALL" else (district or "ALL"))
    p_val = _clean_geo(panchayat_id if panchayat_id and str(panchayat_id).strip().upper() != "ALL" else (panchayat or "ALL"))
    
    s_name = _clean_geo(state)
    d_name = _clean_geo(district)
    p_name = _clean_geo(panchayat)

    extra_str = ""
    if extra:
        if isinstance(extra, dict):
            extra_str = ",".join(f"{k}={v}" for k, v in sorted(extra.items()))
        elif isinstance(extra, (list, tuple)):
            extra_str = ",".join(str(x) for x in extra)
        else:
            extra_str = str(extra)

    return (
        str(feature).strip().lower(),
        s_val,
        s_name,
        d_val,
        d_name,
        p_val,
        p_name,
        str(financial_year or "2026-27").strip(),
        str(dataset_version).strip(),
        str(model_version).strip(),
        str(lang or "en").strip(),
        extra_str,
    )


def get_cached_layout(page_name, render_fn, *args, **kwargs):
    """
    Retrieve layout from cache if present; otherwise execute render_fn,
    store in LRU cache, and return. Safely filters keyword arguments
    to match the target function signature.
    Guarantees no cross-Panchayat cache contamination.
    """
    state = kwargs.get("state", "ALL")
    district = kwargs.get("district", "ALL")
    panchayat = kwargs.get("panchayat", "ALL")
    state_id = kwargs.get("state_id", state)
    district_id = kwargs.get("district_id", district)
    panchayat_id = kwargs.get("panchayat_id", panchayat)
    year = kwargs.get("year", kwargs.get("financial_year", "2026-27"))
    lang = kwargs.get("lang", "en")

    key = make_cache_key(
        feature=page_name,
        state_id=state_id,
        district_id=district_id,
        panchayat_id=panchayat_id,
        financial_year=year,
        state=state,
        district=district,
        panchayat=panchayat,
        lang=lang,
    )

    with _cache_lock:
        if key in _layout_cache:
            _layout_cache.move_to_end(key)
            return _layout_cache[key]

    # Filter kwargs to only what render_fn accepts
    sig = inspect.signature(render_fn)
    has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    if has_var_kw:
        filtered_kwargs = kwargs
    else:
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

    # Compute outside lock to avoid contention
    layout = render_fn(*args, **filtered_kwargs)

    with _cache_lock:
        _layout_cache[key] = layout
        _layout_cache.move_to_end(key)
        if len(_layout_cache) > MAX_CACHE_SIZE:
            _layout_cache.popitem(last=False)  # Evict oldest entry

    return layout


def get_cached_data(*key_parts):
    """Retrieve arbitrary cached object by composite key parts."""
    key = tuple(str(p).strip() for p in key_parts)
    with _cache_lock:
        if key in _layout_cache:
            _layout_cache.move_to_end(key)
            return _layout_cache[key]
    return None


def set_cached_data(data, *key_parts):
    """Store arbitrary object in LRU cache with composite key parts."""
    key = tuple(str(p).strip() for p in key_parts)
    with _cache_lock:
        _layout_cache[key] = data
        _layout_cache.move_to_end(key)
        if len(_layout_cache) > MAX_CACHE_SIZE:
            _layout_cache.popitem(last=False)
    return data


def invalidate_location(state=None, district=None, panchayat=None):
    """Selectively invalidate cache entries matching the specified geographic criteria."""
    s_filter = str(state).strip().lower() if state and str(state).upper() != "ALL" else None
    d_filter = str(district).strip().lower() if district and str(district).upper() != "ALL" else None
    p_filter = str(panchayat).strip().lower() if panchayat and str(panchayat).upper() != "ALL" else None

    with _cache_lock:
        keys_to_remove = []
        for key in _layout_cache.keys():
            if not isinstance(key, tuple) or len(key) < 7:
                continue
            # Match against state, district, or panchayat anywhere in key
            key_str = " ".join(str(p).lower() for p in key[1:7])
            if s_filter and s_filter not in key_str:
                continue
            if d_filter and d_filter not in key_str:
                continue
            if p_filter and p_filter not in key_str:
                continue
            keys_to_remove.append(key)
        for k in keys_to_remove:
            _layout_cache.pop(k, None)


def clear_layout_cache():
    """Clear all cached page layouts (called after model retraining or data updates)."""
    with _cache_lock:
        _layout_cache.clear()

