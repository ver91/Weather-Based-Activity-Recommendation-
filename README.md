# 🌦️ Weather-Based Activity Recommendation System

A smart Python-based application that analyzes **live weather conditions** and recommends suitable activities based on temperature, humidity, wind speed, and weather conditions.

The system combines a **Tkinter graphical user interface**, **OpenWeather API**, **Machine Learning using Logistic Regression**, and **rule-based fallback logic** to generate activity recommendations.

---

## 1. Problem Statement

Weather conditions can significantly affect the suitability of outdoor and indoor activities.

Users may find it difficult to decide whether conditions are appropriate for activities such as:

* Walking
* Cycling
* Outdoor Sports
* Photography
* Indoor Games
* Movies
* Other indoor activities

A weather-based intelligent system can analyze current weather information and provide suitable activity recommendations.

The system can:

* Retrieve live weather information.
* Analyze temperature, humidity, wind speed, and weather conditions.
* Use a Machine Learning model to predict suitable activities.
* Provide rule-based recommendations when the ML model is unavailable.
* Display the results through a user-friendly Tkinter interface.

---

## 2. Proposed Solution

The proposed system follows these steps:

1. User enters a city name.
2. The system retrieves live weather data using the OpenWeather API.
3. Weather information is processed.
4. Relevant weather features are prepared.
5. The trained Machine Learning model predicts a suitable activity.
6. The system generates an activity recommendation.
7. The recommendation and weather information are displayed through the GUI.

The system also includes a rule-based fallback mechanism so that recommendations can still be generated when the ML model or encoder files are unavailable.

---

## 3. Process Flow

```text
Start
  ↓
Enter City Name
  ↓
Validate Input
  ↓
Fetch Live Weather Data
  ↓
Process Weather Information
  ↓
Prepare Weather Features
  ↓
ML Prediction
  ↓
Determine Suitable Activity
  ↓
Generate Recommendation
  ↓
Display Weather + Activity
  ↓
End
```

---

## 4. Project Mapping

| V-Model Stage        | Weather Activity Recommendation Project                       |
| -------------------- | ------------------------------------------------------------- |
| Requirement Analysis | Identify the need for weather-based activity recommendations  |
| System Design        | Design system architecture and Tkinter interface              |
| Implementation       | Develop Python + ML application                               |
| Integration          | Integrate Tkinter, OpenWeather API, ML model and n8n/Flask    |
| Testing              | Test weather retrieval, prediction and recommendation modules |
| Validation           | Check system against requirements                             |
| Demonstration        | Present the working weather recommendation system             |

---

# 5. Project – Modular Application Development

The project is divided into separate modules and functions.

### Main Modules

* Weather data collection
* Weather analysis
* Activity recommendation
* Machine Learning prediction
* Model loading
* Tkinter GUI
* n8n integration
* Flask webhook API

### Important Functions

```text
get_weather()
get_recommendation()
analyze_weather()
predict()
rule_based_predict()
get_weather_and_recommend()
batch_analyze()
handle_webhook()
create_flask_app()
clear_screen()
```

The GUI retrieves weather information and passes the relevant values to the recommendation engine.

---

# 6. Requirement Analysis

## 6.1 Functional Requirements

The system should:

* Accept a city name from the user.
* Validate the city input.
* Retrieve live weather information.
* Display current temperature.
* Display feels-like temperature.
* Display humidity.
* Display wind speed.
* Display weather condition.
* Display weather description.
* Process weather information.
* Apply the trained ML model.
* Predict a suitable activity.
* Generate an activity recommendation.
* Provide rule-based fallback recommendations.
* Display results through the GUI.
* Handle invalid city names.
* Handle network errors.
* Handle API timeout errors.
* Provide a Clear option.
* Support Enter-key weather search.

---

## 6.2 Non-Functional Requirements

The application should be:

* User-friendly
* Easy to understand
* Fast in generating recommendations
* Reliable
* Maintainable
* Scalable
* Easy to test
* Responsive
* Capable of handling network failures
* Secure with respect to API credentials and user data

---

## 6.3 Identify the User

Primary users may include:

* Students
* General users
* Travelers
* Outdoor activity enthusiasts
* Fitness enthusiasts
* Faculty and project demonstrators

---

## 6.4 User Requirement

The user should be able to:

* Enter a city name.
* Search for current weather.
* View live weather conditions.
* Understand the current weather situation.
* View a recommended activity.
* Understand why the activity was recommended.
* Clear the displayed information.
* Search again for another city.

---

## 6.5 Identify System Inputs

The system uses the following weather information:

