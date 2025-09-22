import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, classification_report
import os
import joblib

# Ensure the output directory for plots exists
output_dir = 'ML_plots'
os.makedirs(output_dir, exist_ok=True)

# Load the dataset
try:
    # First, try to read as CSV
    df = pd.read_csv("Crop_recommendation.xls")
    print("Read as CSV successfully.")
except Exception as e_csv:
    print(f"Could not read as CSV: {e_csv}. Trying to read as Excel (xls) with xlrd...")
    try:
        # If CSV fails, try to read as Excel (xls) with xlrd
        # If you encounter an error like 'No module named 'xlrd'', you may need to install it:
        # pip install xlrd
        df = pd.read_excel("Crop_recommendation.xls", engine='xlrd')
        print("Read as Excel (xls) successfully.")
    except FileNotFoundError:
        print("Error: 'Crop_recommendation.xls' not found. Make sure it's in the project root directory.")
        exit()
    except Exception as e_excel:
        print(f"Error reading 'Crop_recommendation.xls' as Excel: {e_excel}")
        print("Please ensure the file is a valid .xls or .csv file and xlrd is installed if it's an .xls file.")
        exit()

print("Dataset loaded successfully.")
print("Dataset head:")
print(df.head())
print("\nDataset Info:")
df.info()
print("\nDataset Description:")
print(df.describe())

# --- EDA and Visualization ---

# 1. Histograms for numerical features
print("\nGenerating histograms...")
df.hist(bins=15, figsize=(15, 10))
plt.suptitle('Distribution of Numerical Features')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(os.path.join(output_dir, 'numerical_feature_histograms.png'))
plt.close()
print("Histograms saved to 'ML_plots/numerical_feature_histograms.png'")

# 2. Correlation Matrix Heatmap
print("\nGenerating correlation heatmap...")
plt.figure(figsize=(12, 10))
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix of Features')
plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
plt.close()
print("Correlation heatmap saved to 'ML_plots/correlation_heatmap.png'")

# 3. Target variable distribution
print("\nGenerating target variable distribution plot...")
plt.figure(figsize=(12, 6))
sns.countplot(data=df, y='label')
plt.title('Distribution of label Types')
plt.savefig(os.path.join(output_dir, 'crop_distribution.png'))
plt.close()
print("Crop distribution plot saved to 'ML_plots/crop_distribution.png'")

# --- Machine Learning Models ---

# Separate features and target variable
X = df.drop('label', axis=1)
y = df['label']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTraining data shape: {X_train.shape}")
print(f"Testing data shape: {X_test.shape}")

# Scale numerical features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Initialize models
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Support Vector Machine': SVC(random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(),
    'Random Forest': RandomForestClassifier(random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(random_state=42)
}

results = {}
best_model_name = None
best_f1_score = -1

print("\n--- Training and Evaluating Models ---")
for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    results[name] = {'accuracy': accuracy, 'f1_score': f1, 'model': model}
    print(f"{name} - Accuracy: {accuracy:.4f}, F1 Score: {f1:.4f}")

    if f1 > best_f1_score:
        best_f1_score = f1
        best_model_name = name

print("\n--- Model Comparison ---")
for name, metrics in results.items():
    print(f"{name}: Accuracy = {metrics['accuracy']:.4f}, F1 Score = {metrics['f1_score']:.4f}")

print(f"\nBest performing model: {best_model_name} with F1 Score: {best_f1_score:.4f}")

# Save the best model
best_model = results[best_model_name]['model']
model_filename = 'best_crop_prediction_model.joblib'
joblib.dump(best_model, model_filename)
print(f"Best model saved as '{model_filename}'")

# Save the scaler as well, as it's needed for new predictions
scaler_filename = 'scaler.joblib'
joblib.dump(scaler, scaler_filename)
print(f"Scaler saved as '{scaler_filename}'")

# --- Evaluation of the Best Model ---
print(f"\n--- Detailed Evaluation of {best_model_name} ---")
y_pred_best = best_model.predict(X_test_scaled)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred_best))

# Confusion Matrix
print("\nGenerating Confusion Matrix for Best Model...")
cm = confusion_matrix(y_test, y_pred_best)
plt.figure(figsize=(15, 12))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=best_model.classes_, yticklabels=best_model.classes_)
plt.title(f'Confusion Matrix for {best_model_name}')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f'confusion_matrix_{best_model_name.replace(" ", "_")}.png'))
plt.close()
print(f"Confusion Matrix for {best_model_name} saved to 'ML_plots/confusion_matrix_{best_model_name.replace(' ', '_')}.png'")

print("\nMachine learning process completed. Check 'ML_plots' directory for visualizations and the current directory for the saved model and scaler.")