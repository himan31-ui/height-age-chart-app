import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Database Setup ---
conn = sqlite3.connect("userdata.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        address TEXT,
        height REAL
    )
""")
conn.commit()

# --- Main Window ---
root = tk.Tk()
root.title("Form with SQLite and Chart")

# --- Entry Fields ---
tk.Label(root, text="Name").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Age").grid(row=1, column=0)
age_entry = tk.Entry(root)
age_entry.grid(row=1, column=1)

tk.Label(root, text="Address").grid(row=2, column=0)
address_entry = tk.Entry(root)
address_entry.grid(row=2, column=1)

tk.Label(root, text="Height").grid(row=3, column=0)
height_entry = tk.Entry(root)
height_entry.grid(row=3, column=1)

# --- Treeview Table ---
tree = ttk.Treeview(root, columns=("ID", "Name", "Age", "Address", "Height"), show="headings")
for col in ("ID", "Name", "Age", "Address", "Height"):
    tree.heading(col, text=col)
tree.grid(row=5, column=0, columnspan=2, pady=10)

# --- Graph Frame ---
graph_frame = tk.Frame(root)
graph_frame.grid(row=0, column=2, rowspan=6, padx=20)

fig = Figure(figsize=(5, 4), dpi=100)
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.draw()
canvas.get_tk_widget().pack()

# --- Graph Update Function ---
def update_graph():
    cursor.execute("SELECT age, height FROM users")
    data = cursor.fetchall()
    ages = [row[0] for row in data]
    heights = [row[1] for row in data]

    ax1.clear()
    ax2.clear()

    ax1.bar(range(len(ages)), ages, color='green')
    ax1.set_title("Age Chart")
    ax1.set_xlabel("Entry #")
    ax1.set_ylabel("Age")

    ax2.bar(range(len(heights)), heights, color='blue')
    ax2.set_title("Height Chart")
    ax2.set_xlabel("Entry #")
    ax2.set_ylabel("Height")

    canvas.draw()

# --- Save Data ---
def save_data():
    name = name_entry.get()
    age = age_entry.get()
    address = address_entry.get()
    height = height_entry.get()

    if not name or not age or not address or not height:
        messagebox.showerror("Error", "Please fill all fields")
        return

    cursor.execute("INSERT INTO users (name, age, address, height) VALUES (?, ?, ?, ?)",
                   (name, int(age), address, float(height)))
    conn.commit()
    load_data()
    update_graph()
    clear_fields()

# --- Load Data into Table ---
def load_data():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

# --- Clear Fields ---
def clear_fields():
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)

# --- Delete Selected ---
def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "No row selected")
        return
    item = tree.item(selected[0])
    user_id = item['values'][0]
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    load_data()
    update_graph()

# --- Buttons ---
tk.Button(root, text="Save Data", command=save_data).grid(row=4, column=0, pady=5)
tk.Button(root, text="Clear All Data", command=clear_fields).grid(row=4, column=1, pady=5)
tk.Button(root, text="Delete Selected", command=delete_selected).grid(row=6, column=0, columnspan=2)

# --- Initial Load ---
load_data()
update_graph()

root.mainloop()
