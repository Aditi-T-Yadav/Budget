import csv
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import defaultdict

class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker App")
        self.budget_data = self.read_data()
        self.create_gui()

    def read_data(self):
        try:
            with open('budget_data.csv', 'r') as file:
                reader = csv.DictReader(file)
                data = list(reader)
            return data
        except FileNotFoundError:
            return []

    def write_data(self):
        with open('budget_data.csv', 'w', newline='') as file:
            fieldnames = ['Date', 'Category', 'Type', 'Amount']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.budget_data)

    def calculate_budget(self):
        income = sum(float(item['Amount']) for item in self.budget_data if item['Type'] == 'Income')
        expenses = sum(float(item['Amount']) for item in self.budget_data if item['Type'] == 'Expense')
        remaining_budget = income - expenses
        return remaining_budget

    def expense_analysis(self):
        expense_by_category = defaultdict(float)
        for item in self.budget_data:
            if item['Type'] == 'Expense':
                category = item['Category']
                amount = float(item['Amount'])
                expense_by_category[category] += amount
        return expense_by_category

    def create_gui(self):
        # GUI components
        self.notebook = ttk.Notebook(self.root)

        self.income_expense_frame = ttk.Frame(self.notebook)
        self.summary_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.income_expense_frame, text="Enter Income/Expense")
        self.notebook.add(self.summary_frame, text="Budget Summary")
        self.notebook.add(self.analysis_frame, text="Expense Analysis")

        # Labels and entry widgets for income/expense entry
        ttk.Label(self.income_expense_frame, text="Date (YYYY-MM-DD):").grid(column=0, row=0, padx=10, pady=5)
        self.date_entry = ttk.Entry(self.income_expense_frame)
        self.date_entry.grid(column=1, row=0, padx=10, pady=5)

        ttk.Label(self.income_expense_frame, text="Category:").grid(column=0, row=1, padx=10, pady=5)
        self.category_entry = ttk.Entry(self.income_expense_frame)
        self.category_entry.grid(column=1, row=1, padx=10, pady=5)

        ttk.Label(self.income_expense_frame, text="Type (Income/Expense):").grid(column=0, row=2, padx=10, pady=5)
        self.type_entry = ttk.Entry(self.income_expense_frame)
        self.type_entry.grid(column=1, row=2, padx=10, pady=5)

        ttk.Label(self.income_expense_frame, text="Amount:").grid(column=0, row=3, padx=10, pady=5)
        self.amount_entry = ttk.Entry(self.income_expense_frame)
        self.amount_entry.grid(column=1, row=3, padx=10, pady=5)

        ttk.Button(self.income_expense_frame, text="Add Entry", command=self.add_entry).grid(column=0, row=4, columnspan=2, pady=10)

        # Budget summary
        self.budget_summary_label = ttk.Label(self.summary_frame, text="")
        self.budget_summary_label.grid(column=0, row=0, padx=10, pady=5)

        ttk.Button(self.summary_frame, text="Refresh", command=self.refresh_summary).grid(column=0, row=1, pady=10)

        # Expense analysis
        self.analysis_text = tk.Text(self.analysis_frame, wrap="word", width=40, height=10)
        self.analysis_text.grid(column=0, row=0, padx=10, pady=5)
        self.analysis_text.config(state=tk.DISABLED)

        ttk.Button(self.analysis_frame, text="Refresh", command=self.refresh_analysis).grid(column=0, row=1, pady=10)

        # Expense trend chart
        self.figure, self.ax = plt.subplots(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.analysis_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(column=1, row=0, padx=10, pady=5)

        ttk.Button(self.analysis_frame, text="Refresh Chart", command=self.refresh_chart).grid(column=1, row=1, pady=10)

        self.notebook.pack(expand=True, fill='both')

    def add_entry(self):
        date = self.date_entry.get()
        category = self.category_entry.get()
        entry_type = self.type_entry.get()
        amount = float(self.amount_entry.get())

        if not date or not category or not entry_type or not amount:
            messagebox.showerror("Error", "All fields must be filled.")
            return

        self.budget_data.append({'Date': date, 'Category': category, 'Type': entry_type, 'Amount': amount})
        self.write_data()
        self.clear_entry_fields()
        messagebox.showinfo("Success", "Entry added successfully!")

    def clear_entry_fields(self):
        self.date_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def refresh_summary(self):
        remaining_budget = self.calculate_budget()
        self.budget_summary_label.config(text=f"Remaining Budget: ${remaining_budget:.2f}")

    def refresh_analysis(self):
        analysis_data = self.expense_analysis()
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete("1.0", tk.END)
        for category, amount in analysis_data.items():
            self.analysis_text.insert(tk.END, f"{category}: ${amount:.2f}\n")
        self.analysis_text.config(state=tk.DISABLED)

    def refresh_chart(self):
        analysis_data = self.expense_analysis()

        categories = list(analysis_data.keys())
        amounts = list(analysis_data.values())

        self.ax.clear()
        self.ax.bar(categories, amounts, color='blue')
        self.ax.set_xlabel('Expense Categories')
        self.ax.set_ylabel('Amount (USD)')
        self.ax.set_title('Expense Analysis')

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetTrackerApp(root)
    root.mainloop()
