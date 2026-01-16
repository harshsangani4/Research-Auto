"""
arXiv API client for fetching recent papers.

This module provides functionality to fetch raw arXiv entries
and parse them into structured dictionaries.
"""

import feedparser
from datetime import datetime
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class ArxivClient:
    """Client for interacting with the arXiv API."""

    ARXIV_BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, max_results: int = 50):
        """
        Initialize the arXiv client.

        Args:
            max_results: Maximum number of results to fetch per query
        """
        self.max_results = max_results

    def fetch(
        self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> List:
        """
        Fetch raw arXiv entries matching the query.

        Args:
            query: Search query string (e.g., "cat:cs.AI" or "energy AND technology")
            max_results: Maximum number of results (overrides instance default)
            sort_by: Sort field ("relevance", "lastUpdatedDate", "submittedDate")
            sort_order: Sort order ("ascending" or "descending")

        Returns:
            List of raw feedparser entry objects

        Raises:
            Exception: If network/API request fails
        """
        max_results = max_results or self.max_results
        url = (
            f"{self.ARXIV_BASE_URL}?"
            f"search_query={query}&"
            f"start=0&"
            f"max_results={max_results}&"
            f"sortBy={sort_by}&"
            f"sortOrder={sort_order}"
        )

        logger.info(f"Fetching papers from arXiv with query: {query}")
        
        try:
            # Add retry logic for network errors
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    feed = feedparser.parse(url)
                    
                    if feed.bozo:
                        logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
                    
                    entries = feed.entries
                    logger.info(f"Successfully fetched {len(entries)} raw entries")
                    return entries
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Unexpected error fetching from arXiv: {e}")
            raise

    def parse_entry(self, entry) -> Optional[Dict]:
        """
        Parse a raw arXiv entry into a structured dictionary.

        Args:
            entry: Raw feedparser entry object

        Returns:
            Dictionary with parsed fields: title, abstract, authors, published_date, pdf_link
            Returns None if parsing fails
        """
        try:
            # Extract title and clean newlines
            title = entry.get("title", "").replace("\n", " ").strip()
            
            # Extract abstract and clean newlines
            abstract = entry.get("summary", "").replace("\n", " ").strip()
            # Remove extra whitespace
            abstract = " ".join(abstract.split())
            
            # Extract authors
            authors = [author.name for author in entry.get("authors", [])]
            
            # Parse published date
            published_date = None
            if entry.published_parsed:
                try:
                    published_date = datetime(*entry.published_parsed[:6])
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing published date: {e}")
            
            # Extract PDF link
            pdf_link = None
            for link in entry.get("links", []):
                if link.get("type") == "application/pdf":
                    pdf_link = link.get("href")
                    break
            
            paper = {
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "published_date": published_date,
                "pdf_link": pdf_link,
            }
            
            return paper
            
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None

    def parse_entries(self, entries: List) -> List[Dict]:
        """
        Parse multiple raw arXiv entries.

        Args:
            entries: List of raw feedparser entry objects

        Returns:
            List of parsed paper dictionaries
        """
        parsed_papers = []
        for entry in entries:
            paper = self.parse_entry(entry)
            if paper:
                parsed_papers.append(paper)
        
        logger.info(f"Parsed {len(parsed_papers)} papers from {len(entries)} entries")
        return parsed_papers
