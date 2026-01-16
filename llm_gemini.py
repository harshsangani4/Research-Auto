"""
Gemini API client for LLM summarization.

This module provides functionality to interact with Google's Gemini-3-Flash API
for generating insight-oriented summaries of research paper abstracts.
"""

import os
import logging
from typing import Optional, Dict
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google's Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the Gemini client.

        Args:
            api_key: Google API key (if None, reads from GEMINI_API_KEY env var)
            model_name: Name of the Gemini model to use (default: gemini-2.5-flash for Gemini-3-Flash API)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in environment "
                "variables or pass it as a parameter."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

        logger.info(f"Initialized Gemini client with model: {model_name}")

    def summarize_abstract(self, abstract: str) -> Dict[str, any]:
        """
        Generate an insight-oriented summary of an arXiv paper abstract using Gemini.

        Args:
            abstract: Paper abstract text

        Returns:
            Dictionary with structured insights:
            - insight_summary: 2-4 sentence expert insight
            - key_innovations: List of innovation bullet points
            - novel_methods: List of novel methods/techniques
            - potential_applications: List of potential applications
            - extracted_keywords: List of 5-8 technical keywords
        """
        if not abstract or not abstract.strip():
            logger.warning("Empty abstract provided")
            return self._get_empty_insight()

        prompt = self._build_summarization_prompt(abstract)

        try:
            response = self.model.generate_content(prompt)
            raw_output = response.text.strip()
            
            logger.debug("Successfully generated insight summary")
            
            # Parse the structured output
            parsed_insight = self._parse_structured_output(raw_output)
            return parsed_insight

        except Exception as e:
            logger.error(f"Error summarizing abstract with Gemini: {e}")
            # Return structured error response
            error_insight = self._get_empty_insight()
            error_insight["insight_summary"] = f"Error generating summary: {str(e)}. Please check API key and network connection."
            return error_insight

    def _build_summarization_prompt(self, abstract: str) -> str:
        """
        Build the insight-oriented prompt for abstract summarization.

        Args:
            abstract: Paper abstract text

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert research analyst specializing in Energy Technology and AI.
Analyze the following arXiv paper abstract and generate an insight-oriented summary.

Your task:
- Do NOT rewrite the abstract
- Identify what is truly new or innovative
- Explain potential impact in practical energy systems
- Extract meaningful technical keywords (not generic terms)

Abstract:
{abstract}

Generate your response in the EXACT format below (do not deviate):

Insight Summary:
<2–4 sentences written as an expert insight, focusing on innovation, novelty, and impact>

Key Innovations:
- <bullet point 1>
- <bullet point 2>

Novel Methods / Techniques:
- <bullet point 1>
- <bullet point 2>

Potential Applications:
- <bullet point 1>
- <bullet point 2>

Extracted Keywords:
- keyword1, keyword2, keyword3, keyword4, keyword5
"""
        return prompt

    def _parse_structured_output(self, raw_output: str) -> Dict[str, any]:
        """
        Parse the structured LLM output into a dictionary.

        Args:
            raw_output: Raw text output from Gemini

        Returns:
            Dictionary with parsed structured data
        """
        result = {
            "insight_summary": "",
            "key_innovations": [],
            "novel_methods": [],
            "potential_applications": [],
            "extracted_keywords": [],
        }

        # Split into lines for parsing
        lines = raw_output.split("\n")
        current_section = None
        current_text = []

        for line in lines:
            line = line.strip()
            
            # Detect section headers
            if line.startswith("Insight Summary:"):
                current_section = "insight_summary"
                current_text = []
                # Get text after the colon if present
                after_colon = line.split(":", 1)
                if len(after_colon) > 1 and after_colon[1].strip():
                    current_text.append(after_colon[1].strip())
                continue
            elif line.startswith("Key Innovations:"):
                # Save previous section
                if current_section == "insight_summary" and current_text:
                    result["insight_summary"] = " ".join(current_text).strip()
                
                current_section = "key_innovations"
                current_text = []
                continue
            elif line.startswith("Novel Methods / Techniques:") or line.startswith("Novel Methods:"):
                # Save previous section
                if current_section == "key_innovations" and current_text:
                    result["key_innovations"] = [item for item in current_text if item]
                
                current_section = "novel_methods"
                current_text = []
                continue
            elif line.startswith("Potential Applications:"):
                # Save previous section
                if current_section == "novel_methods" and current_text:
                    result["novel_methods"] = [item for item in current_text if item]
                
                current_section = "potential_applications"
                current_text = []
                continue
            elif line.startswith("Extracted Keywords:"):
                # Save previous section
                if current_section == "potential_applications" and current_text:
                    result["potential_applications"] = [item for item in current_text if item]
                
                current_section = "extracted_keywords"
                current_text = []
                continue

            # Process content based on current section
            if current_section == "insight_summary":
                if line:
                    current_text.append(line)
            elif current_section in ["key_innovations", "novel_methods", "potential_applications"]:
                # Extract bullet points
                if line.startswith("-") or line.startswith("*"):
                    item = line.lstrip("-* ").strip()
                    if item:
                        current_text.append(item)
            elif current_section == "extracted_keywords":
                # Extract keywords (can be comma-separated or bullet points)
                if line.startswith("-"):
                    # Extract after the dash
                    keywords_text = line.lstrip("- ").strip()
                    # Split by comma
                    keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]
                    current_text.extend(keywords)
                elif "," in line:
                    # Direct comma-separated
                    keywords = [kw.strip() for kw in line.split(",") if kw.strip()]
                    current_text.extend(keywords)

        # Save final section
        if current_section == "insight_summary" and current_text:
            result["insight_summary"] = " ".join(current_text).strip()
        elif current_section == "key_innovations" and current_text:
            result["key_innovations"] = [item for item in current_text if item]
        elif current_section == "novel_methods" and current_text:
            result["novel_methods"] = [item for item in current_text if item]
        elif current_section == "potential_applications" and current_text:
            result["potential_applications"] = [item for item in current_text if item]
        elif current_section == "extracted_keywords" and current_text:
            result["extracted_keywords"] = current_text[:8]  # Limit to 8 keywords

        # Fallback: if parsing failed, try to extract at least the summary
        if not result["insight_summary"]:
            # Try to find any substantial text as summary
            paragraphs = [p.strip() for p in raw_output.split("\n\n") if p.strip()]
            if paragraphs:
                result["insight_summary"] = paragraphs[0][:500]  # First paragraph, truncated

        # Ensure we have at least something
        if not result["insight_summary"]:
            result["insight_summary"] = "Unable to generate insight summary."

        return result

    def _get_empty_insight(self) -> Dict[str, any]:
        """
        Get an empty insight structure.

        Returns:
            Dictionary with empty fields
        """
        return {
            "insight_summary": "No abstract available for summarization.",
            "key_innovations": [],
            "novel_methods": [],
            "potential_applications": [],
            "extracted_keywords": [],
        }
