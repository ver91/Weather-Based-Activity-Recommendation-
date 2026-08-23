import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
ewq4eaqa
# ==========================================================
# OPENWEATHER API KEY
# ==========================================================

API_KEY = "8f93b69527326e29e8f2ffd28bb6d0d1"

# N8N Webhook URL - YOUR ACTUAL URL
N8N_WEBHOOK_URL = "https://vermagg.app.n8n.cloud/webhook/d937d822-795b-4368-87b8-3ca303daef73"

BG_COLOR = "#EAF4FF"
HEADER_COLOR = "#1769AA"
HEADER_DARK = "#0D47A1"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1F2937"
SECONDARY_TEXT = "#64748B"

GREEN = "#16A34A"
RED = "#DC2626"
BLUE = "#2563EB"
PURPLE = "#7C3AED"
ORANGE = "#EA580C"

# ==========================================================
# LOCAL RECOMMENDATION LOGIC (FALLBACK)
# ==========================================================

def get_recommendation(temperature, humidity, wind_speed, weather):
    weather = weather.lower()

    if "rain" in weather or "thunderstorm" in weather:
        return ("Indoor Games / Movies", "Rainy weather is not suitable for most outdoor activities.")
    if "snow" in weather:
        return ("Indoor Activities", "Cold snowy conditions are better suited for indoor activities.")
    if temperature >= 35:
        return ("Indoor Activities", "The temperature is high. Avoid strenuous outdoor activities.")
    if wind_speed >= 8:
        return ("Indoor Activities", "Strong wind may make outdoor activities uncomfortable.")
    if temperature < 18:
        return ("Walking / Indoor Games", "The weather is cool. A short walk or indoor activity is suitable.")
    if 18 <= temperature <= 32:
        if humidity <= 75:
            return ("Walking / Cycling / Outdoor Sports", "The weather conditions are comfortable for outdoor activities.")
        else:
            return ("Light Outdoor Activity", "Humidity is somewhat high, so choose a light outdoor activity.")
    if "cloud" in weather:
        return ("Walking / Photography", "Cloudy weather can be comfortable for a short outdoor activity.")
    return ("Indoor / Outdoor Activity", "Weather conditions are moderate.")

# ==========================================================
# GET WEATHER - WITH N8N INTEGRATION
# ==========================================================

