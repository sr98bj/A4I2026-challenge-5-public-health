"""
Custom Python Tools for the Fulton County Mobile Clinic ADK System.
Adheres to the challenge requirement:
  - Custom function tools encapsulating domain logic (tract query, convenience trap scoring, reading level).
  - Context isolation: operational queries never return equity columns.
"""

import math
import re
from typing import List, Dict, Any, Optional
from models import OperationalCandidate, EquityMetrics


def compute_flesch_kincaid_grade(text: str) -> float:
    """Calculate Flesch-Kincaid Grade Level for community readability validation.
    Formula: 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0.0

    words = re.findall(r'\b[A-Za-z]+\b', text)
    if not words:
        return 0.0

    def count_syllables(word: str) -> int:
        word = word.lower()
        if len(word) <= 3:
            return 1
        count = len(re.findall(r'[aeiouy]+', word))
        if word.endswith('e') and not word.endswith('le') and count > 1:
            count -= 1
        return max(1, count)

    total_syllables = sum(count_syllables(w) for w in words)
    words_per_sentence = len(words) / len(sentences)
    syllables_per_word = total_syllables / len(words)

    grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    return round(max(0.0, grade), 1)


def calculate_convenience_trap_score(
    uninsured_rate_pct: float,
    km_to_safety_net: float,
    km_to_any_care: float,
    parking_capacity_spots: int
) -> Dict[str, Any]:
    """Custom Domain Logic Tool:
    Quantifies the discrepancy between physical parking convenience and clinical necessity.
    The challenge turns on 'extra_km_if_uninsured' = km_to_safety_net - km_to_any_care.
    """
    extra_km_if_uninsured = max(0.0, km_to_safety_net - km_to_any_care)

    # Convenience score (0 to 100) based on parking spots
    convenience_score = min(100.0, parking_capacity_spots * 3.0)

    # Need score (0 to 100) based on uninsured rate and safety-net distance
    need_score = min(100.0, (uninsured_rate_pct * 2.5) + (extra_km_if_uninsured * 5.0))

    # A convenience trap occurs when convenience is high (> 60) but clinical need is low (< 35)
    is_trap = (convenience_score >= 60.0 and need_score < 40.0) or (uninsured_rate_pct < 12.0)

    return {
        "convenience_score": round(convenience_score, 1),
        "need_score": round(need_score, 1),
        "extra_km_if_uninsured": round(extra_km_if_uninsured, 2),
        "is_convenience_trap": is_trap,
        "disparity_ratio": round(convenience_score / max(1.0, need_score), 2)
    }
