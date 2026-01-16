"""
Main entry point for Energy Tech research automation.

This script orchestrates the entire pipeline:
1. Fetching recent arXiv papers
2. Parsing entries
3. Applying filters
4. Selecting top 5 papers
5. Summarizing with Gemini-3-Flash
6. Generating Markdown reports
"""

import argparse
import logging
import sys
from datetime import datetime

from arxiv_client import ArxivClient
from filters import (
    filter_by_months,
    filter_by_abstract_keywords,
    sort_by_newest,
    get_default_energy_tech_keywords,
)
from llm_gemini import GeminiClient
from report import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Automated Energy Tech research paper scouting and summarization"
    )
    parser.add_argument(
        "--query",
        type=str,
        default="all:energy+OR+all:renewable+OR+all:solar+OR+all:wind+OR+all:battery",
        help="arXiv search query (default: energy tech keywords)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=50,
        help="Maximum number of papers to fetch (default: 50)",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=1,
        help="Filter papers newer than X months (default: 1)",
    )
    parser.add_argument(
        "--keywords",
        type=str,
        nargs="+",
        default=None,
        help="Custom keywords for filtering (default: energy tech keywords)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top papers to summarize (default: 5)",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Energy Tech Research Automation")
    logger.info("=" * 60)

    try:
        # Step 1: Initialize clients
        logger.info("\n[Step 1/6] Initializing clients...")
        arxiv_client = ArxivClient(max_results=args.max_results)
        gemini_client = GeminiClient()
        report_generator = ReportGenerator()

        # Step 2: Fetch raw arXiv entries
        logger.info(f"\n[Step 2/6] Fetching papers from arXiv...")
        logger.info(f"Query: {args.query}")
        raw_entries = arxiv_client.fetch(
            query=args.query,
            max_results=args.max_results,
            sort_by="submittedDate",
            sort_order="descending",
        )

        if not raw_entries:
            logger.warning("No papers found. Try adjusting --query or --max-results.")
            return

        logger.info(f"Fetched {len(raw_entries)} raw entries")

        # Step 3: Parse entries
        logger.info("\n[Step 3/6] Parsing entries...")
        papers = arxiv_client.parse_entries(raw_entries)

        if not papers:
            logger.warning("No papers could be parsed.")
            return

        logger.info(f"Parsed {len(papers)} papers")

        # Step 4: Apply filters
        logger.info("\n[Step 4/6] Applying filters...")
        
        # Filter by months
        papers = filter_by_months(papers, months=args.months)
        logger.info(f"After month filter: {len(papers)} papers")

        # Filter by abstract keywords
        keywords = args.keywords or get_default_energy_tech_keywords()
        papers = filter_by_abstract_keywords(papers, keywords=keywords)
        logger.info(f"After keyword filter: {len(papers)} papers")

        # Sort by newest first
        papers = sort_by_newest(papers)
        logger.info(f"Sorted {len(papers)} papers by date")

        if not papers:
            logger.warning("No papers passed the filters. Try adjusting filters.")
            return

        # Step 5: Select top N papers
        logger.info(f"\n[Step 5/6] Selecting top {args.top_n} papers...")
        top_papers = papers[:args.top_n]
        logger.info(f"Selected {len(top_papers)} papers for summarization")

        # Step 6: Summarize with Gemini
        logger.info("\n[Step 6/6] Summarizing papers with Gemini-3-Flash...")
        for i, paper in enumerate(top_papers, 1):
            logger.info(f"Summarizing paper {i}/{len(top_papers)}: {paper.get('title', 'Unknown')[:60]}...")
            abstract = paper.get("abstract", "")
            if abstract:
                insight_data = gemini_client.summarize_abstract(abstract)
                paper["gemini_insight"] = insight_data
            else:
                # Use summarize_abstract which handles empty abstracts gracefully
                paper["gemini_insight"] = gemini_client.summarize_abstract("")
                logger.warning(f"Paper {i} has no abstract")

        # Step 7: Generate report
        logger.info("\n[Step 7/7] Generating Markdown report...")
        report_path = report_generator.save_report(top_papers)

        logger.info("\n" + "=" * 60)
        logger.info("✅ SUCCESS!")
        logger.info(f"Report saved to: {report_path}")
        logger.info(f"Total papers processed: {len(top_papers)}")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
