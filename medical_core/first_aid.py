def get_first_aid_advice(condition: str) -> dict:
    """Get first aid advice for medical conditions."""
    first_aid_guides = {
        "high_cholesterol": {
            "immediate_actions": [
                "Do not panic - high cholesterol is manageable",
                "Schedule appointment with doctor for proper evaluation",
                "Start documenting your diet and exercise habits",
            ],
            "lifestyle_changes": [
                "Reduce saturated fats and trans fats in diet",
                "Increase fiber intake (oats, beans, fruits)",
                "Exercise at least 30 minutes daily",
                "Maintain healthy weight",
                "Quit smoking if applicable",
            ],
            "warning_signs": "Seek immediate medical help if experiencing chest pain, shortness of breath, or severe symptoms",
        },
        "diabetes": {
            "immediate_actions": [
                "Check blood sugar levels if possible",
                "Stay hydrated with water",
                "Contact healthcare provider for guidance",
            ],
            "lifestyle_changes": [
                "Monitor blood sugar regularly",
                "Follow diabetic meal plan",
                "Exercise regularly with doctor approval",
                "Take medications as prescribed",
            ],
            "emergency": "Call emergency services if experiencing severe symptoms like confusion, loss of consciousness, or very high/low blood sugar",
        },
        "general": {
            "immediate_actions": [
                "Stay calm and assess the situation",
                "Contact healthcare provider for advice",
                "Document symptoms and measurements",
            ],
            "when_to_seek_help": [
                "Severe or persistent symptoms",
                "Chest pain or difficulty breathing",
                "Sudden changes in condition",
                "Confusion or loss of consciousness",
            ],
        },
    }

    condition_key = condition.lower().replace(" ", "_")
    return first_aid_guides.get(condition_key, first_aid_guides["general"])
