import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

class LoanEligibilityApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Loan Eligibility Prediction")
        self.master.geometry("600x400")

        # Title label
        self.title_label = tk.Label(master, text="Loan Eligibility Prediction", font=("Helvetica", 22, "bold"), bg="#e8f0f2", fg="#333")
        self.title_label.pack(pady=20)

        # Frame for upload button
        self.button_frame = tk.Frame(master, bg="#e8f0f2")
        self.button_frame.pack(pady=10)

        # Upload button
        self.upload_button = tk.Button(self.button_frame, text="Upload CSV File", command=self.upload_file, bg="#05679b", fg="white", font=("Helvetica", 16, "bold"), activebackground="#05679b", bd=0, relief="flat")
        self.upload_button.pack(pady=10)

        # Load and preprocess training data for the model
        self.load_and_preprocess_training_data()

        # Footer label
        self.footer_label = tk.Label(master, text="© 2024 Loan Predictor", font=("Helvetica", 10), bg="#e8f0f2", fg="#666")
        self.footer_label.pack(side='bottom', pady=10)

    def load_and_preprocess_training_data(self):
        data = pd.read_csv("train.csv")  # Replace with your training data path
        # Impute missing values
        data.Gender.fillna('Male', inplace=True)
        data.Married.fillna('Yes', inplace=True)
        data.Dependents.fillna('0', inplace=True)
        data.Self_Employed.fillna('No', inplace=True)
        data.LoanAmount.fillna(data.LoanAmount.mean(), inplace=True)
        data.Loan_Amount_Term.fillna(360.0, inplace=True)
        data.Credit_History.fillna(1.0, inplace=True)

        # Prepare features and labels
        X = data.drop(columns=['Loan_ID', 'Loan_Status']).values  # Drop Loan_ID and Loan_Status
        y = data['Loan_Status'].map({'Y': 1, 'N': 0}).values  # Encode target variable

        # Encoding categorical data
        self.labelencoder_X = {}
        for i in [0, 1, 2, 3, 4, 10]:  # Indices of categorical columns
            le = LabelEncoder()
            X[:, i] = le.fit_transform(X[:, i])
            self.labelencoder_X[i] = le  # Store the encoder for later use

        # Feature scaling
        self.sc = StandardScaler()
        self.X_train = self.sc.fit_transform(X)

        # Handle class imbalance
        smote = SMOTE(random_state=0)
        self.X_train_balanced, self.y_train_balanced = smote.fit_resample(self.X_train, y)

        # Fit the model
        self.model = RandomForestClassifier(random_state=0)
        self.model.fit(self.X_train_balanced, self.y_train_balanced)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                user_data = pd.read_csv(file_path)
                predictions, rejection_reasons, eligible_count, not_eligible_count = self.predict_loan_eligibility(user_data)
                self.show_results(user_data, predictions, rejection_reasons, eligible_count, not_eligible_count)

            except Exception as e:
                messagebox.showerror("Error", f"Error processing the file: {str(e)}")

    def show_results(self, user_data, predictions, rejection_reasons, eligible_count, not_eligible_count):
        result_window = tk.Toplevel(self.master)
        result_window.title("Loan Eligibility Results")
        result_window.geometry("800x600")

        # Display count of eligible and not eligible candidates
        count_label = tk.Label(result_window, text=f"Eligible: {eligible_count} | Not Eligible: {not_eligible_count}", 
                               font=("Helvetica", 16, "bold"), fg="#333")
        count_label.pack(pady=10)

        # Create a notebook for tabs
        notebook = ttk.Notebook(result_window)
        notebook.pack(expand=True, fill='both')

        # Create frames for each tab
        eligible_frame = ttk.Frame(notebook)
        not_eligible_frame = ttk.Frame(notebook)

        # Add frames to the notebook
        notebook.add(eligible_frame, text="Eligible Candidates")
        notebook.add(not_eligible_frame, text="Not Eligible Candidates")

        # Treeview for eligible candidates
        eligible_tree = ttk.Treeview(eligible_frame, columns=("Loan_ID", "Gender", "Married", "Dependents", 
                                                               "Education", "Self_Employed", "ApplicantIncome", 
                                                               "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", 
                                                               "Credit_History", "Property_Area", "Status"),
                                       show="headings")
        for col in eligible_tree["columns"]:
            eligible_tree.heading(col, text=col)
            eligible_tree.column(col, anchor="center", width=100)
        eligible_tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Treeview for not eligible candidates
        not_eligible_tree = ttk.Treeview(not_eligible_frame, columns=("Loan_ID", "Gender", "Married", "Dependents", 
                                                                       "Education", "Self_Employed", "ApplicantIncome", 
                                                                       "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", 
                                                                       "Credit_History", "Property_Area", "Status", "Reason"),
                                           show="headings")
        for col in not_eligible_tree["columns"]:
            not_eligible_tree.heading(col, text=col)
            not_eligible_tree.column(col, anchor="center", width=100)
        not_eligible_tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Add eligible candidates to treeview
        for index, row in user_data.iterrows():
            if predictions[index] == 1:
                eligible_tree.insert("", "end", values=(
                    row['Loan_ID'], row['Gender'], row['Married'], row['Dependents'], 
                    row['Education'], row['Self_Employed'], row['ApplicantIncome'], 
                    row['CoapplicantIncome'], row['LoanAmount'], row['Loan_Amount_Term'], 
                    row['Credit_History'], row['Property_Area'], "Eligible"))

        # Add not eligible candidates to treeview
        for index, row in user_data.iterrows():
            if predictions[index] == 0:
                not_eligible_tree.insert("", "end", values=(
                    row['Loan_ID'], row['Gender'], row['Married'], row['Dependents'], 
                    row['Education'], row['Self_Employed'], row['ApplicantIncome'], 
                    row['CoapplicantIncome'], row['LoanAmount'], row['Loan_Amount_Term'], 
                    row['Credit_History'], row['Property_Area'], "Not Eligible", 
                    rejection_reasons[index]))

    def encode_features(self, row):
        """ Encode categorical features for a single row of data. """
        row_encoded = row.copy()
        for i in [0, 1, 2, 3, 4, 10]:  # Indices of categorical columns
            if row[i] in self.labelencoder_X[i].classes_:
                row_encoded[i] = self.labelencoder_X[i].transform([row[i]])[0]
            else:
                row_encoded[i] = -1  # Unseen labels assigned -1
        return row_encoded

    def predict_loan_eligibility(self, data):
        rejection_reasons = []
        predictions = []
        eligible_count = 0
        not_eligible_count = 0

        for index, row in data.iterrows():
            # Exclude Loan_ID from processing
            user_data = row.drop(labels=['Loan_ID']).copy()  

            # Check for conditions that lead to rejection
            if row['Credit_History'] < 1:
                rejection_reasons.append("Poor credit history.")
                predictions.append(0)
                not_eligible_count += 1
            elif row['LoanAmount'] > 500:
                rejection_reasons.append("Loan amount exceeds the limit.")
                predictions.append(0)
                not_eligible_count += 1
            elif row['ApplicantIncome'] < 1500:
                rejection_reasons.append("Insufficient income.")
                predictions.append(0)
                not_eligible_count += 1
            else:
                # Encode features for prediction
                user_data_encoded = self.encode_features(user_data.values)
                user_data_encoded = user_data_encoded.reshape(1, -1)
                user_data_scaled = self.sc.transform(user_data_encoded)
                prediction = self.model.predict(user_data_scaled)[0]
                predictions.append(prediction)

                if prediction == 1:
                    eligible_count += 1
                    rejection_reasons.append("")
                else:
                    not_eligible_count += 1
                    rejection_reasons.append("Rejected by model prediction.")

        return predictions, rejection_reasons, eligible_count, not_eligible_count


# Create main application window
root = tk.Tk()
app = LoanEligibilityApp(root)
root.mainloop()