def get_weather():
    city = city_entry.get().strip()

    if city == "":
        messagebox.showwarning("Input Required", "Please enter a city name.")
        return

    # Variables for fallback
    temperature = None
    humidity = None
    wind_speed = None
    weather = None

    try:
        status_label.config(text="⏳ Getting weather data...", fg=BLUE)
        root.update()

        # 1. Get weather data from OpenWeather API
        url = "https://api.openweathermap.org/data/2.5/weather"
        parameters = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=parameters, timeout=10)
        data = response.json()

        if response.status_code != 200:
            messagebox.showerror("Weather Error", data.get("message", "Unable to get weather data."))
            status_label.config(text="Weather information not found.", fg=RED)
            return

        # Extract weather data
        city_name = data["name"]
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        weather = data["weather"][0]["main"]
        description = data["weather"][0]["description"]

        # Update UI with weather data
        city_result.config(text=f"📍 {city_name}")
        temperature_result.config(text=f"{temperature:.1f}°C")
        feels_result.config(text=f"Feels like {feels_like:.1f}°C")
        weather_result.config(text=weather)
        description_result.config(text=description.title())
        humidity_result.config(text=f"{humidity}%")
        wind_result.config(text=f"{wind_speed:.1f} m/s")

        # ==========================================================
        # 2. CALL N8N WEBHOOK - THIS IS THE CRITICAL PART
        # ==========================================================
        status_label.config(text="⏳ Getting AI recommendation from n8n...", fg=BLUE)
        root.update()

        n8n_payload = {
            "city": city_name,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "weather": weather,
            "description": description
        }

        # Try n8n first
        n8n_success = False
        activity = None
        reason = None
        
        try:
            print(f"📤 Calling n8n: {N8N_WEBHOOK_URL}")
            print(f"📤 Payload: {json.dumps(n8n_payload, indent=2)}")
            
            n8n_response = requests.post(N8N_WEBHOOK_URL, json=n8n_payload, timeout=15)
            
            print(f"📥 Response Status: {n8n_response.status_code}")
            print(f"📥 Response Body: {n8n_response.text}")
            
            if n8n_response.status_code == 200:
                n8n_result = n8n_response.json()
                
                # Extract recommendation from n8n response
                if 'recommendation' in n8n_result:
                    rec = n8n_result['recommendation']
                    activity = rec.get('activity', 'No recommendation')
                    reason = rec.get('reason', '')
                    method = rec.get('method', 'n8n-ai')
                elif 'activity' in n8n_result:
                    activity = n8n_result.get('activity', 'No recommendation')
                    reason = n8n_result.get('reason', '')
                    method = n8n_result.get('method', 'n8n-ai')
                else:
                    # Fallback: try to find any string that looks like an activity
                    if isinstance(n8n_result, dict):
                        # Check common response formats
                        for key in ['result', 'message', 'suggestion', 'recommendation']:
                            if key in n8n_result:
                                if isinstance(n8n_result[key], str):
                                    activity = n8n_result[key]
                                    reason = f"From n8n: {key}"
                                    break
                                elif isinstance(n8n_result[key], dict) and 'activity' in n8n_result[key]:
                                    activity = n8n_result[key]['activity']
                                    reason = n8n_result[key].get('reason', '')
                                    break
                        else:
                            activity = "Recommendation from n8n"
                            reason = f"Response: {str(n8n_result)[:100]}"
                    else:
                        activity = str(n8n_result)[:50]
                        reason = "Response from n8n"
                    method = 'n8n'
                
                n8n_success = True
                status_label.config(text=f"✓ AI recommendation from n8n!", fg=GREEN)
            else:
                print(f"⚠️ n8n returned non-200 status: {n8n_response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⚠️ n8n request timed out")
        except requests.exceptions.ConnectionError:
            print("⚠️ Cannot connect to n8n (network error)")
        except Exception as e:
            print(f"⚠️ n8n error: {e}")

        # ==========================================================
        # 3. USE N8N RESULT OR FALLBACK TO LOCAL
        # ==========================================================
        if n8n_success and activity:
            # Use n8n recommendation
            activity_result.config(text=f"🏆 {activity}")
            reason_result.config(text=reason if reason else "Recommendation from n8n AI")
        else:
            # Use local recommendation as fallback
            activity, reason = get_recommendation(temperature, humidity, wind_speed, weather)
            activity_result.config(text=f"🏆 {activity}")
            reason_result.config(text=reason)
            status_label.config(text="⚠️ Using local recommendation (n8n unavailable)", fg=ORANGE)

    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection Error", "Please check your internet connection.")
        status_label.config(text="No internet connection. Using local recommendation.", fg=ORANGE)
        
        if temperature is not None:
            activity, reason = get_recommendation(temperature, humidity, wind_speed, weather)
            activity_result.config(text=f"🏆 {activity}")
            reason_result.config(text=reason)

    except requests.exceptions.Timeout:
        messagebox.showerror("Timeout", "The request took too long. Using local recommendation.")
        status_label.config(text="Request timed out. Using local recommendation.", fg=ORANGE)
        
        if temperature is not None:
            activity, reason = get_recommendation(temperature, humidity, wind_speed, weather)
            activity_result.config(text=f"🏆 {activity}")
            reason_result.config(text=reason)

    except Exception as error:
        messagebox.showerror("Error", f"Something went wrong: {str(error)}")
        status_label.config(text="Error occurred.", fg=RED)

# ==========================================================
# CLEAR SCREEN
# ==========================================================

def clear_screen():
    city_entry.delete(0, tk.END)
    city_result.config(text="📍 City")
    temperature_result.config(text="--°C")
    feels_result.config(text="Feels like --°C")
    weather_result.config(text="Weather")
    description_result.config(text="Weather description")
    humidity_result.config(text="--%")
    wind_result.config(text="-- m/s")
    activity_result.config(text="🏆 Recommended Activity")
    reason_result.config(text="Enter a city to get a smart activity recommendation.")
    status_label.config(text="")

# ==========================================================
# ENTER KEY
# ==========================================================

def enter_pressed(event):
    get_weather()

