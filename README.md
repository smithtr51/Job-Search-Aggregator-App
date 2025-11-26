# Job Hunter 🎯

A Python-based job search aggregator that scrapes federal contractor career pages, scores job matches against your resume using Claude, and helps you track applications.

## Features

- **Multi-site scraping** — Scrapes job postings from multiple career pages
- **AI-powered matching** — Uses Claude to score jobs against your resume
- **Gap analysis** — Identifies what you might be missing for specific roles
- **Cover letter guidance** — Generates key talking points per job
- **Application tracking** — Track status from discovery to offer

## Quick Start

```bash
# 1. Clone and setup
cd job_hunter
pip install -r requirements.txt

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"

# 3. Add your resume
# Create resume.txt with your resume content (plain text works best)

# 4. Initialize and run
python main.py init
python main.py scrape
python main.py score
python main.py list --min-score 70
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize the SQLite database |
| `scrape` | Scrape all configured career sites |
| `score` | Score all unscored jobs against your resume |
| `list` | List jobs with filters (--status, --min-score, --company) |
| `show <id>` | Show full details for a job |
| `analyze <id>` | Deep analysis with cover letter points and gap analysis |
| `stats` | Show summary statistics |
| `status <id> <status>` | Update job status (new/reviewed/applied/rejected/interviewing) |

## Configuration

Edit `config.py` to:

- Add/remove target career sites
- Adjust default search terms
- Set minimum match score threshold
- Configure rate limiting

### Adding a New Site

```python
# In config.py, add to TARGET_SITES:
{
    "name": "Company Name",
    "careers_url": "https://company.com/careers",
    "search_params": {"keywords": "your role"},
    "type": "custom"  # or "workday", "icims" for known ATS
}
```

## Architecture

```
job_hunter/
├── main.py        # CLI entry point
├── config.py      # Configuration and target sites
├── scraper.py     # Web scraping logic
├── scorer.py      # LLM-based job matching
├── storage.py     # Database operations
├── requirements.txt
└── resume.txt     # Your resume (create this)
```

## Extending the Scraper

The generic scraper works for many sites but may need customization for specific ATS systems. The codebase supports:

- **USAJobs** — Uses official API (requires API key)
- **Google Custom Search** — Find jobs across multiple sites
- **Generic** — Heuristic-based scraping for most career pages

For JavaScript-heavy sites (Workday, etc.), you may need to:

1. Install Playwright: `pip install playwright && playwright install`
2. Modify `scraper.py` to use Playwright instead of requests

## Database Schema

Jobs are stored in SQLite with these key fields:

- `id` — Unique identifier
- `company`, `title`, `location`, `description`, `url`
- `match_score` — 0-100 AI-generated match score
- `match_reasoning` — Explanation of the score
- `status` — Application status tracking
- `notes` — Your notes on the opportunity

## Tips for Best Results

1. **Resume format** — Plain text works best. Include keywords from your target roles.

2. **Rate limiting** — The default 2-second delay is polite. Increase it if you get blocked.

3. **API usage** — Scoring uses Claude API. Monitor your usage at console.anthropic.com.

4. **High-value targets** — Focus on jobs scoring 70+ for best match likelihood.

5. **Gap analysis** — Use `analyze` command before applying to identify what to emphasize.

## Cost Estimate

- Scoring: ~500 tokens per job (~$0.002 per job with Claude Sonnet)
- Full analysis: ~2000 tokens (~$0.008 per job)
- 100 jobs fully analyzed ≈ $1.00

## Future Enhancements

- [ ] Email alerts for high-match jobs
- [ ] Resume tailoring suggestions per job
- [ ] Integration with LinkedIn API
- [ ] Playwright support for JS-heavy sites
- [ ] Web dashboard (Streamlit or Flask)
- [ ] Auto-detection of job posting RSS feeds

## Legal Note

Respect website terms of service. This tool is for personal use to aggregate publicly available job postings. Avoid excessive request rates and don't use for commercial purposes without permission.
