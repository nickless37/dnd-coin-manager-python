import tkinter as tk
from tkinter import messagebox
import json
import os
from tkinter import ttk

# ======================
# MODEL
# ======================
class Item:
    def __init__(self, name, copper=0, silver=0, gold=0, platinum=0):
        self.name = name
        self.values = {
            "copper": copper,
            "silver": silver,
            "gold": gold,
            "platinum": platinum
        }

    def add(self, key, amount):
        self.values[key] += amount


class DataManager:
    def __init__(self, filename="data.json"):
        self.filename = filename
        self.items = {}

    def add_item(self, item):
        self.items[item.name] = item
        self.save()

    def save(self):
        data = {
            "objects": {
                name: item.values
                for name, item in self.items.items()
            }
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.filename):
            return

        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.items.clear()
        for name, values in data.get("objects", {}).items():
            self.items[name] = Item(name, **values)


current_character = None


# ======================
# WINDOW
# ======================
manager = DataManager()
manager.load()

root = tk.Tk()
root.title("Coin Manager")
root.geometry("400x250")

# ======================
# LISTBOX
# ======================
tk.Label(root, text="Characters").grid(row=0, column=0)

listbox = tk.Listbox(root, height=8, width=18)
listbox.grid(row=1, column=0, rowspan=6, padx=10)

def refresh_list():
    listbox.delete(0, tk.END)
    for name in manager.items:
        listbox.insert(tk.END, name)

refresh_list()
#
# ======================
# VALUE DISPLAY
# ======================
labels = {}

def update_display():
    if not current_character:
        return

    item = manager.items[current_character]

    for key in item.values:
        labels[key]["text"] = str(item.values[key])


row = 1
for key in ("copper", "silver", "gold", "platinum"):
    tk.Label(root, text=key).grid(row=row, column=1, sticky="e")
    labels[key] = tk.Label(root, text="0", width=6)
    labels[key].grid(row=row, column=2, sticky="w")
    row += 1

listbox.bind("<<ListboxSelect>>", lambda e: update_display())

# ======================
# CONTROLS
# ======================
tk.Label(root, text="Coin").grid(row=5, column=1)

prop_var = tk.StringVar()
prop_combo = ttk.Combobox(
    root,
    textvariable=prop_var,
    values=["copper", "silver", "gold", "platinum"],
    state="readonly",
    width=12
)
prop_combo.grid(row=6, column=1)
prop_combo.current(0)

tk.Label(root, text="Amount").grid(row=5, column=2)
value_entry = tk.Entry(root, width=6)
value_entry.grid(row=6, column=2)

def add_object():
    name = name_entry.get()
    if not name:
        return
    if name in manager.items:
        messagebox.showerror("Error", "Character exists")
        return

    manager.add_item(Item(name))
    refresh_list()
    name_entry.delete(0, tk.END)

def delete_object():
    selection = listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Select character")
        return

    name = listbox.get(selection[0])

    if not messagebox.askyesno(
        "Confirm",
        f"Delete '{name}'?"
    ):
        return

    del manager.items[name]
    manager.save()
    refresh_list()

    for lbl in labels.values():
        lbl["text"] = "0"

def change_value(sign=1):
    selection = listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Select character")
        return

    name = listbox.get(selection[0])
    prop = prop_var.get()

    try:
        value = int(value_entry.get())
    except ValueError:
        return

    if prop not in manager.items[name].values:
        messagebox.showerror("Error", "Invalid property")
        return

    manager.items[name].add(prop, value * sign)
    manager.save()
    update_display()


    def on_select(event):
        global current_character
        selection = listbox.curselection()
        if not selection:
            return

        current_character = listbox.get(selection[0])
        update_display()

    listbox.bind("<<ListboxSelect>>", on_select)


# ======================
# ADD CHARACTER
# ======================
tk.Label(root, text="New character").grid(row=7, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=8, column=0)

tk.Button(root, text="Add", command=add_object).grid(row=9, column=0, sticky="w", padx=5, pady=5)

# ======================
# BUTTONS
# ======================
tk.Button(root, text="+", width=4, command=lambda: change_value(1)).grid(row=7, column=1, pady=5)
tk.Button(root, text="-", width=4, command=lambda: change_value(-1)).grid(row=7, column=2)

tk.Button(root, text="Delete", command=delete_object).grid(
    row=9, column=0
)

root.mainloop()