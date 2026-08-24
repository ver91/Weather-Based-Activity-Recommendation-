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

df = pd.read_csv("weather_activity_dataset.csv")
print(f"\nDataset loaded successfully!")
print("Total weather records:", len(df))

activity_col = None
for col in df.columns:
    if 'activity' in col.lower():
        activity_col = col
        break

if activity_col is None:
    activity_col = df.columns[-1]
    print(f"Warning: No 'activity' column found. Using '{activity_col}' as target.")

weather_col = None
for col in df.columns:
    if 'weather' in col.lower() or 'condition' in col.lower():
        weather_col = col
        break

if weather_col is None:
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

print("\n==========================================")
print("PREPARING FEATURES")
print("==========================================")

weather_encoder = LabelEncoder()
df['Weather_Encoded'] = weather_encoder.fit_transform(df[weather_col])

df['is_rain'] = df[weather_col].apply(lambda x: 1 if x in ['Rain', 'Thunderstorm', 'Drizzle'] else 0)
df['is_snow'] = df[weather_col].apply(lambda x: 1 if x == 'Snow' else 0)
df['is_clear'] = df[weather_col].apply(lambda x: 1 if x == 'Clear' else 0)
df['is_cloudy'] = df[weather_col].apply(lambda x: 1 if x in ['Clouds'] else 0)
df['is_foggy'] = df[weather_col].apply(lambda x: 1 if x in ['Mist', 'Fog'] else 0)

activity_encoder = LabelEncoder()
df['Activity_Encoded'] = activity_encoder.fit_transform(df[activity_col])

print("\nWeather Conditions:", list(weather_encoder.classes_))
print("Activities:", list(activity_encoder.classes_))
print("Number of activity classes:", len(activity_encoder.classes_))

numeric_cols = []
for col in df.columns:
    if df[col].dtype in ['float64', 'int64'] and col not in ['Activity_Encoded', 'Weather_Encoded']:
        if col not in ['is_rain', 'is_snow', 'is_clear', 'is_cloudy', 'is_foggy']:
            # Only include temperature, humidity, wind_speed-like columns
            if 'temp' in col.lower() or 'humid' in col.lower() or 'wind' in col.lower():
                numeric_cols.append(col)
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

print("\n==========================================")
print("TRAINING LOGISTIC REGRESSION")
print("==========================================")

lr_model = Pipeline([
    ("scaler", StandardScaler()), 
    ("logistic_regression", LogisticRegression(
        max_iter=2000,              
        solver='lbfgs',             
        C=1.0,                      
        random_state=42,
        class_weight='balanced'     
    ))
])

lr_model.fit(X_train, y_train)
print("\nLogistic Regression training completed!")


print("\n==========================================")
print("MODEL PERFORMANCE")
print("==========================================")

y_pred = lr_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nLogistic Regression Classifier:")
print(f"  Accuracy: {round(accuracy * 100, 2)}%")
print(f"  Classification Report:")
report = classification_report(y_test, y_pred, target_names=activity_encoder.classes_, zero_division=0)
print(report)

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

encoder_package = {
    'weather_encoder': weather_encoder,
    'activity_encoder': activity_encoder,
    'features': list(X.columns),
    'classes': list(activity_encoder.classes_)
}

with open("weather_encoders.pkl", "wb") as file:
    pickle.dump(encoder_package, file)

print("\nEncoders saved: weather_encoders.pkl")


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
print("FEATURE COEFFICIENTS (Logistic Regression)")
print("==========================================")

try:
    lr = lr_model.named_steps['logistic_regression']
    
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

print("\n==========================================")
print("EXECUTION COMPLETE!")
print("==========================================")
