# Flight Management System

A Python command-line application for managing airline flights, pilots, destinations, and pilot assignments using SQLite.

## 1. Project Overview

The Flight Management System is designed to help airline staff manage flight schedules and related information through a simple, menu-driven interface.

The application demonstrates database creation, CRUD operations (Create, Read, Update, Delete), SQL queries, joins, filtering, and aggregate functions.

It uses Python's built-in `sqlite3` library, so no external database server or third-party Python packages are required.

## 2. Technologies Used

- **Python 3** – Application logic and command-line interface.
- **SQLite** – Relational database for storing airline information.
- **SQL** – Database creation, retrieval, modification, deletion, and reporting.
- **GitHub Codespaces** – Development and testing environment.

## 3. Features

### Flight Management

- Add new flights.
- View all flights in a formatted table.
- Search for a flight by flight number.
- Filter flights by destination airport code, status, and departure date.
- Update departure time, arrival time, or flight status.
- Delete flights and their associated assignments.
- View detailed flight reports.
- View delayed and cancelled flights.
- View upcoming flights.
- Summarise flights by status.

### Pilot Management

- View pilot records.
- Add new pilots.
- Update a pilot's active or inactive status.
- Delete pilot records.
- Assign pilots to flights as Captain, First Officer, or Relief Pilot.
- View pilot schedules and existing flight assignments.

### Destination Management

- View destination and airport information.
- Add destinations.
- Update destination details.
- Delete destinations when they are not referenced by existing flights.

### Database Reporting

- Count flights per destination.
- Count flight assignments per pilot.
- Summarise flights by status.
- Retrieve flight details with destination and pilot information using SQL joins.

## 4. Database Design

The database contains four related tables.

| Table | Purpose |
|---|---|
| `Destinations` | Stores airport names, cities, countries, and unique airport codes. |
| `Pilots` | Stores pilot names, licence numbers, hire dates, and active status. |
| `Flights` | Stores flight numbers, origins, destinations, schedules, and status. |
| `FlightAssignments` | Connects pilots to flights and records their assignment roles. |

### Relationships

- One destination can be associated with many flights.
- One flight can have multiple pilot assignments.
- One pilot can be assigned to multiple flights.
- `FlightAssignments` implements the many-to-many relationship between flights and pilots.

Primary keys, foreign keys, unique constraints, and check constraints help maintain data integrity.

## 5. Project Structure

```text
FlightManagement/
├── main.py
├── schema.sql
├── setup_database.py
├── flight_management.db
└── README.md
```

### File Descriptions

- `main.py` – Contains the command-line menu, application functions, and SQL queries.
- `schema.sql` – Defines the database tables, relationships, constraints, and indexes.
- `setup_database.py` – Creates the database and inserts sample records.
- `flight_management.db` – SQLite database file populated by the setup script.
- `README.md` – Project documentation.

## 6. Prerequisites

- Python 3.10 or later.
- SQLite support through Python's built-in `sqlite3` module.
- A terminal or GitHub Codespaces environment.

No external Python packages are required.

## 7. Installation and Setup

### Step 1: Clone the Repository

Replace the placeholders with your public GitHub repository details.

```bash
git clone https://github.com/Esha-Datwani/DBMSGradedAssignment1.git
```

Alternatively, open the repository directly in GitHub Codespaces.

### Step 2: Create and Populate the Database

Run:

```bash
python3 setup_database.py
```

The setup script reads `schema.sql`, creates the database tables, and inserts sample records for destinations, pilots, flights, and flight assignments.

On a fresh database, the expected sample data is:

- 12 destinations
- 12 pilots
- 12 flights
- 24 pilot assignments

The setup script uses `INSERT OR IGNORE` for sample records, so running it again should not duplicate records that already exist with matching unique keys.

### Step 3: Launch the Application

Run:

```bash
python3 main.py
```

The Flight Management System menu will appear in the terminal.

## 8. Application Menu

