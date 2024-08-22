import httpx

async def get_weather(location: str, unit: str = "celsius"):
    """
    Get the current weather for a given location.
    
    :param location: City name (e.g., "London", "New York")
    :param unit: Temperature unit, either "celsius" or "fahrenheit"
    :return: A string describing the current weather
    """
    api_key = "your_weather_api_key_here"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric" if unit == "celsius" else "imperial"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        data = response.json()
    
    if response.status_code == 200:
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The current weather in {location} is {temp}°{'C' if unit == 'celsius' else 'F'} with {description}."
    else:
        return f"Sorry, I couldn't retrieve the weather information for {location}."