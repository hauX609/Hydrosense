import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, List

class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1"
    
    async def get_live_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch live weather data for prediction form auto-fill.
        Calculates precipitation totals for 1, 3, 7, and 14 days.
        """
        # Get past 14 days of data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=14)
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "precipitation_sum",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            # Fetch weather data
            weather_response = await client.get(f"{self.BASE_URL}/forecast", params=params)
            weather_data = weather_response.json()
            
            # Fetch elevation
            elevation_response = await client.get(
                f"{self.BASE_URL}/elevation", 
                params={"latitude": lat, "longitude": lon}
            )
            elevation_data = elevation_response.json()
            
        # Process precipitation data
        daily_precip = weather_data.get("daily", {}).get("precipitation_sum", [])
        # Reverse to get most recent first
        daily_precip = list(reversed(daily_precip))
        
        return {
            "elevation": elevation_data.get("elevation", [0])[0],
            "precip_1d": sum(daily_precip[:1]),
            "precip_3d": sum(daily_precip[:3]),
            "precip_7d": sum(daily_precip[:7]),
            "precip_14d": sum(daily_precip[:14]),
            # Default values for fields we can't easily get
            "slope": 0.5,  # Placeholder
            "landcover": 11,  # Placeholder
            "dis_last": 1500.0,  # Placeholder
            "dis_trend_3": 50.0  # Placeholder
        }

    async def get_historical_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch historical weather data for trends chart.
        Gets last 30 days of precipitation and max temperature.
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["precipitation_sum", "temperature_2m_max"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/forecast", params=params)
            data = response.json()
            
        return {
            "dates": data.get("daily", {}).get("time", []),
            "precipitation": data.get("daily", {}).get("precipitation_sum", []),
            "temperature": data.get("daily", {}).get("temperature_2m_max", [])
        }

weather_service = WeatherService()
