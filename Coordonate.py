import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import numpy as np
import matplotlib.pyplot as plt

# Adaugă baza de date cu formule la începutul fișierului
FORMULAS_DB = {
    # Formule matematice
    "Suma": "A + B",
    "Diferenta": "A - B",
    "Produsul": "A * B",
    "Catul": "A / B if B != 0 else 'Eroare: Div/0'",  # Evita divizarea la 0
    "Patratul": "A ** 2",
    "Radacina patrata": "A ** 0.5 if A >= 0 else 'Eroare: Negativ'",  # Evita radacina patrata a numerelor negative
    "Exponential": "A ** B",
    "Logaritm natural": "np.log(A) if A > 0 else 'Eroare: A <= 0'",  # Necesita A > 0
    "Logaritm baza 10": "np.log10(A) if A > 0 else 'Eroare: A <= 0'",  # Necesita A > 0
    "Sinus": "np.sin(A)",  # A in radiani
    "Cosinus": "np.cos(A)",  # A in radiani
    "Tangenta": "np.tan(A)",  # A in radiani
    "Cotangenta": "1 / np.tan(A) if np.tan(A) != 0 else 'Eroare: Div/0'",  # Evita divizarea la 0
    "Aria cercului": "np.pi * (A ** 2)",  # A = raza
    "Perimetrul cercului": "2 * np.pi * A",  # A = raza
    "Aria triunghiului": "0.5 * A * B",  # A = baza, B = inaltimea
    "Aria dreptunghiului": "A * B",  # A = lungime, B = latime
    "Aria trapezului": "0.5 * (A + B) * C",  # A si B = baze, C = inaltimea

    # Formule fizice
    "Viteza": "A / B if B != 0 else 'Eroare: Div/0'",  # A = distanta, B = timp
    "Forta": "A * B",  # A = masa, B = acceleratia
    "Energie cinetica": "0.5 * A * (B ** 2)",  # A = masa, B = viteza
    "Energie potentiala": "A * 9.81 * B",  # A = masa, B = inaltime
    "Presiune": "A / B if B != 0 else 'Eroare: Div/0'",  # A = forta, B = arie
    "Densitate": "A / B if B != 0 else 'Eroare: Div/0'",  # A = masa, B = volum
    "Putere": "A / B if B != 0 else 'Eroare: Div/0'",  # A = lucru mecanic, B = timp
    "Rezistenta electrica": "A / B if B != 0 else 'Eroare: Div/0'",  # A = tensiune, B = curent
    "Tensiune electrica": "A * B",  # A = rezistenta, B = curent
    "Frecventa": "1 / A if A != 0 else 'Eroare: Div/0'",  # A = perioada
    "Lungimea de unda": "A / B if B != 0 else 'Eroare: Div/0'",  # A = viteza undei, B = frecventa

    # Alte formule utile
    "Media aritmetica": "(A + B) / 2",
    "Media geometrica": "(A * B) ** 0.5 if A >= 0 and B >= 0 else 'Eroare: Negativ'",
    "Distanta in plan 2D": "((A - C) ** 2 + (B - D) ** 2) ** 0.5",  # A, B = coordonate punct 1; C, D = coordonate punct 2
    "Distanta in plan 3D": "((A - C) ** 2 + (B - D) ** 2 + (E - F) ** 2) ** 0.5",  # A, B, E = punct 1; C, D, F = punct 2
}

class DataTableApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Table and Graphing App")
        self.geometry("900x600")
        
        # Initialize table structure
        self.columns = ["Column1", "Column2"]
        self.data = []  # each row is a dict keyed by column name
        self.column_formulas = {}  # Dicționar pentru a stoca formulele asociate coloanelor
        self.auto_update_enabled = True  # Controleaza actualizarea automata
        
        # Create UI frames and menus
        self.create_menu()
        self.create_table_frame()
        self.create_control_frame()
        self.create_graph_settings_frame()
        
        self.update_table_view()
        self.update_graph_options()
        
        # Porneste actualizarea automata
        self.start_auto_update()

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def create_table_frame(self):
        table_frame = ttk.Frame(self)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the Treeview widget to display table data
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings", selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Set up scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_y.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side=tk.TOP, fill=tk.X)
        self.tree.configure(xscrollcommand=scrollbar_x.set)
        
        # Bind double-click to edit a cell or add a new row
        self.tree.bind("<Double-1>", self.on_cell_double_click)

    def create_control_frame(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        btn_add_row = ttk.Button(control_frame, text="Add Row", command=self.add_row)
        btn_add_row.grid(row=0, column=0, padx=5)
        
        btn_del_row = ttk.Button(control_frame, text="Delete Row", command=self.delete_row)
        btn_del_row.grid(row=0, column=1, padx=5)
        
        btn_add_column = ttk.Button(control_frame, text="Add Column", command=self.add_column)
        btn_add_column.grid(row=0, column=2, padx=5)
        
        btn_del_column = ttk.Button(control_frame, text="Delete Column", command=self.delete_column)
        btn_del_column.grid(row=0, column=3, padx=5)
        
        btn_set_formula = ttk.Button(control_frame, text="Set Formula", command=self.set_formula)
        btn_set_formula.grid(row=0, column=4, padx=5)
        
        btn_edit_cell = ttk.Button(control_frame, text="Edit Cell", command=self.edit_cell)
        btn_edit_cell.grid(row=0, column=5, padx=5)

    def create_graph_settings_frame(self):
        graph_frame = ttk.LabelFrame(self, text="Graph Settings")
        graph_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Label(graph_frame, text="X Column:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.x_var = tk.StringVar()
        self.x_dropdown = ttk.Combobox(graph_frame, textvariable=self.x_var, state="readonly")
        self.x_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(graph_frame, text="Y Column:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.y_var = tk.StringVar()
        self.y_dropdown = ttk.Combobox(graph_frame, textvariable=self.y_var, state="readonly")
        self.y_dropdown.grid(row=0, column=3, padx=5, pady=5)
        
        # Options for trendline, equation display and polar coordinates
        self.trendline_var = tk.BooleanVar(value=False)
        self.equation_var = tk.BooleanVar(value=False)
        self.polar_var = tk.BooleanVar(value=False)
        
        chk_trendline = ttk.Checkbutton(graph_frame, text="Trendline", variable=self.trendline_var)
        chk_trendline.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        chk_equation = ttk.Checkbutton(graph_frame, text="Show Equation", variable=self.equation_var)
        chk_equation.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        chk_polar = ttk.Checkbutton(graph_frame, text="Polar Coordinates", variable=self.polar_var)
        chk_polar.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        btn_graph = ttk.Button(graph_frame, text="Graph", command=self.graph_data)
        btn_graph.grid(row=1, column=3, padx=5, pady=5)

    def update_table_view(self):
        # Clear current tree and rebuild columns
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self.columns
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
            
        # Insert each row
        for i, row in enumerate(self.data):
            values = [row.get(col, "") for col in self.columns]
            self.tree.insert("", "end", iid=str(i), values=values)
        
        self.update_graph_options()

    def update_graph_options(self):
        # Update the dropdowns for graphing choices based on table columns
        self.x_dropdown["values"] = self.columns
        self.y_dropdown["values"] = self.columns
        if self.columns:
            if self.x_var.get() not in self.columns:
                self.x_var.set(self.columns[0])
            if self.y_var.get() not in self.columns:
                self.y_var.set(self.columns[0])

    def add_row(self):
        # Create an empty row (all columns empty) and update view
        new_row = {col: "" for col in self.columns}
        self.data.append(new_row)
        self.update_table_view()
        self.recalculate_results()  # Recalculeaza rezultatele

    def delete_row(self):
        # Delete the selected row
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Delete Row", "No row selected.")
            return
        index = int(selected[0])
        del self.data[index]
        self.update_table_view()
        self.recalculate_results()  # Recalculeaza rezultatele

    def add_column(self):
        col_name = simpledialog.askstring("Add Column", "Enter column name:")
        if col_name and col_name.strip():
            col_name = col_name.strip()
            if col_name in self.columns:
                messagebox.showerror("Error", "Column already exists.")
                return
            self.columns.append(col_name)
            for row in self.data:
                row[col_name] = ""
            self.update_table_view()
            self.update_graph_options()  # Actualizeaza optiunile pentru grafic
        else:
            messagebox.showwarning("Add Column", "Invalid column name.")

    def delete_column(self):
        if not self.columns:
            messagebox.showwarning("Delete Column", "No columns to delete.")
            return
        col_name = simpledialog.askstring("Delete Column", f"Enter column name to delete:\nOptions: {', '.join(self.columns)}")
        if col_name in self.columns:
            self.columns.remove(col_name)
            for row in self.data:
                if col_name in row:
                    del row[col_name]
            self.update_table_view()
            self.update_graph_options()  # Actualizeaza optiunile pentru grafic
        else:
            messagebox.showerror("Error", "Column not found.")

    def edit_cell(self):
        # Get selected cell via row selection and then ask for column
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Edit Cell", "No row selected.")
            return
        row_index = int(selected[0])
        # Ask user which column to edit (by name)
        col_name = simpledialog.askstring("Edit Cell", f"Enter column name to edit:\nOptions: {', '.join(self.columns)}")
        if col_name not in self.columns:
            messagebox.showerror("Error", "Column not found.")
            return
        current_value = self.data[row_index].get(col_name, "")
        new_value = simpledialog.askstring("Edit Cell", f"Editing cell at row {row_index+1}, column '{col_name}':", initialvalue=current_value)
        if new_value is not None:
            self.data[row_index][col_name] = new_value.strip()
            self.update_table_view()
            self.recalculate_results()  # Recalculeaza rezultatele

    def on_cell_double_click(self, event):
        """Gestioneaza dublu clic pe celule sau zona libera."""
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify_column(event.x)

        if item:  # Dublu clic pe o celulă existentă
            col_index = int(column.replace("#", "")) - 1
            if col_index >= 0 and col_index < len(self.columns):
                col_name = self.columns[col_index]
                row_index = int(item)
                current_value = self.data[row_index].get(col_name, "")
                new_value = simpledialog.askstring("Edit Cell", f"Editing cell at row {row_index+1}, column '{col_name}':", initialvalue=current_value)
                if new_value is not None:
                    self.data[row_index][col_name] = new_value.strip()
                    self.update_table_view()
                    self.recalculate_results()  # Recalculeaza rezultatele
        else:  # Dublu clic pe zona libera
            self.add_row()

    def set_formula(self):
        if len(self.columns) < 2:
            messagebox.showwarning("Setare formula", "Sunt necesare cel putin doua coloane pentru a aplica formula.")
            return

        # Alege prima coloana sursa
        source_column1 = simpledialog.askstring("Setare formula", f"Introduceti prima coloana sursa pentru formula:\nOptiuni: {', '.join(self.columns)}")
        if source_column1 not in self.columns:
            messagebox.showerror("Eroare", "Prima coloana sursa nu a fost gasita.")
            return

        # Alege a doua coloana sursa
        source_column2 = simpledialog.askstring("Setare formula", f"Introduceti a doua coloana sursa pentru formula:\nOptiuni: {', '.join(self.columns)}")
        if source_column2 not in self.columns:
            messagebox.showerror("Eroare", "A doua coloana sursa nu a fost gasita.")
            return

        # Alege coloana tinta
        target_column = simpledialog.askstring("Setare formula", f"Introduceti coloana tinta pentru formula:\nOptiuni: {', '.join(self.columns)}")
        if target_column not in self.columns:
            messagebox.showerror("Eroare", "Coloana tinta nu a fost gasita.")
            return

        # Alege o formula din baza de date sau introdu manual
        formula_choice = messagebox.askquestion("Alegere formula", "Doriti sa utilizati o formula predefinita?")
        if formula_choice == "yes":
            # Selecteaza o formula din baza de date
            formula_name = simpledialog.askstring("Selectare formula", f"Formule disponibile:\n{', '.join(FORMULAS_DB.keys())}")
            if formula_name not in FORMULAS_DB:
                messagebox.showerror("Eroare", "Formula nu a fost gasita.")
                return
            formula = FORMULAS_DB[formula_name]
        else:
            # Introdu manual formula
            formula = simpledialog.askstring("Setare formula", "Introduceti formula (folositi A si B ca variabile):")
            if formula is None or formula.strip() == "":
                return
            formula = formula.strip()

        # Salveaza configuratia formulei in dictionarul de formule
        self.column_formulas[target_column] = {
            "source_column1": source_column1,
            "source_column2": source_column2,
            "formula": formula
        }

        # Recalculeaza rezultatele initiale
        self.recalculate_results()

    def recalculate_results(self):
        for target_column, config in self.column_formulas.items():
            source_column1 = config["source_column1"]
            source_column2 = config["source_column2"]
            formula = config["formula"]

            for i, row in enumerate(self.data):
                try:
                    # Creeaza contextul pentru evaluare
                    context = {
                        "A": float(row.get(source_column1, 0) or 0),  # Înlocuiește valorile goale cu 0
                        "B": float(row.get(source_column2, 0) or 0)   # Înlocuiește valorile goale cu 0
                    }
                    result = eval(formula, {"__builtins__": {}, "np": np}, context)
                    # Rotunjeste rezultatul la doua zecimale
                    self.data[i][target_column] = round(result, 2)
                except Exception as e:
                    self.data[i][target_column] = f"Eroare: {e}"

        # Actualizeaza tabelul pentru a include formula
        self.update_table_view()

    def start_auto_update(self):
        """Actualizeaza rezultatele la fiecare 2 secunde, daca este activata."""
        if self.auto_update_enabled:
            self.recalculate_results()  # Recalculeaza rezultatele
        self.after(2000, self.start_auto_update)  # Reapeleaza functia dupa 2 secunde

    def disable_auto_update(self):
        """Dezactiveaza actualizarea automata."""
        self.auto_update_enabled = False

    def enable_auto_update(self):
        """Reactiveaza actualizarea automata."""
        self.auto_update_enabled = True

    def graph_data(self):
        """Genereaza graficul pe baza coloanelor selectate."""
        self.disable_auto_update()  # Dezactiveaza actualizarea automata
        
        # Get selected x and y column names
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        if x_col not in self.columns or y_col not in self.columns:
            messagebox.showerror("Graph Error", "Invalid column selection.")
            self.enable_auto_update()  # Reactiveaza actualizarea automata
            return
        
        # Collect data and convert to floats
        x_data = []
        y_data = []
        for row in self.data:
            try:
                x_val = float(row.get(x_col, 0))
                y_val = float(row.get(y_col, 0))
                x_data.append(x_val)
                y_data.append(y_val)
            except ValueError:
                continue  # skip rows with non-numeric data
        
        if not x_data or not y_data:
            messagebox.showwarning("Graph Warning", "Not enough numeric data to plot.")
            self.enable_auto_update()  # Reactiveaza actualizarea automata
            return

        # Create a new figure for the graph
        if self.polar_var.get():
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="polar")
            # For polar, assume x_data represents angles in degrees (convert to radians)
            theta = np.deg2rad(x_data)
            ax.plot(theta, y_data, 'bo', label="Data")
            title_str = f"Polar Plot of {y_col} vs {x_col}"
            ax.set_title(title_str)
            # Trendline typically does not apply to polar coordinates
            if self.trendline_var.get():
                messagebox.showinfo("Trendline Info", "Trendline is not available for polar plots.")
        else:
            fig, ax = plt.subplots()
            ax.plot(x_data, y_data, 'bo', label="Data")
            title_str = f"{y_col} vs {x_col}"
            ax.set_title(title_str)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            
            # If trendline is selected, compute linear regression
            if self.trendline_var.get():
                try:
                    coeffs = np.polyfit(x_data, y_data, 1)  # linear fit: slope and intercept
                    poly_eq = np.poly1d(coeffs)
                    # Create line using the min and max of x_data
                    x_line = np.linspace(min(x_data), max(x_data), 100)
                    y_line = poly_eq(x_line)
                    ax.plot(x_line, y_line, 'r-', label="Trendline")
                    # If equation display is selected, add text annotation
                    if self.equation_var.get():
                        eq_str = f"y = {coeffs[0]:.3f}x + {coeffs[1]:.3f}"
                        ax.text(0.05, 0.95, eq_str, transform=ax.transAxes, fontsize=10,
                                verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
                except Exception as e:
                    messagebox.showerror("Trendline Error", f"Could not compute trendline: {e}")
                    
        ax.legend()
        plt.show()
        
        self.enable_auto_update()  # Reactiveaza actualizarea automata

    def save_project(self):
        # Save the current project (table data and columns) as a JSON file.
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                project = {
                    "columns": self.columns,
                    "data": self.data,
                }
                with open(file_path, "w") as f:
                    json.dump(project, f, indent=4)
                messagebox.showinfo("Save Project", "Project saved successfully.")
            except Exception as e:
                messagebox.showerror("Save Error", f"An error occurred while saving: {e}")

    def open_project(self):
        # Open and load a saved project from a JSON file.
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    project = json.load(f)
                self.columns = project.get("columns", [])
                self.data = project.get("data", [])
                self.update_table_view()
                messagebox.showinfo("Open Project", "Project loaded successfully.")
            except Exception as e:
                messagebox.showerror("Open Error", f"An error occurred while opening the project: {e}")

    def new_project(self):
        # Reset the table data and columns.
        if messagebox.askyesno("New Project", "Are you sure you want to create a new project? Unsaved changes will be lost."):
            self.columns = ["Column1", "Column2"]
            self.data = []
            self.update_table_view()

if __name__ == "__main__":
    app = DataTableApp()
    app.mainloop()