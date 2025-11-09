import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pymongo
from bson import ObjectId

# --------------------------
# Config / Theme definitions
# --------------------------
LIGHT_THEME = {
    "bg": "#F7F9FB",
    "frame_bg": "#FFFFFF",
    "accent": "#0078D7",
    "text": "#111827",
    "muted": "#6B7280",
    "success": "#16A34A",
}

# --------------------------
# Main Application
# --------------------------
class ExpenseTrackerApp:
    def __init__(self, root,
                 mongo_uri="mongodb://localhost:27017/",
                 db_name="expense_db",
                 collection_name="expenses"):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("960x620")
        self.root.minsize(900, 560)

        # MongoDB
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # State
        self.theme_vars = LIGHT_THEME
        self.description_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Select Category")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.total_expenses = tk.DoubleVar(value=0.0)

        # Search/filter vars
        self.filter_from = tk.StringVar()
        self.filter_to = tk.StringVar()

        # Setup style & UI
        self.setup_style()
        self.build_ui()
        self.apply_theme()  # apply colors
        self.load_all_expenses()

    # --------------------------
    # Styling
    # --------------------------
    def setup_style(self):
        style = ttk.Style(self.root)
        style.configure("TFrame", background=self.theme_vars["bg"])
        style.configure("Card.TFrame", background=self.theme_vars["frame_bg"], relief="flat")
        style.configure("TLabel", background=self.theme_vars["bg"], foreground=self.theme_vars["text"])
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("Accent.TButton", foreground="white")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("My.TFrame", background="#E3F2FD")

    # --------------------------
    # UI Construction
    # --------------------------
    def build_ui(self):
        root = self.root

        # Top bar
        topbar = ttk.Frame(root, padding=(12, 10, 12, 6))
        topbar.pack(fill="x") #geometry-management option used with .pack()

        title = ttk.Label(topbar, text="Expense Tracker", style="Header.TLabel")
        title.pack(side="left") #Places the widget on the left side of the parent window/frame.


        main_frame = ttk.Frame(root, padding=12)
        main_frame.pack(fill="both", expand=True) # expand controls WHETHER a widget receives extra space when the window grows.

        # Left: input card
        left_card = ttk.Frame(main_frame, style="Card.TFrame", padding=12)
        left_card.pack(side="left", fill="y", padx=(0, 8))
        #Sets horizontal external padding:
        #0 No padding on the left
        #8 pixels padding on the right

        # Input fields
        ttk.Label(left_card, text="Description:").grid(row=0, column=0, sticky="w")
        #"w" = West (left)
        #Controls alignment inside the cell
        #align the widget to the left side of its grid cell
        desc_entry = ttk.Entry(left_card, textvariable=self.description_var, width=28)
        desc_entry.grid(row=1, column=0, pady=(0,8))

        ttk.Label(left_card, text="Amount (DZD):").grid(row=2, column=0, sticky="w")
        amt_entry = ttk.Entry(left_card, textvariable=self.amount_var, width=28)
        amt_entry.grid(row=3, column=0, pady=(0,8))

        ttk.Label(left_card, text="Category:").grid(row=4, column=0, sticky="w")
        categories = ["Food", "Transport", "Housing", "Bills", "Clothing", "Health", "Education", "Entertainment", "Travel", "Other"]
        #ttk.Combobox : A dropdown list widget from the themed ttk module.
        cat_combo = ttk.Combobox(left_card, textvariable=self.category_var, values=categories, state="readonly", width=26)
        #state="readonly" : User must pick from the list (can't type custom text)
        cat_combo.grid(row=5, column=0, pady=(0,8))

        ttk.Label(left_card, text="Date:").grid(row=6, column=0, sticky="w")
        date_entry = DateEntry(left_card, textvariable=self.date_var, width=26, date_pattern='yyyy-mm-dd')
        date_entry.grid(row=7, column=0, pady=(0,10))

        # Action buttons
        btn_frame = ttk.Frame(left_card)
        btn_frame.grid(row=8, column=0, pady=6)

        add_btn = tk.Button(btn_frame, text="➕ Add", command=self.add_expense, bg="#16A34A", fg="white", width=12)
        add_btn.grid(row=0, column=0, padx=4)

        edit_btn = tk.Button(btn_frame, text="✏️ Edit Selected", command=self.edit_selected, bg="#0EA5E9", fg="white", width=12)
        edit_btn.grid(row=0, column=1, padx=4)

        delete_btn = tk.Button(btn_frame, text="🗑 Delete", command=self.delete_selected, bg="#DC3545", fg="white", width=12)
        delete_btn.grid(row=0, column=2, padx=4)

        # Export & Graph buttons
        extra_frame = ttk.Frame(left_card)
        extra_frame.grid(row=9, column=0, pady=(8,0))

        graph_btn = tk.Button(extra_frame, text="📊 Show Graphs", command=self.show_graphs, bg="#7C3AED", fg="white", width=14)
        graph_btn.grid(row=0, column=0, padx=4, pady=4)

        exp_csv_btn = tk.Button(extra_frame, text="💾 Export CSV", command=self.export_csv, bg="#F59E0B", fg="black", width=14)
        exp_csv_btn.grid(row=1, column=0, padx=4, pady=4)

        exp_xl_btn = tk.Button(extra_frame, text="📄 Export Excel", command=self.export_excel, bg="#F97316", fg="white", width=14)
        exp_xl_btn.grid(row=2, column=0, padx=4, pady=4)

        # Right: table + filters
        right_card = ttk.Frame(main_frame, style="Card.TFrame", padding=12)
        right_card.pack(side="left", fill="both", expand=True)

        # Filters row
        filters = ttk.Frame(right_card)
        filters.pack(fill="x", pady=(0,8))

        ttk.Label(filters, text="From:").grid(row=0, column=2, sticky="w")
        DateEntry(filters, textvariable=self.filter_from, width=14, date_pattern='yyyy-mm-dd').grid(row=1, column=2, padx=(0,8))

        ttk.Label(filters, text="To:").grid(row=0, column=3, sticky="w")
        DateEntry(filters, textvariable=self.filter_to, width=14, date_pattern='yyyy-mm-dd').grid(row=1, column=3, padx=(0,8))

        search_btn = ttk.Button(filters, text="Apply Filters", command=self.apply_filters)
        search_btn.grid(row=1, column=4, padx=(20,20))

        clear_btn = ttk.Button(filters, text="Clear Filters", command=self.clear_filters)
        clear_btn.grid(row=1, column=5, padx=(8,0))

        # Table
        columns = ("_id", "description", "amount", "category", "date")
        self.tree = ttk.Treeview(right_card, columns=columns, show="headings", selectmode="extended")
        for col in columns:
            self.tree.heading(col, text=col.capitalize(), command=lambda c=col: self.sort_by_column(c, False))
            if col == "_id":
                self.tree.column(col, width=0, stretch=False, anchor="center")
            else:
                self.tree.column(col, anchor="center", width=140)
        self.tree.pack(fill="both", expand=True, pady=(6, 0))

        # alternating row tags
        self.tree.tag_configure("odd", background="#FBFBFB")
        self.tree.tag_configure("even", background="#FFFFFF")

        # bind double-click to edit
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

        # total summary
        summary_frame = ttk.Frame(right_card)
        summary_frame.pack(fill="x", pady=(8,0))
        ttk.Label(summary_frame, text="Total:", font=("Segoe UI", 11, "bold")).pack(side="left")
        ttk.Label(summary_frame, textvariable=self.total_expenses, font=("Segoe UI", 11, "bold")).pack(side="left", padx=(6,0))

    # --------------------------
    # Theme handling
    # --------------------------
    def apply_theme(self):
        self.theme_vars = LIGHT_THEME
        
        bg = self.theme_vars["bg"]
        frame_bg = self.theme_vars["frame_bg"]
        text = self.theme_vars["text"]
        accent = self.theme_vars["accent"]

        self.root.configure(bg=bg)
        # iterate widgets and apply where appropriate (safe, minimal)
        for w in self.root.winfo_children():
            try:
                w.configure(background=bg)
            except Exception:
                pass
        style = ttk.Style(self.root)
        # Treeview heading/row colors
        style.configure("Treeview", background=frame_bg, fieldbackground=frame_bg, foreground=text)
        style.configure("Treeview.Heading", background=frame_bg, foreground=text)




    # --------------------------
    # Data operations
    # --------------------------
    def validate_inputs(self, desc, amount_text, category, date_str):
        # inline minimal validation returns (ok, message)
        if not desc:
            return False, "Description required."
        if not amount_text:
            return False, "Amount required."
        try:
            amt = float(amount_text)
            if amt <= 0:
                return False, "Amount must be > 0."
        except ValueError:
            return False, "Amount must be a number."
        if category not in ["Food", "Transport", "Housing", "Bills", "Clothing", "Health", "Education", "Entertainment", "Travel", "Other"]:
            return False, "Please select a category."
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Date must be YYYY-MM-DD."
        return True, ""

    def add_expense(self):
        #.get() reads the current string value of that StringVar.
        # .strip() is a standard Python string method which returns a new string with 
        #any leading or trailing whitespace removed (spaces, tabs, newline characters) from the string returned by .get()
        desc = self.description_var.get().strip()
        amt_text = self.amount_var.get().strip()
        cat = self.category_var.get()
        date_str = self.date_var.get().strip()

        ok, msg = self.validate_inputs(desc, amt_text, cat, date_str)
        if not ok:
            messagebox.showwarning("Validation", msg)
            return

        amt = float(amt_text)
        rec = {"description": desc, "amount": amt, "category": cat, "date": date_str, "created_at": datetime.utcnow()}
        res = self.collection.insert_one(rec)

        # insert into tree (show _id as string)
        _id_str = str(res.inserted_id)
        idx = len(self.tree.get_children())
        tag = "even" if idx % 2 == 0 else "odd"
        self.tree.insert("", "end", values=(_id_str, desc, f"{amt:.2f}", cat, date_str), tags=(tag,))
        self.total_expenses.set(self.total_expenses.get() + amt)

        # clear inputs
        self.description_var.set("")
        self.amount_var.set("")
        self.category_var.set("Select Category")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))

    def load_all_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        total = 0.0
        recs = list(self.collection.find().sort("date", pymongo.ASCENDING))
        for i, r in enumerate(recs):
            _id_str = str(r.get("_id"))
            desc = r.get("description", "")
            amt = float(r.get("amount", 0.0))
            cat = r.get("category", "")
            date = r.get("date", "")
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(_id_str, desc, f"{amt:.2f}", cat, date), tags=(tag,))
            total += amt
        self.total_expenses.set(total)

    def apply_filters(self):
        date_from = self.filter_from.get().strip()
        date_to = self.filter_to.get().strip()

        # Build query
        query = {}
        if date_from:
            try:
                # module datetime.
                datetime.strptime(date_from, "%Y-%m-%d") # strptime : string representation of a date into a datetime.datetime object
                query["date"] = query.get("date", {})
                query["date"]["$gte"] = date_from
            except ValueError:
                messagebox.showwarning("Filter error", "From date must be YYYY-MM-DD")
                return
        if date_to:
            try:
                datetime.strptime(date_to, "%Y-%m-%d")
                query["date"] = query.get("date", {})
                query["date"]["$lte"] = date_to
            except ValueError:
                messagebox.showwarning("Filter error", "To date must be YYYY-MM-DD")
                return
                
        #query = {"date": {"$gte": start, "$lte": end}}
        # find
        for item in self.tree.get_children():
            self.tree.delete(item)

        total = 0.0
        recs = list(self.collection.find(query).sort("date", pymongo.ASCENDING))
        #.sort("date", pymongo.ASCENDING) tells the cursor to sort the matched documents by the "date" field in ascending order.

        for i, r in enumerate(recs):
            _id_str = str(r.get("_id"))
            desc = r.get("description", "")
            amt = float(r.get("amount", 0.0))
            cat = r.get("category", "")
            date = r.get("date", "")
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(_id_str, desc, f"{amt:.2f}", cat, date), tags=(tag,))
            total += amt
        self.total_expenses.set(total)

    def clear_filters(self):
        self.filter_from.set("")
        self.filter_to.set("")
        self.load_all_expenses()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection", "No expense selected.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(selected)} selected item(s)?"):
            return
        for item in selected:
            vals = self.tree.item(item, "values")
            _id = vals[0]
            try:
                obj_id = ObjectId(_id)
            except Exception:
                continue
            amount = float(vals[2])
            self.collection.delete_one({"_id": obj_id})
            self.total_expenses.set(self.total_expenses.get() - amount)
            self.tree.delete(item)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Edit", "Select a single item to edit (double click row or select then click Edit).")
            return
        if len(selected) > 1:
            messagebox.showinfo("Edit", "Please select only one item to edit at a time.")
            return

        item = selected[0]
        vals = self.tree.item(item, "values")
        _id = vals[0]
        rec = self.collection.find_one({"_id": ObjectId(_id)})
        if not rec:
            messagebox.showerror("Edit", "Record not found.")
            return

        # Edit dialog
        dlg = tk.Toplevel(self.root)
        # Toplevel is a widget that creates a new top‐level window (a separate window) in your Tkinter application.
        dlg.title("Edit Expense")
        dlg.geometry("360x300")
        dlg.transient(self.root) # If the parent is iconified (minimised), the transient window will also be iconified.
        dlg.grab_set() # grab_set() makes the Toplevel window grab all events in the application (mouse, keyboard, etc) so that clicks and inputs go only to this window and its children.

        tk.Label(dlg, text="Description:").pack(anchor="w", padx=12, pady=(12,0))
        desc_var = tk.StringVar(value=rec.get("description", ""))
        tk.Entry(dlg, textvariable=desc_var, width=40).pack(padx=12, pady=(0,8))

        tk.Label(dlg, text="Amount (DZD):").pack(anchor="w", padx=12)
        amt_var = tk.StringVar(value=f"{float(rec.get('amount', 0.0)):.2f}")
        tk.Entry(dlg, textvariable=amt_var, width=40).pack(padx=12, pady=(0,8))

        tk.Label(dlg, text="Category:").pack(anchor="w", padx=12)
        cat_var = tk.StringVar(value=rec.get("category", "Other"))
        ttk.Combobox(dlg, textvariable=cat_var, values=["Food","Transport","Housing","Bills","Clothing","Health","Education","Entertainment","Travel","Other"], state="readonly", width=36).pack(padx=12, pady=(0,8))

        tk.Label(dlg, text="Date:").pack(anchor="w", padx=12)
        date_var = tk.StringVar(value=rec.get("date", datetime.now().strftime("%Y-%m-%d")))
        DateEntry(dlg, textvariable=date_var, width=36, date_pattern='yyyy-mm-dd').pack(padx=12, pady=(0,8))

        def save_edits():
            desc_new = desc_var.get().strip()
            amt_new = amt_var.get().strip()
            cat_new = cat_var.get()
            date_new = date_var.get().strip()
            ok, msg = self.validate_inputs(desc_new, amt_new, cat_new, date_new)
            if not ok:
                messagebox.showwarning("Validation", msg)
                return
            amt_new_f = float(amt_new)
            # update db
            self.collection.update_one({"_id": ObjectId(_id)}, {"$set": {"description": desc_new, "amount": amt_new_f, "category": cat_new, "date": date_new}})
            # refresh table (simplest: reload filters or all)
            self.load_all_expenses()
            dlg.destroy()

        ttk.Button(dlg, text="Save", command=save_edits).pack(pady=12)

    # --------------------------
    # Sorting helper
    # --------------------------
    def sort_by_column(self, col, descending):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        # try numeric sort
        try:
            data = [(float(v), k) for (v, k) in data]
        except Exception:
            data = [(v.lower(), k) for (v, k) in data]
        data.sort(reverse=descending)
        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)
        # reverse sort next time
        self.tree.heading(col, command=lambda c=col: self.sort_by_column(c, not descending))

    # --------------------------
    # Export / Graph
    # --------------------------
    def export_csv(self):
        recs = list(self.collection.find({}, {"_id":0})) # it tells MongoDB to return all fields except the _id field
        if not recs:
            messagebox.showinfo("Export", "No records to export.")
            return
        df = pd.DataFrame(recs)
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        # asksaveasfilename() displays a Save As file-dialog window that asks the user to select (or type) 
        #a file name and location to save a file. It then returns the selected file path as a string.
        if path:
            df.to_csv(path, index=False)
            messagebox.showinfo("Export", f"Exported to {path}")

    def export_excel(self):
        recs = list(self.collection.find({}, {"_id":0}))
        if not recs:
            messagebox.showinfo("Export", "No records to export.")
            return
        df = pd.DataFrame(recs)
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if path:
            df.to_excel(path, index=False, engine="openpyxl")
            messagebox.showinfo("Export", f"Exported to {path}")

    def show_graphs(self):
        recs = list(self.collection.find({}, {"_id":0}))
        if not recs:
            messagebox.showinfo("Graphs", "No data to graph.")
            return
        df = pd.DataFrame(recs)
        # Ensure date column present
        if "date" not in df.columns:
            messagebox.showinfo("Graphs", "No date data available.")
            return

        # create dialog
        dlg = tk.Toplevel(self.root)
        dlg.title("Expense Charts")
        dlg.geometry("900x600")
        dlg.transient(self.root)

        # pie by category
        fig1 = plt.Figure(figsize=(4,4))
        ax1 = fig1.add_subplot(111) 
        # equivalent to: fig.add_subplot(1, 1, 1) (number of rows in the subplot grid, number of columns in the subplot grid, index of the subplot)
        cat_sum = df.groupby("category")["amount"].sum() #perform a group-by and aggregation
        ax1.pie(cat_sum, labels=cat_sum.index, autopct='%1.1f%%', startangle=90) #Rotates the start of the pie so that the first wedge starts at 90°
        ax1.set_title("Expenses by Category")

        canvas1 = FigureCanvasTkAgg(fig1, master=dlg)
        # FigureCanvasTkAgg is a class in matplotlib.backends.backend_tkagg 
        # that creates a Tkinter-compatible canvas widget from a matplotlib Figure object.
        canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=6, pady=6)
        canvas1.draw()

        # bar by date
        fig2 = plt.Figure(figsize=(5,4))
        ax2 = fig2.add_subplot(111)
        date_sum = df.groupby("date")["amount"].sum()
        date_sum.plot(kind="bar", ax=ax2)
        ax2.set_title("Expenses by Date")
        ax2.set_ylabel("Amount (DZD)")
        ax2.set_xlabel("Date")
        for label in ax2.get_xticklabels():
            label.set_rotation(45)

        canvas2 = FigureCanvasTkAgg(fig2, master=dlg)
        canvas2.get_tk_widget().pack(side="left", fill="both", expand=True, padx=6, pady=6)
        canvas2.draw()

    # --------------------------
    # Run app
    # --------------------------
def main():
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