# ==========================================================
# MAIN WINDOW
# ==========================================================

root = tk.Tk()
root.title("Weather-Based Activity Recommendation System")
root.state("zoomed")
root.configure(bg=BG_COLOR)
root.resizable(True, True)

# ==========================================================
# STYLE
# ==========================================================

style = ttk.Style()
style.theme_use("clam")
style.configure("Search.TEntry", padding=12, font=("Segoe UI", 14))

# ==========================================================
# HEADER
# ==========================================================

header = tk.Frame(root, bg=HEADER_COLOR, height=130)
header.pack(fill="x")
header.pack_propagate(False)

header_left = tk.Frame(header, bg=HEADER_COLOR)
header_left.pack(side="left", padx=45, pady=20)

tk.Label(header_left, text="🌦", font=("Segoe UI Emoji", 42), bg=HEADER_COLOR, fg="white").pack(side="left", padx=(0, 15))

title_box = tk.Frame(header_left, bg=HEADER_COLOR)
title_box.pack(side="left")

tk.Label(title_box, text="WEATHER ACTIVITY", font=("Segoe UI", 24, "bold"), bg=HEADER_COLOR, fg="white").pack(anchor="w")
tk.Label(title_box, text="Smart Weather-Based Activity Recommendation", font=("Segoe UI", 11), bg=HEADER_COLOR, fg="#DCEEFF").pack(anchor="w")

tk.Label(header, text="N8N INTEGRATION", font=("Segoe UI", 11, "bold"), bg=HEADER_COLOR, fg="#DCEEFF").pack(side="right", padx=45)

# ==========================================================
# SEARCH AREA
# ==========================================================

search_outer = tk.Frame(root, bg=BG_COLOR)
search_outer.pack(pady=25)

