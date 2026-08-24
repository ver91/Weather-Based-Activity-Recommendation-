# Weather Activity Recommendation System — V-Model

## 1. System Overview

The **Weather Activity Recommendation System** is an intelligent application that analyzes real-time weather conditions and recommends suitable activities.

The system combines:

* Real-time weather data from the **OpenWeather API**
* **Machine Learning** for activity prediction
* **Rule-based logic** as a fallback mechanism
* **Tkinter** for the desktop user interface
* **Flask** for API communication
* **n8n** for workflow automation

---

## 2. V-Model Development Process

The V-Model is used to organize the development and testing of the system.

```text
                    V-MODEL
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             │
  Requirements Analysis               │
        │                             │
        ▼                             │
  System Design                       │
        │                             │
        ▼                             │
  Architecture Design                │
        │                             │
        ▼                             │
  Module Design                       │
        │                             │
        ▼                             │
  Implementation                      │
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼
                Unit Testing
                       │
                       ▼
               Integration Testing
                       │
                       ▼
                System Testing
                       │
                       ▼
             Acceptance Testing
```

---

## 3. V-Model Phases

### 3.1 Requirements Analysis

The system requirements are identified before implementation.

### Functional Requirements

* Accept city name from the user.
* Fetch real-time weather information.
* Display temperature, humidity, wind speed, and weather condition.
* Predict a suitable activity.
* Provide a recommendation to the user.
* Support ML-based prediction.
* Provide rule-based fallback logic.
* Support API and n8n integration.

### Non-Functional Requirements

* Easy-to-use interface
* Fast response
* Reliable weather data
* Maintainable code
* Accurate activity prediction

---

## 4. System Design

The system is divided into multiple layers.

```text
┌──────────────────────────────────────┐
│          User Interface              │
│            Tkinter GUI               │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       Application / API Layer        │
│             Flask API                │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│         Weather Data Layer           │
│          OpenWeather API             │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       Machine Learning Layer         │
│        Logistic Regression           │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│      Recommendation Engine           │
│       ML + Rule-Based Logic          │
└──────────────────────────────────────┘
```

---

## 5. Architecture Design

### User Interface Layer

The Tkinter desktop application allows the user to:

* Enter a city
* Request weather information
* View current weather conditions
* View recommended activities

### API Integration Layer

The Flask server provides API endpoints for processing weather information and returning recommendations.

### Weather Data Layer

The OpenWeather API provides real-time:

* Temperature
* Humidity
* Wind speed
* Weather condition

### Machine Learning Layer

The ML model analyzes weather features and predicts the most appropriate activity.

### Recommendation Layer

The recommendation engine returns the final activity using:

1. ML prediction when the model is available.
2. Rule-based logic when ML prediction is unavailable.

---

# 6. Module Design

The project is divided into the following modules:

```text
weather_app.py
       │
       ▼
    server.py
       │
       ├──────────────► OpenWeather API
       │
       ▼
      ai.py
       │
       ▼
 ML Recommendation Model
       │
       ▼
 Activity Recommendation
```

### weather_app.py

Responsible for the Tkinter desktop interface.

### server.py

Responsible for Flask API services and request processing.

### ai.py

Contains the recommendation logic and ML model integration.

### train_model.py

Responsible for training and evaluating the machine learning model.

### gen.py

Generates the weather activity training dataset.

### n8n.py

Handles communication between the Python application and n8n workflow automation.

---

# 7. Machine Learning Module

The system uses **Logistic Regression** for activity classification.

### Input Features

The model uses weather-related features such as:

* Temperature
* Humidity
* Wind Speed
* Weather Condition

### Output

The model predicts a suitable activity category.

Example:

```text
Weather Data
     ↓
Feature Processing
     ↓
Label Encoding
     ↓
Standard Scaling
     ↓
Logistic Regression
     ↓
Activity Prediction
```

The trained model is stored using **Pickle** so that it can be loaded by the application without retraining every time.

---

# 8. Recommendation Logic

The system follows a dual-layer approach.

