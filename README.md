# Energy Tech Research Automation

A production-quality Python script for automatically scouting and summarizing recent Energy Technology innovations from arXiv using Google's Gemini-3-Flash API.

## Features

- 🔍 **Automated arXiv Scouting**: Fetches recent papers from arXiv API
- 🎯 **Smart Filtering**: Filters papers by recency and relevance to Energy Tech
- 🤖 **AI Summarization**: Uses Gemini-3-Flash to extract key innovations
- 📊 **Clean Reports**: Generates well-structured Markdown reports
- 🔒 **Secure**: No hardcoded secrets, uses environment variables

## Project Structure

```
.
├── main.py              # Main entry point
├── arxiv_client.py      # arXiv API client
├── filters.py           # Paper filtering utilities
├── llm_gemini.py        # Gemini API integration
├── report.py            # Report generation
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Installation

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key**:
   - Get your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

## Usage

### Basic Usage

```bash
python main.py
```

This will:
- Fetch papers from the last 7 days
- Filter for Energy Tech relevance
- Summarize up to 20 papers
- Generate a report in the `reports/` directory

### Advanced Options

```bash
# Custom date range and paper count
python main.py --days-back 14 --max-papers 50

# Limit summarization (useful for testing)
python main.py --max-summarize 5

# Custom keywords
python main.py --keywords solar battery grid

# Skip keyword filtering (only filter by date)
python main.py --no-filter

# Custom output directory
python main.py --output-dir my_reports
```

### Command-Line Arguments

- `--days-back`: Number of days to look back (default: 7)
- `--max-papers`: Maximum papers to fetch (default: 20)
- `--max-summarize`: Maximum papers to summarize (default: all)
- `--output-dir`: Output directory for reports (default: reports)
- `--keywords`: Custom keywords for filtering
- `--no-filter`: Skip keyword filtering

## Requirements

- Python 3.10+
- Google Gemini API key
- Internet connection for arXiv API access

## Dependencies

- `feedparser`: arXiv XML parsing
- `google-generativeai`: Gemini API client
- `python-dotenv`: Environment variable management
- `requests`: HTTP requests (dependency)

## Output

Reports are saved as Markdown files in the `reports/` directory with:
- Executive summary
- Individual paper summaries
- Key innovations extracted by AI
- Relevance scores
- Links to arXiv and PDFs

## Example Output

```markdown
# Energy Tech Research Report

**Generated:** 2024-01-15 10:30:00
**Total Papers:** 5

## Executive Summary
This report summarizes 5 recent Energy Technology research papers...

## Paper 1: Advanced Solar Panel Efficiency...

### Summary
[AI-generated summary]

### Key Innovations
- Innovation 1
- Innovation 2
...
```

## Best Practices

1. **API Rate Limits**: Be mindful of Gemini API rate limits when processing many papers
2. **Filtering**: Use `--no-filter` sparingly to avoid irrelevant papers
3. **Testing**: Use `--max-summarize` to test with fewer papers first
4. **Secrets**: Never commit `.env` file to version control

## Troubleshooting

- **No papers found**: Try increasing `--days-back` or `--max-papers`
- **API errors**: Verify your `GEMINI_API_KEY` is set correctly
- **Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## License

This project is provided as-is for research and educational purposes.