tk.Label(search_outer, text="Search Weather", font=("Segoe UI", 18, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(0, 10))

search_frame = tk.Frame(search_outer, bg="white", bd=1, relief="solid")
search_frame.pack()

tk.Label(search_frame, text="📍", font=("Segoe UI Emoji", 18), bg="white").pack(side="left", padx=(15, 5))

city_entry = ttk.Entry(search_frame, width=32, style="Search.TEntry")
city_entry.pack(side="left", padx=5, pady=5)
city_entry.bind("<Return>", enter_pressed)

check_button = tk.Button(search_frame, text="  CHECK WEATHER  ", font=("Segoe UI", 12, "bold"), bg=HEADER_COLOR, fg="white", activebackground=HEADER_DARK, activeforeground="white", relief="flat", cursor="hand2", padx=15, pady=12, command=get_weather)
check_button.pack(side="left", padx=5)

clear_button = tk.Button(search_frame, text="CLEAR", font=("Segoe UI", 11, "bold"), bg="#F1F5F9", fg=TEXT_COLOR, activebackground="#E2E8F0", relief="flat", cursor="hand2", padx=15, pady=12, command=clear_screen)
clear_button.pack(side="left", padx=(5, 10))

# ==========================================================
# CURRENT LOCATION
# ==========================================================

city_result = tk.Label(root, text="📍 City", font=("Segoe UI", 22, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
city_result.pack(pady=(5, 15))

# ==========================================================
# MAIN WEATHER CARD
# ==========================================================

main_card = tk.Frame(root, bg=CARD_COLOR, bd=0, highlightbackground="#D5E3F0", highlightthickness=1)
main_card.pack(padx=80, fill="x")

# Temperature
temperature_frame = tk.Frame(main_card, bg=CARD_COLOR)
temperature_frame.pack(side="left", expand=True, fill="both", padx=20, pady=25)

tk.Label(temperature_frame, text="CURRENT TEMPERATURE", font=("Segoe UI", 10, "bold"), bg=CARD_COLOR, fg=SECONDARY_TEXT).pack()
temperature_result = tk.Label(temperature_frame, text="--°C", font=("Segoe UI", 42, "bold"), bg=CARD_COLOR, fg=HEADER_COLOR)
temperature_result.pack(pady=5)
feels_result = tk.Label(temperature_frame, text="Feels like --°C", font=("Segoe UI", 11), bg=CARD_COLOR, fg=SECONDARY_TEXT)
feels_result.pack()

# Condition
condition_frame = tk.Frame(main_card, bg=CARD_COLOR)
condition_frame.pack(side="left", expand=True, fill="both", padx=20, pady=25)

tk.Label(condition_frame, text="CONDITION", font=("Segoe UI", 10, "bold"), bg=CARD_COLOR, fg=SECONDARY_TEXT).pack()
weather_result = tk.Label(condition_frame, text="Weather", font=("Segoe UI", 24, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
weather_result.pack(pady=8)
description_result = tk.Label(condition_frame, text="Weather description", font=("Segoe UI", 11), bg=CARD_COLOR, fg=SECONDARY_TEXT)
description_result.pack()

# Humidity
humidity_frame = tk.Frame(main_card, bg="#F0FDF4")
humidity_frame.pack(side="left", expand=True, fill="both", padx=10, pady=20)

tk.Label(humidity_frame, text="💧", font=("Segoe UI Emoji", 22), bg="#F0FDF4").pack(pady=(10, 0))
tk.Label(humidity_frame, text="HUMIDITY", font=("Segoe UI", 10, "bold"), bg="#F0FDF4", fg=SECONDARY_TEXT).pack()
humidity_result = tk.Label(humidity_frame, text="--%", font=("Segoe UI", 22, "bold"), bg="#F0FDF4", fg=GREEN)
humidity_result.pack(pady=(5, 15))

# Wind
wind_frame = tk.Frame(main_card, bg="#FFF7ED")
wind_frame.pack(side="left", expand=True, fill="both", padx=10, pady=20)

tk.Label(wind_frame, text="💨", font=("Segoe UI Emoji", 22), bg="#FFF7ED").pack(pady=(10, 0))
tk.Label(wind_frame, text="WIND SPEED", font=("Segoe UI", 10, "bold"), bg="#FFF7ED", fg=SECONDARY_TEXT).pack()
wind_result = tk.Label(wind_frame, text="-- m/s", font=("Segoe UI", 22, "bold"), bg="#FFF7ED", fg=ORANGE)
wind_result.pack(pady=(5, 15))

# ==========================================================
# RECOMMENDATION SECTION
# ==========================================================

recommendation_outer = tk.Frame(root, bg=BG_COLOR)
recommendation_outer.pack(padx=80, pady=25, fill="x")

recommendation_frame = tk.Frame(recommendation_outer, bg="#ECFDF5", bd=0, highlightbackground="#A7F3D0", highlightthickness=1)
recommendation_frame.pack(fill="x")

tk.Label(recommendation_frame, text="💡", font=("Segoe UI Emoji", 32), bg="#ECFDF5").pack(side="left", padx=30)

recommendation_content = tk.Frame(recommendation_frame, bg="#ECFDF5")
recommendation_content.pack(side="left", fill="both", expand=True, pady=20)

tk.Label(recommendation_content, text="SMART ACTIVITY RECOMMENDATION", font=("Segoe UI", 10, "bold"), bg="#ECFDF5", fg=GREEN).pack(anchor="w")
activity_result = tk.Label(recommendation_content, text="🏆 Recommended Activity", font=("Segoe UI", 20, "bold"), bg="#ECFDF5", fg="#166534")
activity_result.pack(anchor="w", pady=5)
reason_result = tk.Label(recommendation_content, text="Enter a city to get a smart activity recommendation.", font=("Segoe UI", 11), bg="#ECFDF5", fg="#475569", wraplength=1000, justify="left")
reason_result.pack(anchor="w")

# ==========================================================
# STATUS
# ==========================================================

status_label = tk.Label(root, text="Ready — enter a city to check live weather.", font=("Segoe UI", 10), bg=BG_COLOR, fg=SECONDARY_TEXT)
status_label.pack(pady=(0, 15))

# ==========================================================
# FOOTER
# ==========================================================

footer = tk.Frame(root, bg="#E2ECF5")
footer.pack(side="bottom", fill="x")

tk.Label(footer, text="Weather-Based Activity Recommendation System  •  Powered by OpenWeather API & n8n", font=("Segoe UI", 9), bg="#E2ECF5", fg=SECONDARY_TEXT).pack(pady=8)

# ==========================================================
# START APPLICATION
# ==========================================================

root.mainloop()