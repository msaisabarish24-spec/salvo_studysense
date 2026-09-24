import os
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer

# Global State Variables
best_model = None
imputer = None
df_current = None
feature_cols = []
target_col = None
generated_formula_str = "No formula generated yet."
formula_coefs = {}
formula_intercept = 0.0
data_analytics_summary = "No dataset analyzed yet."

STANDARD_KEYS = {
    'Attendance': ['attendance', 'attendance percentage', 'attendance_pct', 'attendance %', 'att'],
    'Previous Marks': ['previous marks', 'previous_marks', 'prev_marks', 'past_marks', 'prev marks'],
    'Assignment Marks': ['assignment marks', 'assignment_marks', 'assignment', 'assignments'],
    'Study Hours': ['study hours', 'study_hours', 'study time', 'hours_studied', 'study hrs'],
    'Final Marks': ['final marks', 'final_marks', 'total_marks', 'target', 'final_score']
}

DEFAULT_FILE = r"C:\Users\malle\Downloads\salvo\salvo\raw_data.xlsx"

def auto_detect_columns(columns):
    col_mapping = {}
    cols_lower = [str(c).strip().lower() for c in columns]
    
    for std_key, aliases in STANDARD_KEYS.items():
        found = None
        for i, original_col in enumerate(columns):
            if cols_lower[i] in aliases:
                found = original_col
                break
        if not found:
            for i, original_col in enumerate(columns):
                if any(alias in cols_lower[i] for alias in aliases):
                    found = original_col
                    break
        col_mapping[std_key] = found
    return col_mapping

def analyze_dataset_and_generate_formula(file_path):
    """
    1. Reads the user-loaded or default Excel file.
    2. Performs deep row/column correlation and missing value analysis.
    3. Derives the explicit mathematical equation dynamically directly from the loaded file.
    """
    global best_model, imputer, df_current, feature_cols, target_col
    global generated_formula_str, formula_coefs, formula_intercept, data_analytics_summary

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file '{file_path}' not found.")

    df_current = pd.read_excel(file_path)
    mapping = auto_detect_columns(df_current.columns)

    detected_features = []
    for key in ['Attendance', 'Previous Marks', 'Assignment Marks', 'Study Hours']:
        if mapping[key] is not None and mapping[key] in df_current.columns:
            detected_features.append(mapping[key])

    target_col = mapping['Final Marks']
    if target_col is None or target_col not in df_current.columns:
        target_col = df_current.columns[-1]

    feature_cols = [c for c in detected_features if c != target_col]

    # --- DEEP ROW & COLUMN ANALYSIS FOR LOADED FILE ---
    n_rows, n_cols = df_current.shape
    numeric_df = df_current[feature_cols + [target_col]].apply(pd.to_numeric, errors='coerce')
    
    null_counts = numeric_df.isnull().sum().to_dict()
    corr_matrix = numeric_df.corr()
    target_corrs = corr_matrix[target_col].drop(target_col)
    
    strongest_col = target_corrs.abs().idxmax() if not target_corrs.empty else "N/A"
    strongest_val = target_corrs[strongest_col] if strongest_col != "N/A" else 0.0

    summary_lines = [
        f"📊 File Analyzed: {os.path.basename(file_path)} ({n_rows} rows x {n_cols} columns)",
        f"🔍 Extracted Features: {', '.join(feature_cols)}",
        f"🎯 Highest Impact Feature: '{strongest_col}' (Correlation: {strongest_val:.3f})",
        f"⚠️ Missing Values Detected: {sum(null_counts.values())}"
    ]
    data_analytics_summary = "\n".join(summary_lines)

    # --- DYNAMIC FORMULA DERIVATION DIRECTLY FROM USER FILE ---
    X = numeric_df[feature_cols].dropna()
    y = numeric_df.loc[X.index, target_col]

    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)

    lin_reg = LinearRegression()
    lin_reg.fit(X_imputed, y)

    formula_intercept = lin_reg.intercept_
    formula_coefs = dict(zip(feature_cols, lin_reg.coef_))

    # Construct equation string dynamically from loaded file's columns and coefficients
    terms = [f"{coef:+.4f} * ({col})" for col, coef in formula_coefs.items()]
    generated_formula_str = f"Final Marks = {formula_intercept:.4f} " + " ".join(terms)

    # ML Regressor for Prediction Pipeline
    best_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    best_model.fit(X_imputed, y)

    return file_path, mapping

