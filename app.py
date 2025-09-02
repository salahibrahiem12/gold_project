import os
import io
import pandas as pd
import yfinance as yf
from prophet import Prophet
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# كاش للتنبؤات
_FORECAST = None
_LAST_UPDATE = None

def fetch_and_train_model():
    """
    يجلب بيانات الذهب من yfinance، 
    يدرب Prophet، 
    يخرج تنبؤات 90 يومًا،
    ويخزنها لمدة ساعة.
    """
    global _FORECAST, _LAST_UPDATE

    # إذا سبق وحصلنا على التنبؤ قبل أقل من ساعة، نعيده
    if _FORECAST is not None and _LAST_UPDATE is not None:
        if (datetime.now() - _LAST_UPDATE).seconds < 3600:
            return _FORECAST

    # 1. جلب البيانات
    df = yf.download('GC=F', period='2y', progress=False)
    if df.empty or len(df) < 10:
        # بيانات نموذجية عند الفشل
        dates = pd.date_range(end=datetime.now(), periods=500)
        prices = [1800 + i*5 + 20*(i % 7) for i in range(len(dates))]
        df = pd.DataFrame({'Date': dates, 'Close': prices}).set_index('Date')

    df = df[['Close']].reset_index()
    df.columns = ['ds', 'y']

    # 2. تدريب النموذج
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df)

    # 3. إنتاج التنبؤ
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)

    # 4. تنقية التنبؤات المستقبلية
    fc = forecast[forecast['ds'] > datetime.now()][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    fc['ds'] = fc['ds'].dt.strftime('%Y-%m-%d')

    # 5. كاش وتاريخ
    _FORECAST = fc
    _LAST_UPDATE = datetime.now()
    return _FORECAST

@app.route('/')
def index():
    fc = fetch_and_train_model()
    df30 = fc.head(30)

    # إحصائيات المُلخص
    avg_price = df30['yhat'].mean().round(2)
    max_row   = df30.loc[df30['yhat'].idxmax()]
    min_row   = df30.loc[df30['yhat'].idxmin()]

    return render_template('gold_forecast.html',
        last_update=_LAST_UPDATE.strftime('%Y-%m-%d %H:%M'),
        forecast=df30.to_dict('records'),
        avg_price=avg_price,
        max_price=round(max_row['yhat'],2),
        min_price=round(min_row['yhat'],2),
        max_date=max_row['ds'],
        min_date=min_row['ds']
    )

@app.route('/api/forecast')
def api_forecast():
    """ترجع JSON للتنبؤات حسب فترة start_date و end_date"""
    start = request.args.get('start_date')
    end   = request.args.get('end_date')
    fc = fetch_and_train_model()

    df = fc[(fc['ds'] >= start) & (fc['ds'] <= end)]
    if df.empty:
        return jsonify(status="success", data=[], summary={})

    summary = {
        "avg_price": round(df['yhat'].mean(),2),
        "max_price": round(df['yhat'].max(),2),
        "min_price": round(df['yhat'].min(),2),
        "max_date": df.loc[df['yhat'].idxmax(), 'ds'],
        "min_date": df.loc[df['yhat'].idxmin(), 'ds']
    }
    return jsonify(status="success",
                   data=df.to_dict('records'),
                   summary=summary)

@app.route('/export-excel')
def export_excel():
    """تصدير التنبؤات إلى ملف Excel"""
    start = request.args.get('start_date')
    end   = request.args.get('end_date')
    fc = fetch_and_train_model()

    df = fc[(fc['ds'] >= start) & (fc['ds'] <= end)]
    if df.empty:
        return "لا توجد بيانات للتصدير.", 404

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Forecast', index=False)
    output.seek(0)
    filename = f"gold_forecast_{start}_to_{end}.xlsx"

    return send_file(output,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     download_name=filename)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    fetch_and_train_model()  # تهيئة أولية
    app.run(debug=True, port=5001)