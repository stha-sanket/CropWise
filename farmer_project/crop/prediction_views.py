import joblib
import numpy as np
from django.conf import settings
import os
from crop.models import LearningContent # Import LearningContent model

# Load the model and scaler
MODEL_PATH = os.path.join(settings.BASE_DIR, 'best_crop_prediction_model.joblib')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'scaler.joblib')

model = None
scaler = None

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    print(f"Error loading model or scaler: {e}")

def get_crop_prediction_context(request, num_predictions=4):
    top_predictions = []
    if request.method == 'POST':
        try:
            N = float(request.POST.get('nitrogen'))
            P = float(request.POST.get('phosphorus'))
            K = float(request.POST.get('potassium'))
            temperature = float(request.POST.get('temperature'))
            humidity = float(request.POST.get('humidity'))
            ph = float(request.POST.get('ph'))
            rainfall = float(request.POST.get('rainfall'))

            input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

            if scaler and model:
                scaled_data = scaler.transform(input_data)

                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(scaled_data)[0]
                    class_labels = model.classes_
                    sorted_predictions = sorted(zip(class_labels, probabilities), key=lambda x: x[1], reverse=True)

                    for crop, prob in sorted_predictions[:num_predictions]:
                        image_url = "https://via.placeholder.com/150" # Default placeholder
                        try:
                            learning_content = LearningContent.objects.get(title__iexact=crop) # Case-insensitive match
                            if learning_content.image:
                                image_url = learning_content.image.url
                        except LearningContent.DoesNotExist:
                            pass # Use default placeholder if not found
                        
                        top_predictions.append({'crop': crop, 'probability': round(prob * 100, 2), 'image_url': image_url})
                else:
                    # Fallback for models without predict_proba (e.g., SVC without probability=True)
                    predicted_crop = model.predict(scaled_data)[0]
                    image_url = "https://via.placeholder.com/150" # Default placeholder
                    try:
                        learning_content = LearningContent.objects.get(title__iexact=predicted_crop)
                        if learning_content.image:
                            image_url = learning_content.image.url
                    except LearningContent.DoesNotExist:
                        pass
                    top_predictions.append({'crop': predicted_crop, 'probability': 100.0, 'image_url': image_url})
            else:
                top_predictions.append({'crop': "Error: Model or scaler not loaded.", 'probability': 0.0, 'image_url': "https://via.placeholder.com/150"})

        except Exception as e:
            top_predictions.append({'crop': f"Error processing input: {e}", 'probability': 0.0, 'image_url': "https://via.placeholder.com/150"})

    return {'top_predictions': top_predictions}