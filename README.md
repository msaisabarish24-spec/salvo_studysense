# 🎓 STUDYSENSE
# Student Final Marks Prediction Application
A desktop application built with Python and Tkinter that estimates student final marks based on academic and engagement metrics. 

Instead of relying on hardcoded assumptions, the app dynamically reads training data on-the-fly, derives mathematical relationships directly from the uploaded dataset, and adapts its prediction logic to fit the data provided.

---

## ✨ Features

* **Dynamic File Analysis:** Loads training data directly from `raw_data.xlsx` or any custom Excel file uploaded by the user.
* **On-the-Fly Formula Derivation:** Performs deep row and column analytics to calculate regression weights and dynamically display the derived mathematical formula in the UI.
* **Smart Column Mapping:** Automatically detects and maps flexible column headers (e.g., `Attendance %`, `Prev_Score`, `Study_Time`) using fuzzy string alias matching.
* **Exact Match Lookup:** Checks if the exact input combination exists in the active dataset and displays the exact recorded score (or the average if multiple duplicate entries match).
* **High-Performance Priority Rules:** Automatically suppresses attendance penalties if a student has high previous exam performance ($\ge 70$), prioritizing academic track record over low attendance ($\le 60\%$).
* **Input Validation & Safety:** Features strict out-of-bound value rejections and prompts for auto-imputation if fields are left blank.
* **Interactive Feedback Loop:** Asks users if the prediction matches expectations; confirmed results are appended back into the Excel file to continuously retrain and refine the model.

---

## 📊 Features & Input Ranges

| Input Feature | Expected Range | Description |
| :--- | :--- | :--- |
| **Attendance Percentage** | 0.0 – 100.0% | Student class attendance rate |
| **Previous Marks** | 0.0 – 100.0 | Past exam performance |
| **Assignment Marks** | 0.0 – 50.0 | Continuous assignment evaluation score |
| **Study Hours** | 0.0 – 24.0 hrs | Average daily study routine |

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Latest Version of Python installed along with the required dependencies:

```bash
pip install pandas numpy scikit-learn openpyxl
```
## Setup & Execution Instructions
1. Install required dependencies:
   pip install pandas numpy scikit-learn openpyxl
2. Run the application:
   python studysense.py

### Dataset Information
- Dataset URL / Link: [(https://github.com/msaisabarish24-spec/salvo_studysense/raw/refs/heads/main/raw_data.xlsx)]
- File Format: Excel (.xlsx) containing columns for Attendance, Previous Marks, Assignment Marks, Study Hours, and Final Marks.

### Methodology & Approach
- Data Preprocessing: Implemented flexible alias matching to automatically map dataset columns to key features. Handled missing numeric values using median imputation via Scikit-Learn's SimpleImputer.
- Modeling & Analytics:
  1. Linear Regression: Used to compute feature correlations, intercept, and variable coefficients to derive a readable dynamic equation for user visibility.
  2. Random Forest Regressor: Applied an ensemble model (100 estimators) to capture non-linear relationships across feature combinations.
  3. Hybrid Rule Override: Incorporated domain-specific logic to prevent excessive attendance penalties when prior academic performance is strong.
  4. Active Learning Feedback: Appends verified user predictions back into the active dataset to update model parameters dynamically over time.