```text
             Weather Input
                   │
                   ▼
             ML Prediction
                   │
             Model Available?
              /          \
            Yes           No
             │             │
             ▼             ▼
        ML Result     Rule-Based Logic
             │             │
             └──────┬──────┘
                    ▼
             Final Activity
                    │
                    ▼
              User Interface
```

### ML Layer

The trained Logistic Regression model predicts the recommended activity based on weather conditions.

### Rule-Based Layer

If the ML model is unavailable or cannot process the input, predefined weather rules are used.

Example:

```text
Rainy Weather
      ↓
Indoor Activity

Clear + Comfortable Temperature
      ↓
Outdoor Activity

High Temperature
      ↓
Indoor / Low-Intensity Activity

Strong Wind
      ↓
Indoor Activity
```

---

# 9. Testing Phase

Testing is performed after implementation according to the V-Model.

## Unit Testing

Individual modules are tested separately.

Examples:

* Weather API function
* ML prediction function
* Recommendation function
* Input validation
* Flask endpoints

## Integration Testing

The interaction between modules is tested.

```text
Tkinter
   ↓
Flask
   ↓
OpenWeather API
   ↓
ML Model
   ↓
Recommendation
```

## System Testing

The complete application is tested as a single system.

Test cases include:

* Valid city input
* Invalid city input
* Clear weather
* Rainy weather
* Extreme temperature
* High humidity
* High wind speed
* ML model unavailable

## Acceptance Testing

The final system is checked against the original requirements to ensure that it provides correct weather information and meaningful activity recommendations.

---

# 10. n8n Integration

n8n is used for workflow automation.

```text
User / Application
        │
        ▼
   n8n Webhook
        │
        ▼
 Python / Flask API
        │
        ▼
 Weather Analysis
        │
        ▼
 ML / Rule-Based Engine
        │
        ▼
 Recommendation
        │
        ▼
   n8n Response
```

The n8n workflow can receive weather information, send it to the Python service, process the response, and return the recommendation.

---

# 11. Project Workflow

```text
START
  │
  ▼
Enter City
  │
  ▼
Request Weather Data
  │
  ▼
OpenWeather API
  │
  ▼
Receive Weather Information
  │
  ▼
Preprocess Weather Data
  │
  ▼
ML Model Available?
  │
 ┌┴───────────────┐
 │                │
Yes              No
 │                │
 ▼                ▼
ML Prediction   Rule-Based
 │                │
 └───────┬────────┘
         ▼
Activity Recommendation
         │
         ▼
Display Result
         │
         ▼
        END
```

---

# 12. Project Structure

```text
weather-activity-recommendation/
│
├── weather_app.py
├── server.py
├── ai.py
├── train_model.py
├── gen.py
├── n8n.py
├── requirements.txt
│
├── models/
│   ├── weather_activity_model.pkl
│   └── weather_encoders.pkl
│
├── data/
│   └── weather_activity_dataset.csv
│
└── workflows/
    └── weather_analysis_workflow.json
```

---

# 13. Technologies Used

| Component            | Technology          |
| -------------------- | ------------------- |
| Programming Language | Python              |
| GUI                  | Tkinter             |
| Machine Learning     | Scikit-learn        |
| Data Processing      | Pandas, NumPy       |
| ML Algorithm         | Logistic Regression |
| Model Storage        | Pickle              |
| Weather Data         | OpenWeather API     |
| Backend API          | Flask               |
| Automation           | n8n                 |

---

# 14. Final V-Model Mapping

| Development Phase     | Corresponding Testing Phase |
| --------------------- | --------------------------- |
| Requirements Analysis | Acceptance Testing          |
| System Design         | System Testing              |
| Architecture Design   | Integration Testing         |
| Module Design         | Unit Testing                |
| Implementation        | Code Verification           |

---

## 15. Conclusion

The Weather Activity Recommendation System follows the **V-Model software development methodology**, where every development phase is associated with a corresponding testing phase.

The completed system integrates **real-time weather data, machine learning, rule-based recommendation logic, Tkinter, Flask, and n8n** to provide intelligent activity recommendations based on current weather conditions.
