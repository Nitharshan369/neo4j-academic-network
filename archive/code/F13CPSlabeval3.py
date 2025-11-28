import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import pandas as pd
from datetime import datetime
from neo4j import GraphDatabase

# ---------------- Neo4j Configuration ----------------
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jneo"

# Global driver
driver = None

# ---------------- Neo4j Initialization ----------------
def init_neo4j():
    global driver
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Test connection
        with driver.session() as session:
            session.run("RETURN 1")
        print("Neo4j connected successfully.")
        return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to connect to Neo4j: {e}\nEnsure Neo4j is running on {NEO4J_URI}.")
        return False

# ---------------- Clear & Populate DB ----------------
def clear_and_populate_db():
    if not driver:
        return False
    
    with driver.session() as session:
        # Clear all nodes/relationships
        session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing Neo4j database.")
        
        # ---- Faculty / Courses ----
        faculty_data = [
            ("23CSE101", "Computational Problem Solving", "Dr. Dhanya M Dhanalakshmy"),
            ("23ENG101", "Technical Communication", "Dr. Nandhini I"),
            ("23ENG101", "Lab Session Technical Communication", "Dr. Nandhini I"),
            ("23MAT107", "Calculus", "Dr. Selar E"),
            ("23MAT107", "Calculus MATLAB", "Dr. Selar E"),
            ("23EEE104", "Introduction to Electrical & Electronics Engineering", "Dr. K Ilango"),
            ("22ADM101", "Foundations of Indian Heritage", "Shreeram Kasturi"),
            ("22AVP103", "Mastery Over Mind", "Dr. Senthilkumar M"),
            ("23CSE102", "Computer Hardware Essentials", "Mr. Sriram S"),
            ("23CSE101 (Lab)", "LAB Computational Problem Solving", "Dr. Dhanya M Dhanalakshmy"),
            ("23CSE102 (Lab)", "Computer Hardware Essentials", "Mr. Sriram S"),
            ("23EEE184 (Lab)", "Basic Electrical & Electronics Engineering Practice", "Dr. T Ananthan")
        ]
        for code, name, faculty in faculty_data:
            session.run("""
                MERGE (t:Teacher {name: $faculty})
                MERGE (c:Course {code: $code, name: $name})
                MERGE (t)-[:TEACHES]->(c)
            """, faculty=faculty, code=code, name=name)
        
        # ---- Timetable / ClassSessions ----
        timetable_data = [
            # Only a few entries here for brevity
            ("Monday", "Slot 2", "8:50 am - 9:40 am", "23CSE101", "Computational Problem Solving", "F305", "CSE", "1st Semester", "Section F"),
            ("Monday", "Slot 3", "9:40 am - 10:30 am", "22ADM101", "Foundations of Indian Heritage", "F305", "CSE", "1st Semester", "Section F")
        ]
        for day, slot, time_range, code, name, room, branch, semester, section in timetable_data:
            session.run("""
                MERGE (c:Course {code: $code, name: $name})
                CREATE (s:ClassSession {day: $day, slot: $slot, time_range: $time_range, room: $room, branch: $branch, semester: $semester, section: $section})
                MERGE (c)-[:HAS_SESSION]->(s)
            """, day=day, slot=slot, time_range=time_range, code=code, name=name, room=room, branch=branch, semester=semester, section=section)
        
        # ---- Test Schedules ----
        test_data = [
            ("Dr. Selar E", "Calculus", "2024-11-21", "Slot 4 ( 2:05 Pm - 2:55 PM) - F305"),
            ("Dr. Dhanya M Dhanalakshmy", "Computational Problem Solving", "2024-11-22", "Slot 3 ( 9:40 am - 10:30 am) - F305")
        ]
        for teacher, subject, date, period in test_data:
            session.run("""
                MERGE (t:Teacher {name: $teacher})
                CREATE (test:Test {subject: $subject, date: $date, period: $period})
                MERGE (t)-[:SCHEDULES_TEST]->(test)
            """, teacher=teacher, subject=subject, date=date, period=period)
        
        print("Database populated successfully.")
    return True

