# Expense Tracker App

A desktop GUI application built with Python & Tkinter for tracking personal expenses — store, edit, delete expenses, filter by date, export to CSV/Excel, and visualize with charts.

---

## 📝 Table of Contents

- [About](#about)  
- [Features](#features)  
- [Built with](#built-with)  
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
  - [Usage](#usage)  
- [Project Structure](#project-structure)  
- [Future Improvements](#future-improvements)  
- [Contributing](#contributing)  
- [License](#license)  
- [Author](#author)  

---

## About  
This application (“Expense Tracker”) allows you to:

- Add expenses (description, amount in DZD, category, date)  
- Edit or delete recorded expenses  
- Filter expenses by date range  
- Export data to CSV or Excel  
- View charts: expense breakdown by category (pie chart), and expense amount by date (bar chart)  
- Use a simple MongoDB backend (via pymongo) and a Tkinter UI  

It was built to provide an easy-to-use personal finance tool you can run locally.

---

## Features  
- ✅ Add expense entries with date picker (`tkcalendar.DateEntry`)  
- ✅ Edit or delete selected entries  
- ✅ Filter by “From” and “To” dates  
- ✅ Automatic total expense summary  
- ✅ Export data: CSV and Excel  
- ✅ Visualisation: pie chart (by category) and bar chart (by date) via Matplotlib  
- ✅ Stores data in MongoDB (`mongodb://localhost:27017/` by default)  
- ✅ Themed UI layout with Tkinter / ttk  

---

## Built with  
- Python 3.x  
- [`tkinter`](https://docs.python.org/3/library/tkinter.html) — standard Python GUI library  
- [`tkcalendar`](https://github.com/j4321/tkcalendar) — date picker widget  
- [`pymongo`](https://pymongo.readthedocs.io/) — MongoDB driver for Python  
- [`pandas`](https://pandas.pydata.org/) — for data export and manipulation  
- [`matplotlib`](https://matplotlib.org/) — for plotting charts  
- [`ttk`](https://docs.python.org/3/library/tkinter.ttk.html) — themed Tkinter widgets  

---

## Getting Started  

### Prerequisites  
Make sure you have:  
- Python 3 installed  
- MongoDB running locally (or accessible via URI)  
- Required Python libraries (see next section)  

### Installation  
1. Clone the repository:  
   ```sh
   git clone https://github.com/your-username/expense-tracker.git
   cd expense-tracker
   ```  
2. (Optional) Create & activate a virtual environment:  
   ```sh
   python3 -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```  
3. Install dependencies:  
   ```sh
   pip install -r requirements.txt
   ```  
4. Ensure MongoDB is running and accessible at the configured URI (default: `mongodb://localhost:27017/`).

### Usage  
Run the main application script:  
```sh
python app.py
```  
You should see the main window with input fields (description, amount, category, date) on the left and the expense table on the right.  
- Add new expenses via the form.  
- Edit or delete a selected expense.  
- Use the date filter to show a subset of expenses.  
- Export to CSV or Excel via the buttons.  
- Click “Show Graphs” to view charts.  

---

## Project Structure  
```
expense-tracker/
├── app.py               # Main application script
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── …                    # (Optional additional modules / assets)
```  
Feel free to reorganize as needed (e.g., split UI vs data access modules).

---

## Future Improvements  
Here are a few ideas for future enhancements:  
- 🔧 Store `date` field in MongoDB as a proper `Date` type (not just string) for more robust querying.  
- 📈 Add filtering by category, amount range, or recurrence.  
- 🧮 Add budgeting features (monthly budget, alerts when threshold exceeded).  
- 🖥 Improve UI: dark theme, custom styling, responsive resizing.  
- 📱 Build a standalone executable for non-Python users (via PyInstaller or similar).  
- ☁️ Support cloud database / multi-user sync.  

---

## Contributing  
Contributions are welcome! If you’d like to contribute:  
1. Fork this repository.  
2. Create a new branch (`git checkout -b feature/YourFeature`).  
3. Make your changes and commit (`git commit -m 'Add some feature'`).  
4. Push to the branch (`git push origin feature/YourFeature`).  
5. Open a pull request and describe the changes you’ve made.  

Please ensure code is well-commented and includes tests if applicable.

---

## License  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  

---

## Author  
Your Name — [your.email@example.com](mailto:your.email@example.com)  
GitHub: [https://github.com/your-username](https://github.com/your-username)  
