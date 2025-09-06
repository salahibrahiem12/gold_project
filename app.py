import os
import io
import logging
import pandas as pd
import yfinance as yf
from prophet import Prophet
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from config import config

# Get configuration
config_name = os.getenv('FLASK_ENV', 'default')
app_config = config[config_name]

app = Flask(__name__)
app.config.from_object(app_config)

# Configure logging
logging.basicConfig(level=getattr(logging, app_config.LOG_LEVEL))
logger = logging.getLogger(__name__)

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

    # إذا سبق وحصلنا على التنبؤ قبل أقل من المدة المحددة، نعيده
    if _FORECAST is not None and _LAST_UPDATE is not None:
        if (datetime.now() - _LAST_UPDATE).total_seconds() < app_config.CACHE_DURATION_HOURS * 3600:
            return _FORECAST

    # 1. جلب البيانات
    try:
        logger.info("Fetching gold price data from yfinance...")
        df = yf.download(app_config.YFINANCE_SYMBOL, period=f'{app_config.DATA_PERIOD_YEARS}y', progress=False)
        if df.empty or len(df) < 10:
            logger.warning("Insufficient data from yfinance, using fallback data")
            # بيانات نموذجية عند الفشل
            dates = pd.date_range(end=datetime.now(), periods=500)
            prices = [1800 + i*5 + 20*(i % 7) for i in range(len(dates))]
            df = pd.DataFrame({'Date': dates, 'Close': prices}).set_index('Date')
        else:
            logger.info(f"Successfully fetched {len(df)} data points")
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
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
    future = model.make_future_dataframe(periods=app_config.FORECAST_PERIOD_DAYS)
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
    try:
        start = request.args.get('start_date')
        end   = request.args.get('end_date')
        
        # Validate input dates
        if not start or not end:
            return jsonify(status="error", message="Missing start_date or end_date parameters"), 400
        
        try:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
        except ValueError:
            return jsonify(status="error", message="Invalid date format. Use YYYY-MM-DD"), 400
        
        if start_date >= end_date:
            return jsonify(status="error", message="Start date must be before end date"), 400
        
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
    except Exception as e:
        logger.error(f"Error in api_forecast: {e}")
        return jsonify(status="error", message="Internal server error"), 500

@app.route('/export-excel')
def export_excel():
    """تصدير التنبؤات إلى ملف Excel"""
    try:
        start = request.args.get('start_date')
        end   = request.args.get('end_date')
        
        if not start or not end:
            return "Missing date parameters", 400
            
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
    except Exception as e:
        logger.error(f"Error in export_excel: {e}")
        return "Error generating export file", 500

@app.route('/export-csv')
def export_csv():
    """تصدير التنبؤات إلى ملف CSV"""
    try:
        start = request.args.get('start_date')
        end   = request.args.get('end_date')
        
        if not start or not end:
            return "Missing date parameters", 400
            
        fc = fetch_and_train_model()
        df = fc[(fc['ds'] >= start) & (fc['ds'] <= end)]
        
        if df.empty:
            return "لا توجد بيانات للتصدير.", 404

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        response = app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=gold_forecast_{start}_to_{end}.csv'}
        )
        return response
    except Exception as e:
        logger.error(f"Error in export_csv: {e}")
        return "Error generating CSV file", 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        fc = fetch_and_train_model()
        return jsonify({
            "status": "healthy",
            "last_update": _LAST_UPDATE.isoformat() if _LAST_UPDATE else None,
            "forecast_count": len(fc) if fc is not None else 0,
            "cache_age_hours": (datetime.now() - _LAST_UPDATE).total_seconds() / 3600 if _LAST_UPDATE else None
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    fetch_and_train_model()  # تهيئة أولية
    app.run(debug=app_config.DEBUG, port=app_config.PORT)