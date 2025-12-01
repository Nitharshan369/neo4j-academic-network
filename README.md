# Neo4j Student Management System

## Overview

  This project implements a Student Management System using Neo4j, a graph database, to efficiently manage student data and relationships. It allows easy querying, updating, and visualization of student             information. The system is designed to be scalable, flexible, and easy to integrate with other applications.

## Architecture

    The system follows a client-server model:

* **Client (Python Application)**: Interacts with the user and sends queries to Neo4j.
* **Neo4j Graph Database**: Stores all student records and relationships as nodes and edges.
* **CSV Data Import**: Initial data is imported via CSV files.
* **Modules & Scripts**: Separate Python scripts handle different functionalities for maintainability.

**Workflow:**

    1. The Python application connects to the Neo4j database. <br>
    2. CSV files are loaded to populate nodes and relationships.<br>
    3. Users can perform CRUD operations and queries on student data.<br>
    4. Archived code is preserved for future reference or extension.<br>

## Features

* Add, update, and delete student records.
* Query student data based on various attributes like semester, section, or department.
* Manage relationships between students, courses, and instructors.
* Import and export data using CSV files.
* View graph representations of student connections.
* Maintain modular and maintainable code structure.

## Benefits

* Efficient storage and retrieval of complex relationships.
* Easy to scale as student data grows.
* Quick insights through graph-based queries.
* Easy integration with other Python or web applications.

## Technologies Used

* Neo4j: Graph database for managing student data.
* Python: Programming language for application logic.
* CSV: Format for importing and storing data.

## Setup & Installation

    1. Clone the repository:

```bash
git clone https://github.com/Nitharshan369/neo4j-academic-network.git
cd Neo4j
```

    2. Install dependencies:

```bash
pip install -r requirements.txt
```

    3. Configure the Neo4j connection in `app.py`:

```python
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "your_password"
driver = GraphDatabase.driver(uri, auth=(username, password))
```

    4. Populate the database:

```bash
python populate_neo4j.py
```

    5. Run the application:

```bash
python app.py
```

## Project Parts and Contributions

----------------------------------------------------------------------------------------------------------------------------------------------
| Part                             | Description                                                       | Contributors                         |
| -------------------------------- | ----------------------------------------------------------------- | ------------------------------------ |
| Database Connection & Setup      | Establishing Neo4j connection, configuration, and initial setup   | SharveshC, Prawin443               |
| Data Population                  | Scripts to populate the Neo4j database from CSV files             | SharveshC, Nitharshan369           |
| CRUD Operations                  | Add, update, delete, and query operations on student nodes        | SharveshC, Prasanna-Balakrishnan   |
| Archive & Legacy Code Management | Organizing archived code and Neo4j scripts for reference          | Nitharshan369, Prawin443                |
| CSV Handling & Utilities         | Managing CSV files, parsing, and utilities for smooth data import | Nitharshan369, Prasanna-Balakrishnan |
----------------------------------------------------------------------------------------------------------------------------------------------
 
## Project Structure

```
├── app.py
├── populate_neo4j.py
├── archive/
│   ├── code/       # Legacy or other project code
│   └── neo4j/      # Neo4j-related scripts or backups
├── csv/            # CSV files used for populating the database
├── README.md
└── .gitignore
```

* **app.py**: Main application logic for interacting with Neo4j.
* **populate_neo4j.py**: Script to populate the Neo4j database with initial data.
* **archive/code**: Legacy or other project code.
* **archive/neo4j**: Neo4j scripts or backups.
* **csv/**: Stores CSV files for importing student data.


## Contributors
- **[Nitharshan369](https://github.com/Nitharshan369)**
- **[SharveshC](https://github.com/SharveshC)**
- **[Prawin443](https://github.com/Prawin443)**
- **[Prasanna-Balakrishnan](https://github.com/Prasanna-Balakrishnan)**

