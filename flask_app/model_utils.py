import joblib
import os
import pandas as pd
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

# Load all exported assets
dt_pipeline = joblib.load(os.path.join(MODELS_DIR, 'dt_pipeline.joblib'))
pheno_preprocessor = joblib.load(os.path.join(MODELS_DIR, 'pheno_preprocessor.joblib'))
kmeans_phenotypes = joblib.load(os.path.join(MODELS_DIR, 'kmeans_phenotypes.joblib'))
danger_zones = joblib.load(os.path.join(MODELS_DIR, 'danger_zones.joblib'))
pheno_summary = joblib.load(os.path.join(MODELS_DIR, 'pheno_summary.joblib'))
overall_means = joblib.load(os.path.join(MODELS_DIR, 'overall_means.joblib'))
feature_cols = joblib.load(os.path.join(MODELS_DIR, 'feature_cols.joblib'))
phenotype_features = joblib.load(os.path.join(MODELS_DIR, 'phenotype_features.joblib'))

def assess_patient(patient_data):
    """
    Perform full thyroid cancer assessment for a patient.
    
    patient_data: dict with clinical features
    Returns: dict with diagnosis, phenotype, and risk assessment
    """
    patient_df = pd.DataFrame([patient_data])
    patient_df = patient_df[feature_cols] # Ensure order
    
    # 1. Supervised Diagnosis
    pred_class_label = dt_pipeline.predict(patient_df)[0]
    classes = dt_pipeline.classes_.tolist()
    class_idx = classes.index(pred_class_label)
    pred_prob = dt_pipeline.predict_proba(patient_df)[0][class_idx]
    diagnosis = pred_class_label
    
    # 2. Phenotype Assignment
    patient_pheno_df = pd.DataFrame([patient_data])[phenotype_features]
    X_pheno_proc = pheno_preprocessor.transform(patient_pheno_df)
    pheno_id = int(kmeans_phenotypes.predict(X_pheno_proc)[0])
    
    # Get Phenotype Description
    row = pheno_summary.loc[pheno_id]
    desc_parts = []
    
    # Numerical comparisons
    num_map = {
        'Age': 'age',
        'TSH_Level': 'TSH',
        'T3_Level': 'T3',
        'T4_Level': 'T4',
        'Nodule_Size': 'nodule size'
    }
    
    for feat, label in num_map.items():
        if row[feat] > overall_means[feat]:
            desc_parts.append(f"higher {label}")
        else:
            desc_parts.append(f"lower {label}")
            
    pheno_desc = {
        'id': pheno_id,
        'summary': f"{', '.join(desc_parts)}; typical risk: {row['Thyroid_Cancer_Risk']}",
        'gender': row['Gender'],
        'iodine': row['Iodine_Deficiency'],
        'radiation': row['Radiation_Exposure'],
        'family_history': row['Family_History']
    }
    
    # 3. Risk Zone Assessment
    risk_assessment = {}
    for feature_name, zone_info in danger_zones.items():
        if feature_name in patient_data:
            value = float(patient_data[feature_name])
            thresholds = zone_info['thresholds']
            
            if len(thresholds) == 1:
                zone = 'Low Risk' if value < thresholds[0] else 'High Risk'
            elif len(thresholds) >= 2:
                if value < thresholds[0]: zone = 'Low Risk'
                elif value >= thresholds[-1]: zone = 'High Risk'
                else: zone = 'Moderate Risk'
            else:
                zone = 'Unknown'
                
            risk_assessment[feature_name] = {
                'value': value,
                'zone': zone,
                'thresholds': thresholds
            }
            
    return {
        'diagnosis': diagnosis,
        'confidence': pred_prob,
        'phenotype': pheno_desc,
        'risk_assessment': risk_assessment
    }
