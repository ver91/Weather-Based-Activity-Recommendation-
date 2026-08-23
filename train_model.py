import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

print("==========================================")
print(" WEATHER ACTIVITY RECOMMENDATION TRAINING")
print("==========================================")

# ==========================================================
# LOAD DATASET - WITH AUTOMATIC COLUMN DETECTION
# ==========================================================

df = pd.read_csv("weather_activity_dataset.csv")
print(f"\nDataset loaded successfully!")
print("Total weather records:", len(df))

# ==========================================================
# DETECT COLUMN NAMES AUTOMATICALLY
# ==========================================================

# Find the activity column (handle different naming conventions)
activity_col = None
for col in df.columns:
    if 'activity' in col.lower():
        activity_col = col
        break

if activity_col is None:
    # If no activity column found, use the last column
    activity_col = df.columns[-1]
    print(f"Warning: No 'activity' column found. Using '{activity_col}' as target.")

# Find weather condition column
weather_col = None
for col in df.columns:
    if 'weather' in col.lower() or 'condition' in col.lower():
        weather_col = col
        break

if weather_col is None:
    # If no weather column found, use the 4th column (assuming standard format)
    weather_col = df.columns[3]
    print(f"Warning: No 'weather' column found. Using '{weather_col}' as weather condition.")

print(f"\nUsing target column: '{activity_col}'")
print(f"Using weather column: '{weather_col}'")

print("\n==========================================")
print("DATA OVERVIEW")
print("==========================================")
print("\nFirst 5 records:")
print(df.head())

print("\nDataset Info:")
print(df.info())

print(f"\nActivity Distribution:")
print(df[activity_col].value_counts())

# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

print("\n==========================================")
print("PREPARING FEATURES")
print("==========================================")

# Encode weather condition
weather_encoder = LabelEncoder()
df['Weather_Encoded'] = weather_encoder.fit_transform(df[weather_col])

# Create binary weather features
df['is_rain'] = df[weather_col].apply(lambda x: 1 if x in ['Rain', 'Thunderstorm', 'Drizzle'] else 0)
df['is_snow'] = df[weather_col].apply(lambda x: 1 if x == 'Snow' else 0)
df['is_clear'] = df[weather_col].apply(lambda x: 1 if x == 'Clear' else 0)
df['is_cloudy'] = df[weather_col].apply(lambda x: 1 if x in ['Clouds'] else 0)
df['is_foggy'] = df[weather_col].apply(lambda x: 1 if x in ['Mist', 'Fog'] else 0)

# Encode target variable
activity_encoder = LabelEncoder()
df['Activity_Encoded'] = activity_encoder.fit_transform(df[activity_col])

print("\nWeather Conditions:", list(weather_encoder.classes_))
print("Activities:", list(activity_encoder.classes_))
print("Number of activity classes:", len(activity_encoder.classes_))

# ==========================================================
# FEATURE SELECTION
# ==========================================================

# Find numeric columns
numeric_cols = []
for col in df.columns:
    if df[col].dtype in ['float64', 'int64'] and col not in ['Activity_Encoded', 'Weather_Encoded']:
        if col not in ['is_rain', 'is_snow', 'is_clear', 'is_cloudy', 'is_foggy']:
            # Only include temperature, humidity, wind_speed-like columns
            if 'temp' in col.lower() or 'humid' in col.lower() or 'wind' in col.lower():
                numeric_cols.append(col)

# If no numeric columns found, use the first three columns
if not numeric_cols:
    numeric_cols = df.columns[:3].tolist()

X = df[
    numeric_cols + 
    [
        "Weather_Encoded",
        "is_rain",
        "is_snow",
        "is_clear",
        "is_cloudy",
        "is_foggy"
    ]
]

y = df["Activity_Encoded"]

print("\nFeature columns:")
for col in X.columns:
    print(f"  - {col}")

print(f"\nTarget: {activity_col}")

# ==========================================================
# TRAIN-TEST SPLIT
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n==========================================")
print("DATA SPLIT")
print("==========================================")
print("Training samples:", len(X_train))
print("Testing samples :", len(X_test))

# ==========================================================
# TRAIN LOGISTIC REGRESSION MODEL (FIXED)
# ==========================================================

print("\n==========================================")
print("TRAINING LOGISTIC REGRESSION")
print("==========================================")

# Create the Logistic Regression model with fixed parameters
lr_model = Pipeline([
    ("scaler", StandardScaler()),  # Logistic Regression requires feature scaling
    ("logistic_regression", LogisticRegression(
        max_iter=2000,               # Increased iterations for convergence
        solver='lbfgs',              # Good for small to medium datasets
        C=1.0,                       # Regularization strength (default)
        random_state=42,
        class_weight='balanced'      # Handle any class imbalance
    ))
])

lr_model.fit(X_train, y_train)
print("\nLogistic Regression training completed!")

# ==========================================================
# MODEL EVALUATION
# ==========================================================

