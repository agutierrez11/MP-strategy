import os
import requests, json, time

token = os.getenv("APIFY_API_TOKEN", "")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Run actor compass/crawler-google-places
actor_id = "compass~crawler-google-places"
run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?waitForFinish=120"

run_input = {
    "searchStringsArray": ["ferreteria Puerto Peñasco Sonora"],
    "maxCrawledPlacesPerSearch": 3,
    "language": "es",
    "scrapeResponseFromOwnerText": False,
    "scrapeReviewsPersonalData": False,
    "reviewsSort": "newest",
    "maxReviews": 0,
    "maxImages": 0
}

print("Starting test run on Apify...")
res = requests.post(run_url, headers=headers, json=run_input)
print("Run response status:", res.status_code)

if res.status_code in [200, 201]:
    data = res.json().get("data", {})
    run_id = data.get("id")
    dataset_id = data.get("defaultDatasetId")
    status = data.get("status")
    usage_usd = data.get("usageTotalUsd")
    print(f"Run ID: {run_id} | Status: {status} | Usage: ${usage_usd:.4f} USD")
    
    # Fetch results from dataset
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    d_res = requests.get(dataset_url, headers=headers)
    items = d_res.json()
    print(f"Fetched {len(items)} items from dataset:")
    for idx, item in enumerate(items, 1):
        print(f"\n--- Item #{idx} ---")
        print("Title:", item.get("title"))
        print("Phone:", item.get("phone"))
        print("Address:", item.get("address"))
        print("Rating:", item.get("totalScore"), f"({item.get('reviewsCount')} reviews)")
        print("Website:", item.get("website"))
        print("Category:", item.get("categoryName"))
else:
    print("Error:", res.text)
