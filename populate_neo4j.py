from neo4j import GraphDatabase

# ------------------- Config -------------------
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "Username"
NEO4J_PASSWORD = "Password"
DB_NAME = "student"  # explicitly use this database

driver = None

# ------------------- Initialize Neo4j -------------------
def init_neo4j():
    global driver
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    # quick test
    with driver.session(database=DB_NAME) as s:
        s.run("RETURN 1")

# ------------------- Clear and Populate DB -------------------
def clear_and_populate_db():
    with driver.session(database=DB_NAME) as session:
        # Delete everything
        session.run("MATCH (n) DETACH DELETE n")

        # 1️⃣ Faculty / Courses
        faculty_data = [
            ("23CSE101", "Computational Problem Solving", "Dr. Dhanya M Dhanalakshmy"),
            ("23ENG101", "Technical Communication", "Dr. Nandhini I"),
            ("23ENG101-LAB", "Lab Session Technical Communication", "Dr. Nandhini I"),
            ("23MAT107", "Calculus", "Dr. Selar E"),
            ("23MAT107-MATLAB", "Calculus MATLAB", "Dr. Selar E"),
            ("23EEE104", "Introduction to Electrical & Electronics Engineering", "Dr. K Ilango"),
            ("22ADM101", "Foundations of Indian Heritage", "Shreeram Kasturi"),
            ("22AVP103", "Mastery Over Mind", "Dr. Senthilkumar M"),
            ("23CSE102", "Computer Hardware Essentials", "Mr. Sriram S"),
            ("23CSE101-LAB", "LAB Computational Problem Solving", "Dr. Dhanya M Dhanalakshmy"),
            ("23CSE102-LAB", "Computer Hardware Essentials (Lab)", "Mr. Sriram S"),
            ("23EEE184-LAB", "Basic Electrical & Electronics Engineering Practice", "Dr. T Ananthan")
        ]

        # Create Teachers and Courses
        for code, name, faculty in faculty_data:
            session.run("""
                MERGE (t:Teacher {name:$faculty})
                MERGE (c:Course {code:$code})
                SET c.name = $name
                MERGE (t)-[:TEACHES]->(c)
            """, faculty=faculty, code=code, name=name)

        # Map course code -> teacher for session linking
        course_teacher = {code: faculty for code, name, faculty in faculty_data}

        # 2️⃣ Timetable / Class Sessions (Monday to Friday)
        timetable_data = [
            # Monday
            ("Monday", "Slot 2", "8:50 am - 9:40 am", "23CSE101", "F305", "CSE", "1st Semester", "Section F"),
            ("Monday", "Slot 3", "9:40 am - 10:30 am", "22ADM101", "F305", "CSE", "1st Semester", "Section F"),
            ("Monday", "Slot 4", "10:45 am - 11:35 am", "23MAT107", "F305", "CSE", "1st Semester", "Section F"),
            ("Monday", "Slot 5", "11:35 am - 12:25 pm", "23EEE104", "F305", "CSE", "1st Semester", "Section F"),
            ("Monday", "Slot 6", "12:25 pm - 1:15 pm", "22AVP103", "F305", "CSE", "1st Semester", "Section F"),
            ("Monday", "Slot 8", "2:05 pm - 3:45 pm", "23MAT107-MATLAB", "F305", "CSE", "1st Semester", "Section F"),
            ("Monday", "Slot 9", "3:45 pm - 4:35 pm", "23MAT107-MATLAB", "F305", "CSE", "1st Semester", "Section F"),
            # Tuesday
            ("Tuesday", "Slot 4", "10:45 am - 11:35 am", "23EEE104", "F305", "CSE", "1st Semester", "Section F"),
            ("Tuesday", "Slot 5", "11:35 am - 12:25 pm", "23EEE104", "F305", "CSE", "1st Semester", "Section F"),
            ("Tuesday", "Slot 8", "2:05 pm - 2:55 pm", "23ENG101-LAB", "AB1 Language Lab", "CSE", "1st Semester", "Section F"),
            # Wednesday
            ("Wednesday", "Slot 3", "9:40 am - 10:30 am", "22ADM101", "F305", "CSE", "1st Semester", "Section F"),
            ("Wednesday", "Slot 4", "10:45 am - 11:35 am", "23EEE104", "F305", "CSE", "1st Semester", "Section F"),
            ("Wednesday", "Slot 5", "12:25 pm - 1:15 pm", "23CSE102", "F305", "CSE", "1st Semester", "Section F"),
            ("Wednesday", "Slot 8", "2:05 pm - 2:55 pm", "23ENG101", "F305", "CSE", "1st Semester", "Section F"),
            ("Wednesday", "Slot 9", "2:55 pm - 3:45 pm", "23ENG101", "F305", "CSE", "1st Semester", "Section F"),
            # Thursday
            ("Thursday", "Slot 3", "9:40 am - 10:30 am", "23CSE101", "F305", "CSE", "1st Semester", "Section F"),
            ("Thursday", "Slot 4", "10:45 am - 11:35 am", "22AVP103", "F305", "CSE", "1st Semester", "Section F"),
            ("Thursday", "Slot 5", "11:35 am - 12:25 pm", "23EEE104", "F305", "CSE", "1st Semester", "Section F"),
            ("Thursday", "Slot 6", "12:25 pm - 1:15 pm", "23MAT107", "F305", "CSE", "1st Semester", "Section F"),
            ("Thursday", "Slot 8", "2:55 pm - 3:45 pm", "23CSE101-LAB", "CS Lab1", "CSE", "1st Semester", "Section F"),
            ("Thursday", "Slot 9", "3:45 pm - 4:35 pm", "23CSE101-LAB", "CS Lab1", "CSE", "1st Semester", "Section F"),
            # Friday
            ("Friday", "Slot 3", "9:40 am - 10:30 am", "23CSE101", "F305", "CSE", "1st Semester", "Section F"),
            ("Friday", "Slot 4", "10:45 am - 11:35 am", "23ENG101", "F305", "CSE", "1st Semester", "Section F"),
            ("Friday", "Slot 5", "11:35 am - 12:25 pm", "23ENG101", "F305", "CSE", "1st Semester", "Section F"),
            ("Friday", "Slot 6", "12:25 pm - 1:15 pm", "23MAT107", "F305", "CSE", "1st Semester", "Section F"),
            ("Friday", "Slot 7", "2:05 pm - 2:55 pm", "23CSE102-LAB", "Hardware Lab", "CSE", "1st Semester", "Section F"),
            ("Friday", "Slot 8", "2:55 pm - 3:45 pm", "23CSE102-LAB", "Hardware Lab", "CSE", "1st Semester", "Section F"),
        ]

        # Insert sessions and link to course + teacher
        for day, slot, time_range, code, room, branch, semester, section in timetable_data:
            teacher = course_teacher.get(code)
            session.run("""
                MERGE (c:Course {code:$code})
                CREATE (s:ClassSession {
                    day:$day, slot:$slot, time_range:$time_range, room:$room,
                    branch:$branch, semester:$semester, section:$section
                })
                MERGE (c)-[:HAS_SESSION]->(s)
                WITH s
                MATCH (t:Teacher {name:$teacher})
                MERGE (t)-[:CONDUCTS]->(s)
            """, day=day, slot=slot, time_range=time_range, code=code,
                 room=room, branch=branch, semester=semester, section=section,
                 teacher=teacher)

        # 3️⃣ Sample Tests
        test_data = [
            ("Dr. Selar E", "Calculus", "2024-11-21", "Slot 4 (2:05 Pm - 2:55 PM) - F305"),
            ("Dr. Dhanya M Dhanalakshmy", "Computational Problem Solving", "2024-11-22", "Slot 3 (9:40 am - 10:30 am) - F305")
        ]

        for teacher, subject, date, period in test_data:
            session.run("""
                MERGE (t:Teacher {name:$teacher})
                CREATE (test:Test {subject:$subject, date:$date, period:$period})
                MERGE (t)-[:SCHEDULES_TEST]->(test)
            """, teacher=teacher, subject=subject, date=date, period=period)


# ------------------- Main -------------------
if __name__ == "__main__":
    try:
        init_neo4j()
        clear_and_populate_db()
        print("DB populated successfully in 'student' database.")
    except Exception as e:
        print("Error:", e)
    finally:
        if driver:
            driver.close()
