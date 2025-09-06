import streamlit as st
import pandas as pd
import yfinance as yf
from prophet import Prophet
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(
    page_title="Gold Price Forecast",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Gold Price Forecasting")
st.markdown("Predict gold prices using Prophet time series forecasting")

# Cache the model
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_forecast():
    try:
        # Fetch data
        df = yf.download('GC=F', period='2y', progress=False)
        if df.empty:
            return None, "No data available"
        
        # Prepare data
        df = df[['Close']].reset_index()
        df.columns = ['ds', 'y']
        
        # Train model
        model = Prophet(daily_seasonality=True, yearly_seasonality=True)
        model.fit(df)
        
        # Make forecast
        future = model.make_future_dataframe(periods=90)
        forecast = model.predict(future)
        
        # Filter future predictions
        future_forecast = forecast[forecast['ds'] > datetime.now()]
        return future_forecast, None
    except Exception as e:
        return None, str(e)

# Get forecast
forecast, error = get_forecast()

if error:
    st.error(f"Error: {error}")
else:
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() + timedelta(days=1))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date() + timedelta(days=30))
    
    # Filter data
    filtered_data = forecast[
        (forecast['ds'].dt.date >= start_date) & 
        (forecast['ds'].dt.date <= end_date)
    ]
    
    if not filtered_data.empty:
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"${filtered_data['yhat'].mean():.2f}")
        with col2:
            st.metric("Max Price", f"${filtered_data['yhat'].max():.2f}")
        with col3:
            st.metric("Min Price", f"${filtered_data['yhat'].min():.2f}")
        
        # Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_data['ds'],
            y=filtered_data['yhat'],
            mode='lines+markers',
            name='Predicted Price',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=filtered_data['ds'],
            y=filtered_data['yhat_lower'],
            mode='lines',
            name='Lower Bound',
            line=dict(dash='dash', color='red'),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=filtered_data['ds'],
            y=filtered_data['yhat_upper'],
            mode='lines',
            name='Upper Bound',
            line=dict(dash='dash', color='red'),
            fill='tonexty',
            fillcolor='rgba(255,0,0,0.1)'
        ))
        
        fig.update_layout(
            title="Gold Price Forecast",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Forecast Data")
        display_data = filtered_data[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        display_data.columns = ['Date', 'Predicted Price', 'Lower Bound', 'Upper Bound']
        display_data['Date'] = display_data['Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_data, use_container_width=True)
        
        # Download button
        csv = display_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"gold_forecast_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available for the selected date range")
