import requests
import json
import argparse
import time
from bs4 import BeautifulSoup
import concurrent.futures

API_URL = "https://api.ycombinator.com/v0.1/companies"
YC_BASE_URL = "https://www.ycombinator.com"

def fetch_companies_from_page(page, retries=3):
    for i in range(retries):
        try:
            response = requests.get(API_URL, params={"page": page}, timeout=15)
            if response.status_code == 429:
                time.sleep(2 * (i + 1))
                continue
            response.raise_for_status()
            data = response.json()
            if data and 'companies' in data:
                return data.get('companies', [])
            return []
        except requests.RequestException as e:
            time.sleep(2 * (i + 1))
    print(f"Error fetching page {page} after retries")
    return []

def get_founders_for_company(company_slug, retries=3):
    url = f"{YC_BASE_URL}/companies/{company_slug}"
    for i in range(retries):
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 429:
                time.sleep(2 * (i + 1))
                continue
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find('div', attrs={'data-page': True})
            if not div:
                return []

            data = json.loads(div['data-page'])
            company_data = data.get('props', {}).get('company', {})
            if not company_data:
                return []

            founders = company_data.get('founders', [])
            founder_names = [f.get('full_name') for f in founders if f.get('full_name')]
            return founder_names
        except Exception as e:
            time.sleep(2 * (i + 1))
    print(f"Error fetching founders for {company_slug} after retries")
    return []

def scrape_yc_startups(target_batch):
    print(f"Finding all companies for batch '{target_batch}'...")

    try:
        response = requests.get(API_URL, params={"page": 1})
        total_pages = response.json().get('totalPages', 1)
    except Exception as e:
        print(f"Error fetching total pages: {e}")
        return

    print(f"Scanning {total_pages} pages of YC companies. This may take a moment to avoid rate limits...")

    batch_companies = []

    # Use max_workers=5 to avoid 429 Too Many Requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_page = {executor.submit(fetch_companies_from_page, page): page for page in range(1, total_pages + 1)}
        for future in concurrent.futures.as_completed(future_to_page):
            companies = future.result()
            if companies:
                for company in companies:
                    batch = company.get('batch')
                    if batch and isinstance(batch, str) and batch.upper() == target_batch.upper():
                        batch_companies.append(company)

    print(f"Found {len(batch_companies)} companies in batch '{target_batch}'. Fetching founder details...")

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_company = {executor.submit(get_founders_for_company, c['slug']): c for c in batch_companies}

        for i, future in enumerate(concurrent.futures.as_completed(future_to_company)):
            if (i+1) % 20 == 0:
                print(f"Processed {i+1}/{len(batch_companies)} companies...")
            c = future_to_company[future]
            founders = future.result()

            company_info = {
                "Company Name": c.get("name"),
                "YC Batch": c.get("batch"),
                "Short Description": c.get("oneLiner"),
                "Website URL": c.get("website"),
                "Founders": founders,
                "Industry": c.get("industries", []),
                "YC URL": c.get("url")
            }
            results.append(company_info)

    results.sort(key=lambda x: x["Company Name"].lower() if x["Company Name"] else "")

    output_filename = f"yc_startups_{target_batch}.json"
    with open(output_filename, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"Successfully saved data for {len(results)} companies to {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Y Combinator startups for a specific batch.")
    parser.add_argument("--batch", "-b", required=True, help="The YC batch to search for (e.g., W24, S24)")
    args = parser.parse_args()

    scrape_yc_startups(args.batch)
