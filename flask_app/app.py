from flask import Flask, render_template, request, jsonify
from model_utils import assess_patient
import pandas as pd

app = Flask(__name__)

# Categorical options for the form
CAT_OPTIONS = {
    "Gender": ["Female", "Male"],
    "Ethnicity": ["African", "Asian", "Caucasian", "Hispanic", "Middle Eastern"],
    "Family_History": ["No", "Yes"],
    "Radiation_Exposure": ["No", "Yes"],
    "Iodine_Deficiency": ["No", "Yes"],
    "Smoking": ["No", "Yes"],
    "Obesity": ["No", "Yes"],
    "Diabetes": ["No", "Yes"],
    "Thyroid_Cancer_Risk": ["High", "Low", "Medium"]
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Gather numerical data
            patient_data = {
                'Age': float(request.form.get('Age', 45)),
                'TSH_Level': float(request.form.get('TSH_Level', 2.0)),
                'T3_Level': float(request.form.get('T3_Level', 2.0)),
                'T4_Level': float(request.form.get('T4_Level', 10.0)),
                'Nodule_Size': float(request.form.get('Nodule_Size', 1.0))
            }
            for cat in CAT_OPTIONS:
                patient_data[cat] = request.form.get(cat)
            
            assessment = assess_patient(patient_data)
            return render_template('result.html', assessment=assessment, patient_data=patient_data)
        except Exception as e:
            return render_template('index.html', options=CAT_OPTIONS, error=str(e))

    return render_template('index.html', options=CAT_OPTIONS)


### run pyhton app.py 
#### open http://127.0.0.1:5001 in browser

if __name__ == '__main__':
    app.run(debug=True, port=5001)