* City Name
* Temperature
* Feels-like Temperature
* Humidity
* Wind Speed
* Weather Condition
* Weather Description

The OpenWeather API response is processed to obtain these values.

For ML prediction, the system uses weather-related features including:

* Temperature
* Humidity
* Wind Speed
* Encoded Weather Condition
* Rain indicator
* Snow indicator
* Clear-weather indicator
* Cloudy-weather indicator
* Foggy-weather indicator

These features are prepared during model training.

---

# 6.6 Identify System Outputs

## 6.6.1 Weather Information

The application displays:

* City
* Current Temperature
* Feels-like Temperature
* Weather Condition
* Weather Description
* Humidity
* Wind Speed

The Tkinter interface contains dedicated sections for these weather values.

---

## 6.6.2 Activity Recommendation

Possible recommendations include:

* Indoor Games / Movies
* Indoor Activities
* Walking / Indoor Games
* Walking / Cycling / Outdoor Sports
* Light Outdoor Activity
* Walking / Photography
* Indoor / Outdoor Activity

The recommendation is determined using weather conditions and environmental factors.

---

## 6.6.3 Additional Output

The ML integration can provide:

* Recommended Activity
* Prediction Confidence
* Prediction Probabilities
* Prediction Method

The prediction result identifies whether the result came from the **ML Model** or the **Rule-Based fallback**.

### Example

```text
City: Chennai

Temperature: 29°C
Humidity: 65%
Wind Speed: 3 m/s
Weather: Clear

Recommended Activity:
Walking / Cycling / Outdoor Sports
```

---

# 7. Objective

The main objectives of the project are:

* Understand the fundamentals of Machine Learning.
* Understand weather-based decision-making.
* Work with datasets using Pandas and NumPy.
* Perform data preprocessing.
* Perform feature engineering.
* Encode categorical weather conditions.
* Train a Machine Learning model.
* Evaluate the trained model.
* Save the trained model using pickle.
* Retrieve real-time weather information using an API.
* Integrate Machine Learning with a Tkinter GUI.
* Generate suitable activity recommendations.
* Implement a rule-based fallback mechanism.
* Understand API integration.
* Understand Flask and n8n integration.

---

# 8. From Requirements to System Design

## 8.1 Inputs

```text
City Name
Temperature
Humidity
Wind Speed
Weather Condition
Weather Description
```

---

## 8.2 Processing

```text
Validate City
      ↓
Fetch Weather API Data
      ↓
Extract Weather Information
      ↓
Preprocess Features
      ↓
Encode Weather Condition
      ↓
ML Prediction
      ↓
Generate Activity Recommendation
      ↓
Display Result
```

---

## 8.3 Outputs

```text
Current Weather
Temperature
Humidity
Wind Speed
Weather Condition
Recommended Activity
Recommendation Reason
Prediction Confidence
```

---

# 9. Proposed System Architecture

```text
                 Tkinter GUI
                     ↓
              Enter City Name
                     ↓
              Input Validation
                     ↓
             OpenWeather API
                     ↓
             Weather Data
                     ↓
           Data Processing
                     ↓
        Feature Engineering
                     ↓
          ML Prediction Engine
                     ↓
       ┌─────────────┴─────────────┐
       ↓                           ↓
  ML Prediction             Rule-Based Fallback
       ↓                           ↓
       └─────────────┬─────────────┘
                     ↓
          Activity Recommendation
                     ↓
              Result Display
```

---

## Architecture Components

### Tkinter UI

Provides the graphical interface for entering the city and displaying weather and recommendation results.

### Input Validation

Checks whether a city name has been entered before requesting weather data.

### OpenWeather API

Retrieves live weather information for the requested city.

### Data Processing

Extracts temperature, humidity, wind speed, weather condition, and description.

### Feature Engineering

Converts weather conditions into numerical and binary features for the ML model.

### ML Prediction Engine

Uses the trained Logistic Regression model to predict a suitable activity.

### Rule-Based Fallback

Provides recommendations when the ML model or encoder files are unavailable.

### Result Display

Displays the current weather information and recommended activity in the Tkinter interface.

---

# 10. UI Design Requirements

The application contains the following sections.

## 10.1 Header Section

Displays:

* Weather icon
* Application title
* Application description
* Live Weather indicator

---

## 10.2 Search Section

Contains:

* City input field
* Check Weather button
* Clear button

The Enter key can also be used to initiate the weather search.

---

## 10.3 Weather Information Section

Displays:

### Temperature

* Current temperature
* Feels-like temperature

### Weather Condition

* Main weather condition
* Weather description

### Humidity

* Humidity percentage

### Wind

* Wind speed in m/s

---

