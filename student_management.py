
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Connect to the database (created automatically)
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    course TEXT NOT NULL,
    phone TEXT
)
""")
conn.commit()


class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Record Management System")
        self.root.geometry("900x600")
        self.root.minsize(750, 500)

        title = tk.Label(
            root,
            text="Student Record Management System",
            font=("Arial", 20, "bold"),
            bg="#24476b",
            fg="white",
            pady=15
        )
        title.pack(fill="x")

        form = tk.LabelFrame(
            root, text="Student Details",
            font=("Arial", 11, "bold"), padx=10, pady=10
        )
        form.pack(fill="x", padx=15, pady=10)

        self.entries = {}
        fields = ["ID", "Name", "Age", "Course", "Phone"]

        for i, field in enumerate(fields):
            tk.Label(form, text=field + ":").grid(
                row=i // 3 * 2, column=(i % 3) * 2,
                padx=5, pady=5, sticky="w"
            )

            entry = tk.Entry(form, width=23)
            entry.grid(
                row=i // 3 * 2, column=(i % 3) * 2 + 1,
                padx=5, pady=5
            )
            self.entries[field] = entry

        self.entries["ID"].config(state="readonly")

        buttons = tk.Frame(root)
        buttons.pack(pady=5)

        tk.Button(
            buttons, text="Add Student",
            command=self.add_student, bg="#27864a",
            fg="white", width=13
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            buttons, text="Update",
            command=self.update_student, width=12
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            buttons, text="Delete",
            command=self.delete_student, bg="#c0392b",
            fg="white", width=12
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            buttons, text="Clear",
            command=self.clear_fields, width=12
        ).grid(row=0, column=3, padx=5)

        search_frame = tk.Frame(root)
        search_frame.pack(fill="x", padx=15, pady=8)

        tk.Label(search_frame, text="Search:").pack(side="left")

        self.search_entry = tk.Entry(search_frame, width=35)
        self.search_entry.pack(side="left", padx=8)

        tk.Button(
            search_frame, text="Search",
            command=self.search_student
        ).pack(side="left", padx=3)

        tk.Button(
            search_frame, text="Show All",
            command=self.load_students
        ).pack(side="left", padx=3)

        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("ID", "Name", "Age", "Course", "Phone")

        self.table = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", selectmode="browse"
        )

        widths = [55, 200, 60, 180, 150]
        for col, width in zip(columns, widths):
            self.table.heading(col, text=col)
            self.table.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.table.bind("<<TreeviewSelect>>", self.select_student)

        self.load_students()

    def get_values(self):
        name = self.entries["Name"].get().strip()
        age_text = self.entries["Age"].get().strip()
        course = self.entries["Course"].get().strip()
        phone = self.entries["Phone"].get().strip()

        if not name or not age_text or not course:
            messagebox.showwarning(
                "Validation", "Name, age, and course are required."
            )
            return None

        try:
            age = int(age_text)
            if age <= 0 or age > 120:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Age", "Enter a valid age between 1 and 120."
            )
            return None

        return name, age, course, phone

    def add_student(self):
        values = self.get_values()
        if values is None:
            return

        try:
            cursor.execute(
                "INSERT INTO students (name, age, course, phone) "
                "VALUES (?, ?, ?, ?)", values
            )
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_fields()
            self.load_students()
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))

    def load_students(self):
        self.table.delete(*self.table.get_children())
        try:
            cursor.execute(
                "SELECT id, name, age, course, phone "
                "FROM students ORDER BY id DESC"
            )
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))

    def search_student(self):
        keyword = self.search_entry.get().strip()
        self.table.delete(*self.table.get_children())

        try:
            pattern = "%" + keyword + "%"
            cursor.execute("""
                SELECT id, name, age, course, phone
                FROM students
                WHERE CAST(id AS TEXT) LIKE ?
                   OR name LIKE ?
                   OR course LIKE ?
                ORDER BY id DESC
            """, (pattern, pattern, pattern))

            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))

    def select_student(self, event=None):
        selected = self.table.selection()
        if not selected:
            return

        values = self.table.item(selected[0], "values")
        for field, value in zip(
            ["ID", "Name", "Age", "Course", "Phone"], values
        ):
            entry = self.entries[field]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, value)

            if field == "ID":
                entry.config(state="readonly")

    def update_student(self):
        student_id = self.entries["ID"].get()
        if not student_id:
            messagebox.showwarning(
                "Select Student", "Select a student from the table first."
            )
            return

        values = self.get_values()
        if values is None:
            return

        try:
            cursor.execute("""
                UPDATE students
                SET name = ?, age = ?, course = ?, phone = ?
                WHERE id = ?
            """, (*values, int(student_id)))
            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showwarning(
                    "Not Found", "Student record no longer exists."
                )
                self.load_students()
                return

            messagebox.showinfo("Success", "Student updated successfully.")
            self.clear_fields()
            self.load_students()
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))

    def delete_student(self):
        student_id = self.entries["ID"].get()

        if not student_id:
            messagebox.showwarning(
                "Select Student", "Select a student from the table first."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student?"
        )

        if confirm:
            try:
                cursor.execute(
                    "DELETE FROM students WHERE id = ?",
                    (int(student_id),)
                )
                conn.commit()
                self.clear_fields()
                self.load_students()
                messagebox.showinfo("Success", "Student deleted.")
            except sqlite3.Error as error:
                messagebox.showerror("Database Error", str(error))

    def clear_fields(self):
        for field, entry in self.entries.items():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            if field == "ID":
                entry.config(state="readonly")

        self.table.selection_remove(self.table.selection())


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)

    def close_app():
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()
