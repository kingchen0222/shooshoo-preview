import os
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

def get_client():
    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(config)

def get_campaigns(customer_id):
    client = get_client()
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.ctr
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
          AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """
    response = ga_service.search(customer_id=customer_id, query=query)
    return list(response)

def get_keywords(customer_id):
    client = get_client()
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.ctr,
            metrics.average_cpc
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
          AND ad_group_criterion.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
        LIMIT 20
    """
    response = ga_service.search(customer_id=customer_id, query=query)
    return list(response)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    print("=== 智秀：Google Ads 連線測試 ===")
    print(f"帳號：{customer_id}\n")

    print("--- 活躍活動（近 30 天）---")
    try:
        rows = get_campaigns(customer_id)
        if rows:
            for row in rows:
                c = row.campaign
                m = row.metrics
                spend = m.cost_micros / 1_000_000
                print(f"  {c.name} | {c.status.name} | 花費:${spend:,.0f} | 點擊:{m.clicks:,} | CTR:{m.ctr*100:.2f}%")
        else:
            print("  目前沒有活動資料")
    except GoogleAdsException as e:
        for error in e.failure.errors:
            print(f"  錯誤：{error.message}")
