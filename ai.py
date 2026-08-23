def analyze_weather(
    temperature,
    humidity,
    wind_speed,
    weather,
    description=""
):

    weather = weather.lower()

    # Rain
    if "rain" in weather or "thunderstorm" in weather:

        return {
            "activity": "Indoor Games / Movies",
            "reason": "Rainy weather is not suitable for most outdoor activities.",
            "category": "Indoor"
        }

    # Snow
    if "snow" in weather:

        return {
            "activity": "Indoor Activities",
            "reason": "Cold snowy conditions are better suited for indoor activities.",
            "category": "Indoor"
        }

    # Very hot
    if temperature >= 35:

        return {
            "activity": "Indoor Activities",
            "reason": "The temperature is high. Avoid strenuous outdoor activities.",
            "category": "Indoor"
        }

    # Strong wind
    if wind_speed >= 8:

        return {
            "activity": "Indoor Activities",
            "reason": "Strong wind may make outdoor activities uncomfortable.",
            "category": "Indoor"
        }

    # Cold weather
    if temperature < 18:

        return {
            "activity": "Walking / Indoor Games",
            "reason": "The weather is cool. A short walk or indoor activity is suitable.",
            "category": "Mixed"
        }

    # Comfortable weather
    if 18 <= temperature <= 32:

        if humidity <= 75:

            return {
                "activity": "Walking / Cycling / Outdoor Sports",
                "reason": "The weather conditions are comfortable for outdoor activities.",
                "category": "Outdoor"
            }

        else:

            return {
                "activity": "Light Outdoor Activity",
                "reason": "Humidity is somewhat high, so choose a light outdoor activity.",
                "category": "Outdoor"
            }

    # Cloudy weather
    if "cloud" in weather:

        return {
            "activity": "Walking / Photography",
            "reason": "Cloudy weather can be comfortable for a short outdoor activity.",
            "category": "Outdoor"
        }

    # Default
    return {
        "activity": "Indoor / Outdoor Activity",
        "reason": "Weather conditions are moderate.",
        "category": "Mixed"
    }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    result = analyze_weather(
        temperature=31,
        humidity=65,
        wind_speed=3.2,
        weather="Clouds",
        description="scattered clouds"
    )

    print("WEATHER AI")
    print("=" * 40)
    print("Activity:", result["activity"])
    print("Reason:", result["reason"])
    print("Category:", result["category"])