| Option | Function |
|---:|---|
| 1 | Add a New Flight |
| 2 | View All Flights |
| 3 | Search Flight by Flight Number |
| 4 | View Flights by Criteria |
| 5 | Update Flight Information |
| 6 | Delete a Flight |
| 7 | Assign Pilot to Flight |
| 8 | View Pilot Schedule |
| 9 | View Flight Assignments |
| 10 | Manage Destinations |
| 11 | Manage Pilots |
| 12 | Flight Details Report |
| 13 | Database Summaries |
| 14 | Delayed / Cancelled Flights |
| 15 | Upcoming Flights |
| 16 | View Flights by Status Summary |
| 0 | Exit |

## 9. Example Usage

### View All Flights

Run the application and select option `2`.

The application displays flight information, including the flight number, origin, destination, departure time, arrival time, and status in a formatted table.

### Search for a Flight

Select option `3` and enter a flight number, for example:

```text
Enter flight number: FM101
```

The application retrieves the matching flight and its destination information.

### Filter Flights

Select option `4` to search using one or more criteria:

- Destination airport code, such as `JFK`.
- Flight status, such as `Scheduled`.
- Departure date, such as `2027-04-12`.

Leave a field empty to skip that filter.

### Add a Flight

Select option `1` and provide the flight number, origin, destination ID, departure and arrival timestamps, and status.

Use the following timestamp format:

```text
YYYY-MM-DD HH:MM
```

The destination ID must already exist in the `Destinations` table.

### Assign a Pilot

Select option `7` and enter the flight ID, pilot ID, and assignment role.

Valid roles are:

- `Captain`
- `First Officer`
- `Relief Pilot`

Inactive pilots cannot be assigned through the application.

## 10. SQL Concepts Demonstrated

The application demonstrates the following database operations:

| SQL Concept | Purpose |
|---|---|
| `CREATE TABLE` | Defines the relational schema. |
| `INSERT` | Adds flights, pilots, destinations, and assignments. |
| `SELECT` | Retrieves stored records. |
| `WHERE` | Filters flights and identifies individual records. |
| `UPDATE` | Changes flight schedules, statuses, and destination or pilot information. |
| `DELETE` | Removes records while respecting foreign-key constraints. |
| `JOIN` | Combines information from related tables. |
| `LEFT JOIN` | Includes destinations or pilots even when they have no associated flights or assignments. |
| `COUNT()` and `GROUP BY` | Produce summaries of flights by destination, pilot, or status. |
| Parameterised queries | Use `?` placeholders to pass user input safely to SQLite. |

## 11. Data Integrity and Validation

The database and application include several validation measures:

- Flight numbers and pilot licence numbers must be unique.
- Airport codes must contain three characters.
- Foreign keys maintain relationships between tables.
- Flight statuses and assignment roles are restricted to permitted values.
- Inactive pilots cannot be assigned through the application.
- A flight cannot be deleted without its associated assignments being handled by the database's cascade rule.
- User-supplied values are passed through parameterised SQL queries.


## 12. Troubleshooting

### Database Not Found

Run:

```bash
python setup_database.py
```

Make sure `schema.sql` is in the same directory as `setup_database.py`.

### Python Module Error

The project uses only standard-library modules. If `sqlite3` is unavailable, check that Python was installed with SQLite support.

### Duplicate Flight or Pilot

Flight numbers and pilot licence numbers must be unique. Use a different value or review the existing record.

### Foreign-Key Constraint Error

Check that the referenced destination, flight, or pilot exists. A destination or pilot that is still referenced by other records cannot necessarily be deleted.

### Invalid Flight Schedule

Departure and arrival timestamps must be entered in the expected format, and departure must be earlier than arrival.

## 13. Testing

Test the application by performing the following operations:

1. Run the setup script and confirm the sample records are present.
2. Retrieve all flights and search for a flight by number.
3. Filter flights by destination, status, and date.
4. Add a test flight and verify that it can be retrieved.
5. Update the test flight's schedule or status and verify the change.
6. Assign a pilot and retrieve the pilot's schedule.
7. Add and update a destination.
8. View the database summaries.
9. Delete the test flight and confirm that its assignments are removed.

Capture screenshots of these operations for the accompanying project report.

## 14. Limitations and Future Improvements

Potential future enhancements include:

- A graphical user interface or web interface.
- More comprehensive validation of date and time inputs.
- Automatic detection of overlapping pilot schedules.
- Stronger operational rules for pilot assignments.
- User authentication and role-based permissions.
- Automated unit tests.
- Improved table formatting for narrow terminals.