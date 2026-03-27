# 202603_demo
Gather Y Combinator startup data for my research

## Y Combinator Startup Scraper

The `scrape_yc.py` script allows you to easily fetch a complete list of startups for any Y Combinator batch directly from their public API and website.

### Prerequisites

You'll need Python 3 and the following packages installed:

```bash
pip install requests beautifulsoup4
```

### Usage

Run the script from your terminal, providing the desired YC batch via the `--batch` (or `-b`) argument.

For example, to get all the startups from the Winter 2024 batch:

```bash
python scrape_yc.py --batch W24
```

To get startups from Summer 2024:

```bash
python scrape_yc.py -b S24
```

The script will scan through Y Combinator's directory and output the collected data into a JSON file named `yc_startups_BATCH.json` (e.g., `yc_startups_W24.json`).

### Data Fields Collected
*   Company Name
*   YC Batch
*   Short Description
*   Website URL
*   Founders (parsed from their YC profile)
*   Industry
*   YC URL