## 10.4 Recommendation Section

Displays:

* Recommended activity
* Reason for recommendation

The GUI contains a dedicated smart activity recommendation section.

---

## 10.5 Status Section

Displays the current application status, such as:

```text
Ready — enter a city to check live weather.
```

or

```text
✓ Live weather updated successfully
```

---

# 11. Using Frames

Frames are used to organize the GUI into separate sections.

```text
Main Window
│
├── Header Frame
│
├── Search Frame
│
├── Current Location
│
├── Main Weather Card
│   ├── Temperature
│   ├── Weather Condition
│   ├── Humidity
│   └── Wind Speed
│
├── Recommendation Frame
│
├── Status Frame
│
└── Footer Frame
```

The main Tkinter window uses separate frames for the header, search area, weather information and recommendation section.

---

# 12. Workflow

```text
User enters city
        ↓
User clicks Check Weather
        ↓
Button callback executes
        ↓
Weather API request is sent
        ↓
Weather data is received
        ↓
Weather values are extracted
        ↓
ML / Rule-Based prediction executes
        ↓
Activity is selected
        ↓
Recommendation is generated
        ↓
Result is displayed
```

The `get_weather()` function sends a request to the OpenWeather endpoint and extracts the weather values before calling the recommendation function.

---

# 13. Machine Learning Integration

## 13.1 Traditional Rule-Based System vs Machine Learning

| Traditional Rule-Based System      | Machine Learning System                 |
| ---------------------------------- | --------------------------------------- |
| Rules are manually defined         | Model learns patterns from data         |
| Fixed thresholds                   | Learns relationships from training data |
| Example: temperature ≥ 35 → Indoor | Model predicts activity from features   |
| Easy to understand                 | More adaptive                           |
| Limited flexibility                | Can improve with more data              |

The project maintains rule-based logic as a fallback while also supporting a trained ML model.

---

# 14. ML Workflow

```text
Weather Activity Dataset
          ↓
Data Loading
          ↓
Data Preprocessing
          ↓
Feature Engineering
          ↓
Label Encoding
          ↓
Feature Selection
          ↓
Train-Test Split
          ↓
Logistic Regression
          ↓
Model Evaluation
          ↓
Save Model
          ↓
Prediction
```

---

# 15. Dataset

The training dataset is loaded from:

```text
weather_activity_dataset.csv
```

The training program automatically detects the activity target column and weather condition column.

The dataset contains weather-related information that is used to learn relationships between weather conditions and recommended activities.

---

# 16. Data Preprocessing

The project performs the following preprocessing steps:

### 16.1 Weather Encoding

Weather conditions are converted into numerical values using `LabelEncoder`.

```text
Clear
Clouds
Rain
Thunderstorm
Snow
Drizzle
Mist
Fog
```

The training code creates a weather encoder for this purpose.

### 16.2 Binary Weather Features

Additional binary features are created:

```text
is_rain
is_snow
is_clear
is_cloudy
is_foggy
```

These features help the model distinguish between different weather conditions.

---

# 17. Feature Selection

The model uses weather-related numeric features such as:

```text
Temperature
Humidity
Wind Speed
```

along with:

```text
Weather_Encoded
is_rain
is_snow
is_clear
is_cloudy
is_foggy
```

The feature-selection process is implemented in the training program.

---

# 18. Problem Type

## Classification Problem

The project is primarily a **Classification Problem**.

### Input

```text
Temperature
Humidity
Wind Speed
Weather Condition
```

### Output

```text
Recommended Activity
```

Examples:

```text
Indoor Activities
Indoor Games / Movies
Walking / Cycling / Outdoor Sports
Light Outdoor Activity
Walking / Photography
```

The target activity is encoded using `LabelEncoder`.

---

# 19. Model Selection

## Primary Algorithm

### Logistic Regression

Logistic Regression is used as the primary Machine Learning classification algorithm.

The implementation uses:

* StandardScaler
* LogisticRegression
* `max_iter=2000`
* `lbfgs` solver
* Balanced class weights

The model is implemented as a Scikit-learn Pipeline.

---

# 20. Model Evaluation

The model is evaluated using:

### Accuracy

```text
Accuracy = Correct Predictions / Total Predictions
```

### Classification Report

The project generates a classification report containing classification performance information for the activity classes.

---

# 21. Model Saving

The trained Machine Learning model is saved using Python's `pickle` module.

### Model File

```text
weather_activity_model.pkl
```

### Encoder File

```text
weather_encoders.pkl
```

The model package stores the trained model, model name, accuracy, features, classes, and encoders.

---

# 22. Prediction System

During prediction, the system:

