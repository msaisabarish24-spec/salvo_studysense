# 🎓 STUDYSENSE
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
