import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

load_dotenv()

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")

def init():
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)

def get_campaigns():
    init()
    account = AdAccount(AD_ACCOUNT_ID)
    campaigns = account.get_campaigns(fields=[
        Campaign.Field.name,
        Campaign.Field.status,
        Campaign.Field.objective,
        Campaign.Field.daily_budget,
    ])
    return list(campaigns)

def get_insights(date_preset="last_7d"):
    init()
    account = AdAccount(AD_ACCOUNT_ID)
    insights = account.get_insights(params={
        "date_preset": date_preset,
        "level": "campaign",
    }, fields=[
        "campaign_name",
        "impressions",
        "clicks",
        "spend",
        "ctr",
        "cpc",
        "reach",
    ])
    return list(insights)

if __name__ == "__main__":
    print("=== 露思：META 廣告連線測試 ===")
    print(f"帳號：{AD_ACCOUNT_ID}\n")

    print("--- 活躍活動 ---")
    try:
        campaigns = get_campaigns()
        if campaigns:
            for c in campaigns:
                print(f"  {c['name']} | {c['status']}")
        else:
            print("  目前沒有活動")
    except Exception as e:
        print(f"  錯誤：{e}")

    print("\n--- 近 7 天成效 ---")
    try:
        insights = get_insights()
        if insights:
            for i in insights:
                print(f"  {i.get('campaign_name')} | 花費:{i.get('spend')} | CTR:{i.get('ctr')} | CPC:{i.get('cpc')}")
        else:
            print("  無成效資料")
    except Exception as e:
        print(f"  錯誤：{e}")