1. Receives weather information.
2. Encodes the weather condition.
3. Creates the required feature array.
4. Sends the features to the trained model.
5. Gets the predicted activity.
6. Calculates prediction probabilities.
7. Converts the encoded prediction back to the activity name.

The prediction system also returns the prediction confidence and method.

---

# 23. Rule-Based Recommendation System

The project includes a rule-based recommendation system as a fallback.

## Rain

```text
Rain / Thunderstorm
        ↓
Indoor Games / Movies
```

## Snow

```text
Snow
        ↓
Indoor Activities
```

## Very Hot

```text
Temperature ≥ 35°C
        ↓
Indoor Activities
```

## Strong Wind

```text
Wind Speed ≥ 8 m/s
        ↓
Indoor Activities
```

## Cold

```text
Temperature < 18°C
        ↓
Walking / Indoor Games
```

## Comfortable Weather

```text
18°C – 32°C
        ↓
Humidity ≤ 75%
        ↓
Walking / Cycling / Outdoor Sports
```

The same thresholds are implemented in the project's recommendation logic.

---

# 24. API Integration

The system uses the **OpenWeather API** to retrieve live weather information.

The request uses:

```text
City
API Key
Metric Units
```

The application requests weather information from the OpenWeather weather endpoint and processes the returned JSON data.

The system handles:

* Invalid city
* Connection errors
* Request timeout
* API errors
* Unexpected errors

---

# 25. n8n Integration

The project also contains an n8n integration module.

The integration supports:

```text
Weather Analysis
City Weather
Batch Analysis
```

The system provides webhook functionality for external workflow automation.

---

# 26. Flask API

A Flask server can be used to expose the recommendation functionality through HTTP endpoints.

### Available Endpoints

```text
GET  /
POST /webhook/weather
POST /webhook/city
POST /webhook/batch
GET  /health
```

The Flask integration is implemented specifically for webhook and n8n communication.

---

# 27. Batch Analysis

The system supports analyzing multiple weather records.

Example input:

```text
[
    {
        "temperature": 25,
        "humidity": 60,
        "wind_speed": 3,
        "weather": "Clear"
    },
    {
        "temperature": 30,
        "humidity": 80,
        "wind_speed": 5,
        "weather": "Rain"
    }
]
```

Each record is analyzed independently and a recommendation is generated.

---

# 28. Error Handling

The system handles several possible errors.

### Missing City

```text
Please enter a city name.
```

### Invalid Weather Request

The system displays the API error message.

### Internet Connection Error

```text
Please check your internet connection.
```

### Request Timeout

```text
Weather server took too long to respond.
```

### ML Model Error

If ML prediction fails, the system automatically attempts to use rule-based recommendation logic.

---

# 29. Sample Prediction

Example weather input:

```text
Temperature: 25°C
Humidity: 60%
Wind Speed: 3 m/s
Weather: Clear
```

Possible output:

```text
Recommended Activity:
Walking / Cycling / Outdoor Sports
```

The training program also tests sample weather records such as Clear, Rain, Clouds and Snow conditions.

---

# 30. Project Files

A possible project structure is:

```text
Weather-Based-Activity-Recommendation/
│
├── weather_activity_dataset.csv
│
├── train_model.py
│
├── weather_activity_model.pkl
│
├── weather_encoders.pkl
│
├── weather_activity.py
│
├── n8n.py
│
├── README.md
│
└── requirements.txt
```

---

# 31. Technologies Used

### Programming Language

```text
Python
```

### GUI

```text
Tkinter
```

### Machine Learning

```text
Scikit-learn
```

### Data Processing

```text
Pandas
NumPy
```

### API

```text
OpenWeather API
```

### Model Serialization

```text
Pickle
```

### Web Integration

```text
Flask
n8n
```

---

# 32. Python Libraries

The main libraries used include:

```text
tkinter
requests
pandas
numpy
scikit-learn
pickle
flask
```

---

# 33. Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
```

Open the project directory:

```bash
cd Weather-Based-Activity-Recommendation
```

Install the required packages:

```bash
pip install pandas numpy scikit-learn requests flask
```

---

# 34. OpenWeather API Configuration

Create an OpenWeather API key and configure it in the Python application.

Replace the API key placeholder in the source code with your own key.

**Important:** Do not upload a real API key to a public GitHub repository.

For a public repository, use an environment variable instead of directly storing the API key in the source code.

---

# 35. Train the Machine Learning Model

Place the dataset in the project directory:

```text
weather_activity_dataset.csv
```

Run:

```bash
python train_model.py
```

The training process:

```text
Load Dataset
      ↓
