import streamlit as st
import pandas as pd
import pickle

# Load the trained model
model_path = 'classifier.pkl'  # Update the path to your model
with open(model_path, 'rb') as file:
    model = pickle.load(file)

# Load Soil_Type and Crop_Type mappings
Soil_Type = pd.DataFrame({'Soil': ['Sandy', 'Clayey', 'Loamy', 'Black'], 'Encoded': [0, 1, 2, 3]})
Crop_Type = pd.DataFrame({'Crop': ['maize', 'wheat', 'paddy', 'sugarcane'], 'Encoded': [0, 1, 2, 3]})

# Fertilizer Requirements (per hectare)
fertilizer_requirements = {
    "maize": {"N": 120, "P": 60, "K": 60},
    "wheat": {"N": 120, "P": 60, "K": 60},
    "paddy": {"N": 100, "P": 50, "K": 50},
    "sugarcane": {"N": 150, "P": 100, "K": 80}
}

def predict_fertilizer(temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous):
    """Generates the fertilizer recommendation based on ML and manual calculations."""
    try:
        # Encode soil type and crop type
        soil_encoded = Soil_Type[Soil_Type['Soil'] == soil_type]['Encoded'].values[0]
        crop_encoded = Crop_Type[Crop_Type['Crop'] == crop_type]['Encoded'].values[0]

        # Try ML Prediction
        ans = model.predict([[temperature, humidity, moisture, soil_encoded, crop_encoded, nitrogen, potassium, phosphorous]])

        # Map prediction to fertilizer type
        fertilizers = [
            "10-26-26 Fertilizer",
            "14-35-14 Fertilizer",
            "17-17-17 Fertilizer",
            "20-20 Fertilizer",
            "28-28 Fertilizer",
            "DAP (Diammonium phosphate) Fertilizer"
        ]

        if 0 <= ans[0] < len(fertilizers):
            ml_recommendation = fertilizers[ans[0]]
        else:
            ml_recommendation = None  # Invalid ML output

    except Exception:
        ml_recommendation = None  # Handle errors gracefully

    # Always calculate fertilizer requirements
    calculator_output = calculate_fertilizer_requirements(crop_type)

    # Combine outputs
    result = "**Fertilizer Recommendation:**\n"
    if ml_recommendation:
        result += f"- {ml_recommendation}\n\n"
    result += calculator_output
    return result

def calculate_fertilizer_requirements(crop_type):
    """Calculates fertilizer requirements for the given crop."""
    try:
        required_nitrogen = fertilizer_requirements[crop_type]["N"]
        required_phosphorus = fertilizer_requirements[crop_type]["P"]
        required_potassium = fertilizer_requirements[crop_type]["K"]

        # Calculate recommended fertilizer amounts
        urea_needed = required_nitrogen / 0.46  # 46% nitrogen in urea
        dap_needed = required_phosphorus / 0.46  # 46% phosphorus in DAP
        mop_needed = required_potassium / 0.60  # 60% potassium in MOP

        # Prepare the fertilizer recommendation
        return (
            f"- Urea: {urea_needed:.2f} kg/ha\n"
            f"- DAP: {dap_needed:.2f} kg/ha\n"
            f"- MOP: {mop_needed:.2f} kg/ha"
        )
    except KeyError:
        return f"Invalid crop type: {crop_type}"

# Streamlit UI components
st.title("Fertilizer Recommendation System")
st.write("Enter the details about your soil, crop, and environmental conditions to get fertilizer recommendations.")

temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=45.0, step=0.1)
humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, step=0.1)
moisture = st.number_input("Moisture (%)", min_value=0.0, max_value=100.0, step=0.1)
soil_type = st.selectbox("Soil Type", list(Soil_Type['Soil']))
crop_type = st.selectbox("Crop Type", list(Crop_Type['Crop']))
nitrogen = st.number_input("Nitrogen (kg/ha)", min_value=0.0, step=0.1)
potassium = st.number_input("Potassium (kg/ha)", min_value=0.0, step=0.1)
phosphorous = st.number_input("Phosphorous (kg/ha)", min_value=0.0, step=0.1)

# Button to predict fertilizer
if st.button("Predict Fertilizer"):
    result = predict_fertilizer(temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous)
    st.write(result)

