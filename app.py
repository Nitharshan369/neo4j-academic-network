# app.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import pandas as pd
from datetime import datetime
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jneo"
DB_NAME = "student"  # Specify the database explicitly

driver = None

def init_neo4j():
    global driver
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session(database=DB_NAME) as s:
        s.run("RETURN 1")

def get_teacher_names():
    with driver.session(database=DB_NAME) as session:
        result = session.run("MATCH (t:Teacher) RETURN DISTINCT t.name as name ORDER BY t.name")
        return [r["name"] for r in result]

def get_teacher_courses(teacher_name):
    with driver.session(database=DB_NAME) as session:
        result = session.run("""
            MATCH (t:Teacher {name:$name})-[:TEACHES]->(c:Course)
            RETURN DISTINCT c.name as course ORDER BY c.name
        """, name=teacher_name)
        return [r["course"] for r in result]

def get_available_periods(subject, selected_date):
    try:
        select_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except Exception:
        return "INVALID_DATE"
    if select_date <= datetime.now().date():
        return "INVALID_DATE"
    selected_day = pd.Timestamp(selected_date).day_name()
    with driver.session(database=DB_NAME) as session:
        existing = session.run("""
            MATCH (test:Test {date:$date, subject:$subject})
            RETURN test LIMIT 1
        """, date=selected_date, subject=subject).single()
        if existing:
            return "CONFLICT"
        result = session.run("""
            MATCH (c:Course {name:$subject})-[:HAS_SESSION]->(s:ClassSession {day:$day})
            RETURN s.slot + ' (' + s.time_range + ') - ' + s.room as period
            ORDER BY s.slot
        """, subject=subject, day=selected_day)
        periods = [r["period"] for r in result]
        return periods if periods else "NO_PERIODS"

def schedule_test(teacher, subject, date, period):
    with driver.session(database=DB_NAME) as session:
        session.run("""
            MERGE (t:Teacher {name:$teacher})
            CREATE (test:Test {subject:$subject, date:$date, period:$period})
            MERGE (t)-[:SCHEDULES_TEST]->(test)
        """, teacher=teacher, subject=subject, date=date, period=period)

def load_tests():
    with driver.session(database=DB_NAME) as session:
        result = session.run("""
            MATCH (t:Teacher)-[:SCHEDULES_TEST]->(test:Test)
            RETURN t.name as teacher, test.subject as subject, test.date as date, test.period as period
            ORDER BY test.date
        """)
        return [dict(r) for r in result]

# ------------------- GUI -------------------
def main():
    init_neo4j()
    root = tk.Tk()
    root.title("Teachers Test Assignment Portal")
    root.geometry("800x600")

    # Teacher selection
    tk.Label(root, text="Select Teacher:", font=("Arial", 12)).pack(pady=6)
    teacher_var = tk.StringVar()
    teacher_cb = ttk.Combobox(root, textvariable=teacher_var, state="readonly",
                              values=get_teacher_names(), width=60)
    teacher_cb.set("Select Teacher")
    teacher_cb.pack()

    # Subject selection
    tk.Label(root, text="Select Subject:", font=("Arial", 12)).pack(pady=6)
    subject_var = tk.StringVar()
    subject_cb = ttk.Combobox(root, textvariable=subject_var, state="readonly", values=[], width=60)
    subject_cb.set("Select Subject")
    subject_cb.pack()

    # Calendar
    tk.Label(root, text="Select Date:", font=("Arial", 12)).pack(pady=6)
    cal = Calendar(root, selectmode="day", date_pattern="yyyy-mm-dd")
    cal.pack()

    # Periods
    tk.Label(root, text="Available Periods:", font=("Arial", 12)).pack(pady=6)
    periods_lb = tk.Listbox(root, height=6, width=80, exportselection=False)
    periods_lb.pack()

    # ------------------- Callbacks -------------------
    def on_teacher_change(event=None):
        t = teacher_var.get()
        if t and t != "Select Teacher":
            subject_cb['values'] = get_teacher_courses(t)
            subject_cb.set("Select Subject")
            periods_lb.delete(0, tk.END)

    def find_periods():
        subject = subject_var.get()
        date = cal.get_date()
        if subject in ("", "Select Subject"):
            messagebox.showwarning("Select subject", "Choose a subject first.")
            return
        periods = get_available_periods(subject, date)
        periods_lb.delete(0, tk.END)
        if periods == "INVALID_DATE":
            messagebox.showwarning("Invalid date", "Choose a future date.")
            return
        if periods == "CONFLICT":
            messagebox.showerror("Conflict", "A test for this subject is already scheduled on that date.")
            return
        if periods == "NO_PERIODS":
            messagebox.showinfo("No periods", "No class sessions for this subject on that weekday.")
            return
        for p in periods:
            periods_lb.insert(tk.END, p)

    def do_schedule():
        sel = periods_lb.curselection()
        if not sel:
            messagebox.showwarning("Select period", "Choose a period from the list.")
            return
        period = periods_lb.get(sel[0])
        teacher = teacher_var.get()
        subject = subject_var.get()
        date = cal.get_date()
        schedule_test(teacher, subject, date, period)
        messagebox.showinfo("Scheduled", f"Test scheduled for {subject} on {date} ({period})")
        refresh_tests()

    def refresh_tests():
        tests = load_tests()
        top = tk.Toplevel(root)
        top.title("Scheduled Tests")
        cols = ("teacher", "subject", "date", "period")
        tree = ttk.Treeview(top, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c.title())
            tree.column(c, width=150)
        for t in tests:
            tree.insert('', tk.END, values=(t['teacher'], t['subject'], t['date'], t['period']))
        tree.pack(fill='both', expand=True)

    # ------------------- Bindings -------------------
    teacher_cb.bind("<<ComboboxSelected>>", on_teacher_change)
    tk.Button(root, text="Find Periods", command=find_periods).pack(pady=6)
    tk.Button(root, text="Schedule Selected Period", command=do_schedule).pack(pady=6)
    tk.Button(root, text="View Scheduled Tests", command=refresh_tests).pack(pady=6)

    root.protocol("WM_DELETE_WINDOW", lambda: (driver.close(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()