Preprocess Data
      ↓
Encode Weather
      ↓
Encode Activities
      ↓
Select Features
      ↓
Split Dataset
      ↓
Train Logistic Regression
      ↓
Evaluate Model
      ↓
Save Model
```

The training script creates:

```text
weather_activity_model.pkl
weather_encoders.pkl
```

---

# 36. Run the Tkinter Application

After configuring the API key, run:

```bash
python weather_activity.py
```

The application opens the Weather Activity interface.

Enter a city such as:

```text
Chennai
```

Then click:

```text
CHECK WEATHER
```

The application retrieves the live weather information and displays the recommended activity.

---

# 37. Run n8n / Flask Integration

Run:

```bash
python n8n.py
```

The integration module can operate in command-line mode or start the Flask server for webhook integration.

For example:

```bash
python n8n.py --city Chennai
```

Or:

```bash
python n8n.py --analyze --temperature 25 --humidity 60 --wind 3 --weather Clear
```

---

# 38. Example API Usage

### Weather Analysis

```text
POST /webhook/weather
```

Example JSON:

```json
{
    "temperature": 25,
    "humidity": 60,
    "wind_speed": 3,
    "weather": "Clear",
    "description": "clear sky"
}
```

### City Weather

```text
POST /webhook/city
```

Example JSON:

```json
{
    "city": "Chennai"
}
```

### Batch Analysis

```text
POST /webhook/batch
```

---

# 39. Improving the Model

The Machine Learning model can be improved by:

* Increasing dataset size.
* Adding more weather records.
* Adding more activity categories.
* Improving feature selection.
* Trying multiple ML algorithms.
* Hyperparameter tuning.
* Cross-validation.
* Handling class imbalance.
* Adding additional weather features.
* Testing the model on unseen weather conditions.
* Collecting real-world activity feedback.

---

# 40. Future Enhancements

Possible future improvements include:

* Weather forecast-based recommendations.
* GPS-based automatic location detection.
* Mobile application.
* Voice-based weather search.
* Personalized activity recommendations.
* Time-of-day based recommendations.
* UV index analysis.
* Air quality analysis.
* Precipitation probability.
* Weather alerts.
* User preference-based recommendations.
* Advanced Machine Learning models.
* Deep Learning-based weather activity prediction.

---

# 41. Outcomes

The following components are developed as part of the project:

* Weather activity dataset
* Data preprocessing
* Feature engineering
* Logistic Regression model
* Model evaluation
* Activity prediction
* Saved ML model
* Saved encoders
* OpenWeather API integration
* Tkinter GUI
* Rule-based fallback
* n8n integration
* Flask webhook API
* Batch weather analysis

---

# 42. Advantages

* Simple and user-friendly interface.
* Uses real-time weather information.
* Provides quick activity recommendations.
* Combines Machine Learning with rule-based logic.
* Supports fallback when ML resources are unavailable.
* Supports API-based integration.
* Supports batch analysis.
* Can be extended for automation using n8n.
* Can be expanded with additional weather features.

---

# 43. Limitations

* Recommendation quality depends on the training dataset.
* OpenWeather API requires a valid API key.
* Internet connectivity is required for live weather retrieval.
* Weather conditions can change rapidly.
* Activity recommendations are general and may not account for individual preferences.
* The current ML system is based primarily on weather-related features.

---

# 44. Conclusion

The **Weather-Based Activity Recommendation System** demonstrates how Python, Machine Learning, API integration, and GUI development can be combined to create an intelligent recommendation application.

The system retrieves live weather information, processes important weather parameters, predicts suitable activities using Logistic Regression, and provides a rule-based fallback when necessary.

The Tkinter interface makes the system easy to use, while the n8n and Flask integration provides opportunities for workflow automation and external API access.

The project provides a practical example of applying Machine Learning to a real-world recommendation problem.

---

# 45. Project Demonstration

### Basic Workflow

```text
Enter City
     ↓
Check Weather
     ↓
Live Weather Data
     ↓
Temperature + Humidity + Wind + Condition
     ↓
Machine Learning / Rule-Based Analysis
     ↓
Recommended Activity
     ↓
Display Result
```

### Example

```text
🌦 WEATHER ACTIVITY

📍 Chennai

Temperature: 29.5°C
Feels like: 31.0°C

Condition: Clouds
Humidity: 65%
Wind Speed: 3.2 m/s

🏆 Recommended Activity:
Walking / Cycling / Outdoor Sports

Reason:
The weather conditions are comfortable for outdoor activities.
```

---

# 46. License

This project is developed for educational and academic purposes.

You may modify and extend the project according to your requirements.
