# Gold Price Forecasting Application

A web application that predicts gold prices using Facebook Prophet time series forecasting model. The application provides an interactive web interface with Arabic RTL support for viewing and exporting gold price forecasts.

## Features

- **Real-time Gold Price Forecasting**: Uses Prophet model to predict gold prices up to 90 days ahead
- **Interactive Web Interface**: Modern, responsive design with Arabic RTL support
- **Multiple Export Formats**: Export forecasts to Excel (.xlsx) or CSV formats
- **Date Range Filtering**: Filter forecasts by custom date ranges with preset options
- **Data Visualization**: Interactive charts showing price trends and confidence intervals
- **Caching System**: Intelligent caching to improve performance and reduce API calls
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Health Monitoring**: Built-in health check endpoint for monitoring

## Technology Stack

- **Backend**: Python Flask
- **Forecasting**: Facebook Prophet
- **Data Source**: Yahoo Finance (yfinance)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Visualization**: Plotly.js
- **Data Processing**: Pandas, NumPy

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd gold_project
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser and navigate to `http://localhost:5001`

## Configuration

The application uses environment variables for configuration. Create a `.env` file or set environment variables:

```bash
# Cache settings
CACHE_DURATION_HOURS=1

# Forecast settings
FORECAST_PERIOD_DAYS=90
DATA_PERIOD_YEARS=2

# API settings
YFINANCE_SYMBOL=GC=F

# Exchange rates
USD_TO_EGP_RATE=48.5

# Flask settings
FLASK_ENV=development
DEBUG=True
PORT=5001
LOG_LEVEL=INFO
```

## API Endpoints

### Web Interface
- `GET /` - Main application interface

### API Endpoints
- `GET /api/forecast?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Get forecast data
- `GET /export-excel?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Export to Excel
- `GET /export-csv?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Export to CSV
- `GET /health` - Health check endpoint

## Usage

### Web Interface

1. **Select Date Range**: Use the date pickers or preset buttons (1 week, 2 weeks, 1 month, etc.)
2. **View Forecasts**: The application displays:
   - Interactive price chart with confidence intervals
   - Data table with daily forecasts
   - Summary statistics (average, max, min prices)
3. **Export Data**: Download forecasts in Excel or CSV format
4. **Print Reports**: Use the print button for hard copies

### API Usage

```python
import requests

# Get forecast data
response = requests.get('http://localhost:5001/api/forecast', params={
    'start_date': '2024-01-01',
    'end_date': '2024-01-31'
})
data = response.json()

# Export to Excel
excel_url = 'http://localhost:5001/export-excel?start_date=2024-01-01&end_date=2024-01-31'
```

## Project Structure

```
gold_project/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── forecast.py           # Standalone forecasting module (unused)
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   ├── css/
│   │   └── style.css    # Application styles
│   └── js/
│       └── script.js    # Frontend JavaScript
├── templates/
│   └── gold_forecast.html # Main HTML template
└── gold_forecast.csv    # Sample forecast data
```

## Key Improvements Made

### 1. **Bug Fixes**
- Fixed cache timing bug (used `total_seconds()` instead of `seconds`)
- Added proper error handling for API failures
- Improved input validation for date ranges

### 2. **Performance Enhancements**
- Added configuration management system
- Implemented proper logging
- Added health check endpoint for monitoring

### 3. **User Experience**
- Enhanced error messages with Arabic support
- Added input validation on frontend
- Improved loading states and user feedback
- Added CSV export option alongside Excel

### 4. **Code Quality**
- Separated configuration from main code
- Added comprehensive error handling
- Improved code documentation
- Added proper logging system

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Running in Production Mode

```bash
export FLASK_ENV=production
python app.py
```

### Testing

The application includes a health check endpoint for monitoring:

```bash
curl http://localhost:5001/health
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **Port Already in Use**: Change the port in configuration or kill the process using the port

3. **Data Fetching Issues**: The application includes fallback data when Yahoo Finance is unavailable

4. **Memory Issues**: The application uses caching to reduce memory usage. Restart the application if needed.

### Logs

Check the console output for detailed logs. The application logs:
- Data fetching operations
- Model training progress
- API requests and errors
- Cache operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue in the repository

## Future Enhancements

Potential improvements for future versions:
- Multiple currency support
- Historical data visualization
- Model accuracy metrics
- Price alerts and notifications
- User authentication and saved preferences
- Real-time data updates
- Mobile app version
- Advanced charting options