# ---------------- Utility Functions ----------------
def get_teacher_names():
    if not driver:
        return []
    with driver.session() as session:
        result = session.run("MATCH (t:Teacher) RETURN DISTINCT t.name as name ORDER BY t.name")
        return [record["name"] for record in result]

def get_teacher_courses(teacher_name):
    if not driver:
        return []
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Teacher {name: $name})-[:TEACHES]->(c:Course)
            RETURN DISTINCT c.name as course ORDER BY c.name
        """, name=teacher_name)
        return [record["course"] for record in result]

def get_available_periods(teacher_name, subject, selected_date):
    if not driver:
        return None
    select_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    today_date = datetime.now().date()
    if select_date <= today_date:
        return "INVALID_DATE"
    selected_day = pd.Timestamp(selected_date).day_name()
    with driver.session() as session:
        result = session.run("""
            MATCH (test:Test {date: $date, subject: $subject})
            RETURN test.period as period
        """, date=selected_date, subject=subject)
        existing = result.single()
        if existing:
            return "CONFLICT"
        result = session.run("""
            MATCH (c:Course {name: $subject})-[:HAS_SESSION]->(s:ClassSession {day: $day})
            RETURN s.slot + ' (' + s.time_range + ') - ' + s.room as period
            ORDER BY s.slot
        """, subject=subject, day=selected_day)
        periods = [record["period"] for record in result]
        if not periods:
            return "NO_PERIODS"
        return periods

def schedule_test(teacher_name, subject, date, period):
    if not driver:
        return False
    with driver.session() as session:
        session.run("""
            MERGE (t:Teacher {name: $teacher})
            CREATE (test:Test {subject: $subject, date: $date, period: $period})
            MERGE (t)-[:SCHEDULES_TEST]->(test)
        """, teacher=teacher_name, subject=subject, date=date, period=period)
    return True

def load_tests():
    if not driver:
        return []
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Teacher)-[:SCHEDULES_TEST]->(test:Test)
            RETURN t.name as teacher, test.subject as subject, test.date as date, test.period as period
            ORDER BY test.date
        """)
        return [dict(record) for record in result]

# ---------------- GUI Program ----------------
def program1():
    if not init_neo4j():
        return

    # Populate DB if empty
    with driver.session() as session:
        count = session.run("MATCH (n) RETURN count(n) AS cnt").single()["cnt"]
        if count == 0:
            clear_and_populate_db()

    root = tk.Tk()
    root.title("Teachers Management System")
    root.geometry("1000x600")
    tk.Label(root, text="Teachers Test Assignment Portal", font=("Arial", 16, "bold")).pack(pady=10)

    # Teacher selection
    teacher_name_var = tk.StringVar()
    tk.Label(root, text="Select Teacher:", font=("Arial", 12)).pack(pady=5)
    teacher_combo = ttk.Combobox(root, textvariable=teacher_name_var, values=get_teacher_names(), state="readonly", font=("Arial", 12))
    teacher_combo.set("Select Teacher")
    teacher_combo.pack(pady=5)

    # Subject selection
    subject_var = tk.StringVar()
    tk.Label(root, text="Select Subject:", font=("Arial", 12)).pack(pady=5)
    subject_combo = ttk.Combobox(root, textvariable=subject_var, state="readonly", font=("Arial", 12))
    subject_combo.set("Select Subject")
    subject_combo.pack(pady=5)

    # Date selection
    tk.Label(root, text="Select Date:", font=("Arial", 12)).pack(pady=5)
    cal = Calendar(root, selectmode="day", date_pattern="yyyy-mm-dd")
    cal.pack(pady=5)

    root.mainloop()

# ---------------- Run ----------------
if __name__ == "__main__":
    program1()