try:
    current_data_name, current_mapping = analyze_dataset_and_generate_formula(DEFAULT_FILE)
except Exception:
    current_data_name = "None"

VALID_RANGES = {
    'Attendance': (0.0, 100.0),
    'Previous Marks': (0.0, 100.0),
    'Assignment Marks': (0.0, 50.0),
    'Study Hours': (0.0, 24.0)
}

# Tkinter UI App
class AdaptiveMarksPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STUDYSENSE")
        self.root.geometry("640x920")
        self.root.configure(bg="#FFFFFF")

        title_label = tk.Label(
            root, text="Student Marks Predictor", 
            font=("Arial", 15, "bold"), bg="#FFFFFF", fg="#111111"
        )
        title_label.pack(pady=(12, 2))

        self.dataset_status = tk.Label(
            root, text=f"Active Loaded File: {os.path.basename(current_data_name)} ({len(df_current) if df_current is not None else 0} rows)", 
            font=("Arial", 9, "bold"), bg="#FFFFFF", fg="#007AFF"
        )
        self.dataset_status.pack(pady=(0, 6))

        file_btn_frame = tk.Frame(root, bg="#FFFFFF")
        file_btn_frame.pack(pady=2)

        upload_btn = tk.Button(
            file_btn_frame, text=" Upload File", command=self.upload_new_data,
            font=("Arial", 9, "bold"), bg="#E9ECEF", fg="#212529", relief="flat", padx=10, pady=4, cursor="hand2"
        )
        upload_btn.grid(row=0, column=0, padx=5)

        use_default_btn = tk.Button(
            file_btn_frame, text=" Use Default Raw Data", command=self.use_default_data,
            font=("Arial", 9, "bold"), bg="#E9ECEF", fg="#212529", relief="flat", padx=10, pady=4, cursor="hand2"
        )
        use_default_btn.grid(row=0, column=1, padx=5)

        # Inputs Frame
        form_frame = tk.Frame(root, bg="#FFFFFF")
        form_frame.pack(pady=6)

        self.entries = {}
        self.fields = [
            ("Attendance Percentage (0 - 100 %)", 'Attendance'),
            ("Previous Marks (0 - 100)", 'Previous Marks'),
            ("Assignment Marks (0 - 50)", 'Assignment Marks'),
            ("Study Hours (0 - 24 hrs)", 'Study Hours')
        ]

        for i, (label_text, std_key) in enumerate(self.fields):
            lbl = tk.Label(form_frame, text=label_text, font=("Arial", 9, "bold"), bg="#FFFFFF", anchor="w")
            lbl.grid(row=i*2, column=0, sticky="w", pady=(3, 1), padx=10)

            entry = tk.Entry(
                form_frame, font=("Arial", 10), bg="#F8F9FA", 
                relief="flat", highlightthickness=1, highlightbackground="#CCCCCC", highlightcolor="#007AFF"
            )
            entry.grid(row=i*2+1, column=0, ipady=4, ipadx=10, pady=(0, 5), padx=10)
            self.entries[std_key] = entry

        predict_btn = tk.Button(
            root, text="Predict Final Marks", command=self.predict,
            font=("Arial", 10, "bold"), bg="#007AFF", fg="#FFFFFF",
            activebackground="#0056B3", activeforeground="#FFFFFF",
            relief="flat", padx=20, pady=6, cursor="hand2"
        )
        predict_btn.pack(pady=6)

        self.result_card = tk.Frame(root, bg="#F0F4F8", relief="flat", highlightthickness=1, highlightbackground="#D0D7DE")
        self.result_card.pack(fill="x", padx=25, pady=4)

        self.result_label = tk.Label(
            self.result_card, text="Fill values above to get prediction", 
            font=("Arial", 10), bg="#F0F4F8", fg="#555555"
        )
        self.result_label.pack(pady=6)

        self.weight_note_label = tk.Label(
            self.result_card, text="", 
            font=("Arial", 9, "italic"), bg="#F0F4F8", fg="#0056B3", wraplength=520
        )
        self.weight_note_label.pack(pady=(0, 6))

        # Formula & Analytics Display Panel
        panel_frame = tk.LabelFrame(
            root, text=" Dynamic Formula & Analytics (Derived per User File) ", 
            font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#333333", padx=10, pady=6
        )
        panel_frame.pack(fill="both", expand=True, padx=20, pady=6)

        self.analytics_label = tk.Label(
            panel_frame, text=f"{data_analytics_summary}\n\n📐 Derived Formula:\n{generated_formula_str}", 
            font=("Arial", 8, "bold"), bg="#FFFFFF", fg="#222222", justify="left", anchor="nw", wraplength=520
        )
        self.analytics_label.pack(fill="both", expand=True)

    def upload_new_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if file_path:
            try:
                name, mapping = analyze_dataset_and_generate_formula(file_path)
                self.dataset_status.config(text=f"Active Loaded File: {os.path.basename(name)} ({len(df_current)} rows)")
                self.analytics_label.config(text=f"{data_analytics_summary}\n\n📐 Derived Formula:\n{generated_formula_str}")
                messagebox.showinfo(
                    "Formula Derived", 
                    f"New file loaded successfully!\n\nFormula derived from '{os.path.basename(name)}':\n\n{generated_formula_str}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to analyze uploaded file:\n{e}")

    def use_default_data(self):
        try:
            name, mapping = analyze_dataset_and_generate_formula(DEFAULT_FILE)
            self.dataset_status.config(text=f"Active Loaded File: {os.path.basename(DEFAULT_FILE)} ({len(df_current)} rows)")
            self.analytics_label.config(text=f"{data_analytics_summary}\n\n📐 Derived Formula:\n{generated_formula_str}")
            messagebox.showinfo("Default File Loaded", "Reverted to default dataset and derived base formula.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load default file:\n{e}")

    def predict(self):
        user_data = {}
        missing_keys = []

        for label_text, std_key in self.fields:
            val_str = self.entries[std_key].get().strip()
            if val_str == "":
                missing_keys.append(std_key)
                user_data[std_key] = None
            else:
                try:
                    val = float(val_str)
                    min_val, max_val = VALID_RANGES[std_key]
                    if val < min_val or val > max_val:
                        messagebox.showerror(
                            "Input Rejected", 
                            f"The value for '{std_key}' ({val}) exceeds allowed range [{min_val} to {max_val}].\n\n"
                            "Please re-enter a valid value."
                        )
                        self.entries[std_key].focus_set()
                        return
                    user_data[std_key] = val
                except ValueError:
                    messagebox.showerror("Invalid Input", f"Please enter a valid numeric value for '{std_key}'.")
                    self.entries[std_key].focus_set()
                    return

        if missing_keys:
            missing_names = "\n• " + "\n• ".join(missing_keys)
            choice = messagebox.askyesno(
                "Missing Input Values",
                f"The following field(s) were left blank:{missing_names}\n\n"
                "Do you want to predict anyway using auto-imputation?\n"
                "(Click 'No' to return and enter missing details)"
            )
            if not choice:
                return

        # 1. EXACT MATCH LOOKUP FIRST (Average of matches)
        if len(missing_keys) == 0 and len(feature_cols) == 4:
            match_mask = (
                (df_current[feature_cols[0]] == user_data['Attendance']) &
                (df_current[feature_cols[1]] == user_data['Previous Marks']) &
                (df_current[feature_cols[2]] == user_data['Assignment Marks']) &
                (df_current[feature_cols[3]] == user_data['Study Hours'])
            )
            exact_matches = df_current[match_mask]

            if not exact_matches.empty:
                avg_exact_value = float(exact_matches[target_col].mean())
                match_count = len(exact_matches)
                
                self.result_label.config(
                    text=f"Exact Match Final Marks (Avg): {avg_exact_value:.2f} / 100",
                    font=("Arial", 12, "bold"), fg="#107C41"
                )
                note = f"🎯 {match_count} exact match(es) found in dataset. Displayed average of matching scores."
                self.weight_note_label.config(text=note)
                return

        # 2. CALCULATION USING DYNAMIC FORMULA DERIVED FROM USER FILE
        prev = user_data['Previous Marks'] if user_data['Previous Marks'] is not None else 50.0
        att = user_data['Attendance'] if user_data['Attendance'] is not None else 50.0
        assign = user_data['Assignment Marks'] if user_data['Assignment Marks'] is not None else 25.0
        study = user_data['Study Hours'] if user_data['Study Hours'] is not None else 5.0

        if prev >= 70.0 and att <= 60.0:
            calc_val = (
                0.60 * prev +
                0.25 * (assign * 2) +
                0.10 * (study * 8.33) +
                0.05 * att
            )
            note_text = "⚡ High Previous Marks Detected: Attendance penalty suppressed; priority given to past performance."
        else:
            calc_val = formula_intercept
            for col in feature_cols:
                if 'att' in col.lower():
                    calc_val += formula_coefs[col] * att
                elif 'prev' in col.lower():
                    calc_val += formula_coefs[col] * prev
                elif 'assign' in col.lower():
                    calc_val += formula_coefs[col] * assign
                elif 'study' in col.lower() or 'hour' in col.lower():
                    calc_val += formula_coefs[col] * study
            note_text = f"📐 Score calculated dynamically using the formula derived from '{os.path.basename(current_data_name)}'."

        final_pred = round(min(max(calc_val, 0), 100), 2)

        self.result_label.config(
            text=f"Predicted Final Marks: {final_pred:.2f} / 100",
            font=("Arial", 12, "bold"), fg="#107C41"
        )
        self.weight_note_label.config(text=note_text)

        matches = messagebox.askyesno(
            "Verify Prediction", 
            f"The predicted final mark is {final_pred:.2f}.\n\nDoes this match your expected outcome?"
        )

        if matches:
            new_row = {}
            for col in feature_cols:
                if 'att' in col.lower():
                    new_row[col] = user_data['Attendance'] if user_data['Attendance'] is not None else df_current[col].median()
                elif 'prev' in col.lower():
                    new_row[col] = user_data['Previous Marks'] if user_data['Previous Marks'] is not None else df_current[col].median()
                elif 'assign' in col.lower():
                    new_row[col] = user_data['Assignment Marks'] if user_data['Assignment Marks'] is not None else df_current[col].median()
                elif 'study' in col.lower() or 'hour' in col.lower():
                    new_row[col] = user_data['Study Hours'] if user_data['Study Hours'] is not None else df_current[col].median()
            
            new_row[target_col] = final_pred
            
            updated_df = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)
            updated_df.to_excel(current_data_name, index=False)
            
            analyze_dataset_and_generate_formula(current_data_name)
            self.analytics_label.config(text=f"{data_analytics_summary}\n\n📐 Derived Formula:\n{generated_formula_str}")
            
            messagebox.showinfo(
                "Data Saved", 
                f"Thank you! Entry saved to '{os.path.basename(current_data_name)}' and formula updated."
            )
        else:
            messagebox.showwarning(
                "Apology & Feedback", 
                "We sincerely apologize that the predicted mark did not match your expectations!\n\n"
                "We will use this feedback to further tune and improve our machine learning model."
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = AdaptiveMarksPredictorApp(root)
    root.mainloop()