print("\n==========================================")
print("MODEL PERFORMANCE")
print("==========================================")

# Predict on test set
y_pred = lr_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nLogistic Regression Classifier:")
print(f"  Accuracy: {round(accuracy * 100, 2)}%")
print(f"  Classification Report:")
report = classification_report(y_test, y_pred, target_names=activity_encoder.classes_, zero_division=0)
print(report)

# ==========================================================
# SAVE MODEL
# ==========================================================

model_package = {
    "model": lr_model,
    "model_name": "Logistic Regression",
    "accuracy": accuracy,
    "features": list(X.columns),
    "weather_encoder": weather_encoder,
    "activity_encoder": activity_encoder,
    "feature_names": list(X.columns),
    "n_classes": len(activity_encoder.classes_),
    "classes": list(activity_encoder.classes_)
}

with open("weather_activity_model.pkl", "wb") as file:
    pickle.dump(model_package, file)

print("\n==========================================")
print("MODEL SAVED SUCCESSFULLY")
print("==========================================")
print(f"Algorithm: Logistic Regression")
print(f"Accuracy: {round(accuracy * 100, 2)}%")
print("File created: weather_activity_model.pkl")

# ==========================================================
# SAVE ENCODERS
# ==========================================================

encoder_package = {
    'weather_encoder': weather_encoder,
    'activity_encoder': activity_encoder,
    'features': list(X.columns),
    'classes': list(activity_encoder.classes_)
}

with open("weather_encoders.pkl", "wb") as file:
    pickle.dump(encoder_package, file)

print("\nEncoders saved: weather_encoders.pkl")

# ==========================================================
# SAMPLE PREDICTIONS
# ==========================================================

print("\n==========================================")
print("SAMPLE PREDICTIONS")
print("==========================================")

sample_data = [
    {'Temperature': 25, 'Humidity': 60, 'Wind_Speed': 3, 'Weather': 'Clear'},
    {'Temperature': 30, 'Humidity': 80, 'Wind_Speed': 5, 'Weather': 'Rain'},
    {'Temperature': 15, 'Humidity': 70, 'Wind_Speed': 2, 'Weather': 'Clouds'},
    {'Temperature': 35, 'Humidity': 45, 'Wind_Speed': 4, 'Weather': 'Clear'},
    {'Temperature': 5, 'Humidity': 85, 'Wind_Speed': 1, 'Weather': 'Snow'},
]

for i, sample in enumerate(sample_data, 1):
    try:
        # Prepare features
        weather_encoded = weather_encoder.transform([sample['Weather']])[0]
        
        features = np.array([[
            sample['Temperature'],
            sample['Humidity'],
            sample['Wind_Speed'],
            weather_encoded,
            1 if sample['Weather'] in ['Rain', 'Thunderstorm', 'Drizzle'] else 0,
            1 if sample['Weather'] == 'Snow' else 0,
            1 if sample['Weather'] == 'Clear' else 0,
            1 if sample['Weather'] == 'Clouds' else 0,
            1 if sample['Weather'] in ['Mist', 'Fog'] else 0
        ]])
        
        prediction = lr_model.predict(features)
        activity = activity_encoder.inverse_transform(prediction)[0]
        
        # Get prediction probability
        probabilities = lr_model.predict_proba(features)[0]
        max_prob = max(probabilities) * 100
        
        print(f"\nSample {i}:")
        print(f"  Weather: {sample['Weather']}")
        print(f"  Temperature: {sample['Temperature']}°C")
        print(f"  Humidity: {sample['Humidity']}%")
        print(f"  Wind Speed: {sample['Wind_Speed']} m/s")
        print(f"  Recommended Activity: {activity}")
        print(f"  Confidence: {max_prob:.1f}%")
        print("-" * 50)
    except Exception as e:
        print(f"\nSample {i}: Error in prediction - {e}")

print("\n==========================================")
print("TRAINING COMPLETED SUCCESSFULLY!")
print("==========================================")

# ==========================================================
# OPTIONAL: FEATURE IMPORTANCE (Coefficients)
# ==========================================================

print("\n==========================================")
print("FEATURE COEFFICIENTS (Logistic Regression)")
print("==========================================")

try:
    # Get the logistic regression model from pipeline
    lr = lr_model.named_steps['logistic_regression']
    
    # Get feature names
    feature_names = X.columns
    
    # For multi-class, we have coefficients for each class
    coef_df = pd.DataFrame(
        lr.coef_,
        columns=feature_names,
        index=activity_encoder.classes_
    )
    
    print("\nTop features for each activity (positive coefficients indicate stronger association):")
    for activity in coef_df.index:
        top_features = coef_df.loc[activity].sort_values(ascending=False).head(3)
        print(f"\n{activity}:")
        for feature, coef in top_features.items():
            print(f"  {feature}: {coef:.3f}")
            
except Exception as e:
    print(f"Could not display feature coefficients: {e}")

print("\n==========================================")
print("EXECUTION COMPLETE!")
print("==========================================")