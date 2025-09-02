import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta

# سعر التحويل من الدولار للجنيه المصري
EXCHANGE_RATE = 48.5  # مثال، غيّره حسب السعر الحالي

def run_forecast(start_date_str, end_date_str):
    # 1. تحميل البيانات التاريخية
    df = pd.read_csv("data/gold.csv")  # لازم يكون عندك الملف ده
    df.rename(columns={'Date': 'ds', 'Price': 'y'}, inplace=True)
    df['ds'] = pd.to_datetime(df['ds'])

    # 2. تدريب النموذج
    model = Prophet()
    model.fit(df)

    # 3. توليد تواريخ التنبؤ المطلوبة
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    days = (end_date - start_date).days + 1

    future = model.make_future_dataframe(periods=days)
    future = future[future['ds'] >= start_date]  # فلترة من أول التاريخ المحدد

    # 4. الحصول على التوقعات
    forecast = model.predict(future)

    # 5. تجهيز النتيجة
    results = []
    for _, row in forecast.iterrows():
        date = row['ds'].strftime('%Y-%m-%d')
        price_usd = row['yhat']
        price_egp = price_usd * EXCHANGE_RATE
        price_per_gram_egp = price_egp / 31.1  # تحويل من أونصة لجرام

        results.append({
            "ds": date,
            "yhat": round(price_usd, 2),
            "yhat_egp": round(price_egp, 2),
            "price_per_gram_egp": round(price_per_gram_egp, 2)
        })

    return results
