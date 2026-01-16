"""
Filtering utilities for arXiv papers.

This module provides functions to filter papers by recency,
relevance, and sort them.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def filter_by_months(
    papers: List[Dict], months: int = 1
) -> List[Dict]:
    """
    Filter papers newer than X months.

    Args:
        papers: List of paper dictionaries
        months: Number of months to look back

    Returns:
        Filtered list of recent papers
    """
    if not papers:
        return []

    cutoff_date = datetime.now() - timedelta(days=months * 30)
    filtered = [
        p for p in papers
        if p.get("published_date") and p["published_date"] >= cutoff_date
    ]

    logger.info(
        f"Filtered {len(filtered)} papers from {len(papers)} "
        f"(published within {months} months)"
    )
    return filtered


def filter_by_abstract_keywords(
    papers: List[Dict],
    keywords: List[str],
    case_sensitive: bool = False,
) -> List[Dict]:
    """
    Filter papers whose abstract contains Energy Tech keywords.

    Args:
        papers: List of paper dictionaries
        keywords: List of keywords to search for in abstract
        case_sensitive: Whether keyword matching is case-sensitive

    Returns:
        Filtered list of papers with matching keywords in abstract
    """
    if not papers or not keywords:
        return papers

    if not case_sensitive:
        keywords = [kw.lower() for kw in keywords]

    def matches_keywords(paper: Dict) -> bool:
        """Check if paper abstract contains any keyword."""
        abstract = paper.get("abstract", "")
        if not abstract:
            return False
        
        if not case_sensitive:
            abstract = abstract.lower()
        
        return any(kw in abstract for kw in keywords)

    filtered = [p for p in papers if matches_keywords(p)]

    logger.info(
        f"Filtered {len(filtered)} papers from {len(papers)} "
        f"(abstract contains keywords: {keywords})"
    )
    return filtered


def sort_by_newest(papers: List[Dict]) -> List[Dict]:
    """
    Sort papers by published date (newest first).

    Args:
        papers: List of paper dictionaries

    Returns:
        Sorted list of papers (newest first)
    """
    def get_date(paper: Dict) -> datetime:
        """Get published date, defaulting to very old date if missing."""
        date = paper.get("published_date")
        if date is None:
            return datetime(1970, 1, 1)  # Very old date for sorting
        return date

    sorted_papers = sorted(
        papers,
        key=get_date,
        reverse=True  # Newest first
    )

    logger.info(f"Sorted {len(sorted_papers)} papers by date (newest first)")
    return sorted_papers


def get_default_energy_tech_keywords() -> List[str]:
    """
    Get default configurable keywords for energy technology research.

    Returns:
        List of relevant keywords
    """
    return [
        "energy",
        "renewable",
        "solar",
        "wind",
        "battery",
        "storage",
        "grid",
        "power",
        "efficiency",
        "sustainable",
        "photovoltaic",
        "turbine",
        "fuel cell",
        "hydrogen",
        "electric",
        "generation",
        "transmission",
        "distribution",
    ]
