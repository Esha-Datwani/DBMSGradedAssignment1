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
- Filter flights by destination, status, and departure date.
- Update departure time, arrival time, or flight status.
- Delete flights and their associated assignments.
- View detailed flight reports.
- View delayed and cancelled flights.
- View upcoming flights.
- Summarise flights by status.
- View flight overview reports.

### Pilot Management

- View pilot records.
- Add new pilots.
- Update a pilot's active or inactive status.
- Delete pilot records.
- Assign pilots to flights as Captain, First Officer, or Relief Pilot.
- View pilot schedules and existing flight assignments.
- Pilot rank management (Captain / First Officer).
- Validation of pilot-role assignments.

### Aircraft Management

- View aircraft records.
- Add aircraft.
- Update aircraft operational status.
- Delete aircraft.
- Track aircraft utilisation.

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

The database contains five main tables, one database view, and one trigger

| Table | Purpose |
|---------|---------|
| Destinations | Stores airports, city, country and airport code information. |
| Pilots | Stores pilot details, ranks, licence numbers and active status. |
| Aircraft | Stores aircraft registration, model, manufacturer and operational status. |
| Flights | Stores scheduled flights, origin and destination airports, aircraft and status. |
| FlightAssignments | Implements pilot-to-flight assignments. |

### Additional Database Objects

| Object | Purpose |
|----------|----------|
| FlightOverview (View) | Provides consolidated flight, airport and aircraft information. |
| prevent_inactive_pilot_assignment (Trigger) | Prevents inactive pilots from being assigned to flights. |

### Relationships

- One destination can be the origin for many flights.
- One destination can be the destination for many flights.
- One aircraft can operate many flights.
- One flight can have multiple pilot assignments.
- One pilot can be assigned to multiple flights.
- FlightAssignments implements the many-to-many relationship between pilots and flights.

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
- 12 aircraft
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
|----------|----------|
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
| 12 | Manage Aircraft |
| 13 | Flight Details Report |
| 14 | Database Summaries |
| 15 | Delayed / Cancelled Flights |
| 16 | Upcoming Flights |
| 17 | View Flights by Status Summary |
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

Select option 1 and provide:

- Flight Number
- Origin Destination ID
- Destination ID
- Aircraft ID
- Departure Time
- Arrival Time
- Status

The origin and destination must be different.
The destination and aircraft records must already exist.

### Assign a Pilot

Select option `7` and enter the flight ID, pilot ID, and assignment role.

Valid roles are:

- `Captain`
- `First Officer`
- `Relief Pilot`

Additional business rules:
- Inactive pilots cannot be assigned.
- Only pilots with rank Captain can be assigned as Captain.
- Only pilots with rank First Officer can be assigned as First Officer.
- A flight can have only one Captain assignment.

## Database Design Principles

The database was designed according to Third Normal Form (3NF) principles. Repeating data has been eliminated through the use of foreign-key relationships between Flights, Destinations, Aircraft, and Pilots. A junction table (FlightAssignments) is used to model the many-to-many relationship between pilots and flights.

The implementation also demonstrates:
- Primary Keys
- Foreign Keys
- CHECK Constraints
- Triggers
- Views
- Indexes
- Aggregate Queries
- Transaction Management

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
| `VIEW` | Provides consolidated flight reporting through FlightOverview. |
| `TRIGGER` | Prevents assignment of inactive pilots. |
| `INDEX` | Improves performance of common queries. |
| `CHECK Constraints` | Enforce business rules such as flight status and pilot rank. |
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
- Aircraft statuses are restricted to predefined values.
- Pilot ranks are restricted to Captain or First Officer.
- Origin and destination airports cannot be the same.
- Aircraft must exist before they can be assigned to a flight.
- Trigger-based validation prevents inactive pilots being assigned to flights.


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
10. Add and manage aircraft records.
11. Verify that inactive pilots cannot be assigned.
12. Verify that pilot rank restrictions are enforced.
13. Verify aircraft utilisation reporting.
14. Verify FlightOverview view output.

Capture screenshots of these operations for the accompanying project report.

## 14. Limitations and Future Improvements

Potential future enhancements include:

- A graphical user interface or web interface.
- More comprehensive validation of date and time inputs.
- Automatic detection of overlapping pilot schedules.
- Pilot schedule conflict detection.
- Aircraft maintenance scheduling.
- Aircraft availability checking before flight assignment.
- Crew management beyond pilots.
- Route profitability and operational analytics.
- User authentication and role-based permissions.
- Automated unit tests.
- Improved table formatting for narrow terminals.