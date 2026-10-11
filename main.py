import sqlite3
from pathlib import Path

# Use the same database file as setup_database.py.
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "flight_management.db"


def get_connection():
    """Open a database connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def read_int(prompt):
    """Read a valid integer from the user."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Please enter a valid whole number.")


def read_value(prompt):
    """Read a non-empty value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def show_rows(rows):
    """Display SQLite query results as an aligned table."""

    if not rows:
        print("\nNo records found.")
        return

    # Extract column names from the SQLite result.
    headers = list(rows[0].keys())

    # Convert all values to strings for consistent formatting.
    data = [
        [str(row[header]) if row[header] is not None else "-"
         for header in headers]
        for row in rows
    ]

    # Calculate the width needed for each column.
    widths = [
        max(len(headers[i]),
            max(len(row[i]) for row in data))
        for i in range(len(headers))
    ]

    # Build the table's horizontal separator.
    separator = "+-" + "-+-".join(
        "-" * width for width in widths
    ) + "-+"

    # Print the column headings.
    print("\n" + separator)
    print("| " + " | ".join(
        headers[i].replace("_", " ").title().ljust(widths[i])
        for i in range(len(headers))
    ) + " |")
    print(separator)

    # Print each record.
    for row in data:
        print("| " + " | ".join(
            row[i].ljust(widths[i])
            for i in range(len(headers))
        ) + " |")

    print(separator)
    print(f"{len(data)} record(s) found.\n")

def view_all_flights():
    """Display all flights."""

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                f.flight_id,
                f.flight_number,
                f.origin,
                d.city AS destination_city,
                d.airport_code,
                f.departure_time,
                f.arrival_time,
                f.status
            FROM Flights f
            JOIN Destinations d
                ON f.destination_id = d.destination_id
            ORDER BY f.departure_time
        """).fetchall()

        show_rows(rows)


def add_flight():
    """Insert a new flight."""
    flight_number = read_value("Flight number: ")
    origin = read_value("Origin city/airport: ")
    destination_id = read_int("Destination ID: ")
    departure = read_value(
        "Departure (YYYY-MM-DD HH:MM): "
    )
    arrival = read_value(
        "Arrival (YYYY-MM-DD HH:MM): "
    )
    status = input(
        "Status (Scheduled/Boarding/Departed/Landed/"
        "Delayed/Cancelled) [Scheduled]: "
    ).strip() or "Scheduled"

    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO Flights
                (flight_number, origin, destination_id,
                 departure_time, arrival_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                flight_number, origin, destination_id,
                departure, arrival, status
            ))
        print("Flight added successfully.")
    except sqlite3.IntegrityError as error:
        print(f"Could not add flight: {error}")


def view_flights():
    """Retrieve flights using optional search criteria."""
    destination = input(
        "Destination airport code (Enter to skip): "
    ).strip().upper()
    status = input(
        "Status (Enter to skip): "
    ).strip()
    departure_date = input(
        "Departure date YYYY-MM-DD (Enter to skip): "
    ).strip()

    query = """
        SELECT f.flight_id, f.flight_number, f.origin,
               d.city AS destination_city,
               d.airport_code, f.departure_time,
               f.arrival_time, f.status
        FROM Flights f
        JOIN Destinations d
          ON f.destination_id = d.destination_id
        WHERE 1 = 1
    """
    params = []

    if destination:
        query += " AND d.airport_code = ?"
        params.append(destination)

    if status:
        query += " AND f.status = ?"
        params.append(status)

    if departure_date:
        query += " AND date(f.departure_time) = date(?)"
        params.append(departure_date)

    query += " ORDER BY f.departure_time"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        show_rows(rows)

def search_flight():
    """Search for a flight using its flight number."""

    flight_number = read_value(
        "Enter flight number: "
    ).upper()

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                f.flight_id,
                f.flight_number,
                f.origin,
                d.city AS destination,
                d.airport_code,
                f.departure_time,
                f.arrival_time,
                f.status
            FROM Flights f
            JOIN Destinations d
                ON f.destination_id = d.destination_id
            WHERE f.flight_number = ?
        """, (flight_number,)).fetchall()

        show_rows(rows)


def update_flight():
    """Update a flight's schedule or status."""
    flight_id = read_int("Flight ID to update: ")

    print("1. Change departure time")
    print("2. Change arrival time")
    print("3. Change status")
    choice = input("Select field: ").strip()

    fields = {
        "1": "departure_time",
        "2": "arrival_time",
        "3": "status"
    }

    if choice not in fields:
        print("Invalid choice.")
        return

    column = fields[choice]
    new_value = read_value(f"New {column}: ")

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE Flights SET {column} = ? "
                "WHERE flight_id = ?",
                (new_value, flight_id)
            )
            if cursor.rowcount:
                # Verify that the resulting schedule is valid.
                flight = conn.execute("""
                    SELECT departure_time, arrival_time
                    FROM Flights WHERE flight_id = ?
                """, (flight_id,)).fetchone()

                if flight["departure_time"] >= flight["arrival_time"]:
                    raise ValueError(
                        "Departure must be before arrival."
                    )
                print("Flight updated successfully.")
            else:
                print("Flight ID not found.")
    except (sqlite3.IntegrityError, ValueError) as error:
        print(f"Update failed: {error}")


def delete_flight():
    """Delete a flight and its associated assignments."""
    flight_id = read_int("Flight ID to delete: ")
    confirm = input(
        "Delete this flight? Type YES to confirm: "
    ).strip()

    if confirm != "YES":
        print("Deletion cancelled.")
        return

    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM Flights WHERE flight_id = ?",
            (flight_id,)
        )
        print(
            "Flight deleted." if cursor.rowcount
            else "Flight ID not found."
        )


def assign_pilot():
    """Assign a pilot to a flight in a specific role."""
    flight_id = read_int("Flight ID: ")
    pilot_id = read_int("Pilot ID: ")
    role = read_value(
        "Role (Captain/First Officer/Relief Pilot): "
    )

    if role not in ("Captain", "First Officer", "Relief Pilot"):
        print("Invalid assignment role.")
        return

    try:
        with get_connection() as conn:
            pilot = conn.execute("""
                SELECT active FROM Pilots WHERE pilot_id = ?
            """, (pilot_id,)).fetchone()

            if pilot is None:
                print("Pilot not found.")
                return

            if pilot["active"] != 1:
                print("Cannot assign an inactive pilot.")
                return

            if role == "Captain":
                existing = conn.execute("""
                    SELECT 1 FROM FlightAssignments
                    WHERE flight_id = ?
                      AND assignment_role = 'Captain'
                """, (flight_id,)).fetchone()

                if existing:
                    print("This flight already has a Captain.")
                    return

            conn.execute("""
                INSERT INTO FlightAssignments
                (flight_id, pilot_id, assignment_role)
                VALUES (?, ?, ?)
            """, (flight_id, pilot_id, role))

        print("Pilot assigned successfully.")
    except sqlite3.IntegrityError as error:
        print(f"Assignment failed: {error}")


def view_pilot_schedule():
    """Show all flights assigned to a pilot."""
    pilot_id = read_int("Pilot ID: ")

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.first_name, p.last_name,
                   f.flight_number, f.origin,
                   d.city AS destination,
                   f.departure_time, f.arrival_time,
                   f.status, a.assignment_role
            FROM FlightAssignments a
            JOIN Pilots p ON a.pilot_id = p.pilot_id
            JOIN Flights f ON a.flight_id = f.flight_id
            JOIN Destinations d
              ON f.destination_id = d.destination_id
            WHERE p.pilot_id = ?
            ORDER BY f.departure_time
        """, (pilot_id,)).fetchall()

        show_rows(rows)


def manage_destinations():
    """View destinations or update their details."""
    print("1. View all destinations")
    print("2. Update destination")
    print("3. Add destination")
    print("4. Delete destination")
    choice = input("Select option: ").strip()

    try:
        with get_connection() as conn:
            if choice == "1":
                rows = conn.execute("""
                    SELECT * FROM Destinations
                    ORDER BY city
                """).fetchall()
                show_rows(rows)

            elif choice == "2":
                destination_id = read_int("Destination ID: ")
                city = read_value("New city: ")
                country = read_value("New country: ")
                name = read_value("New airport name: ")

                cursor = conn.execute("""
                    UPDATE Destinations
                    SET city = ?, country = ?,
                        destination_name = ?
                    WHERE destination_id = ?
                """, (city, country, name, destination_id))

                print(
                    "Destination updated."
                    if cursor.rowcount else "Destination not found."
                )

            elif choice == "3":
                name = read_value("Airport name: ")
                city = read_value("City: ")
                country = read_value("Country: ")
                code = read_value("Three-letter airport code: ").upper()

                conn.execute("""
                    INSERT INTO Destinations
                    (destination_name, city, country, airport_code)
                    VALUES (?, ?, ?, ?)
                """, (name, city, country, code))
                print("Destination added.")

            elif choice == "4":
                destination_id = read_int("Destination ID: ")
                cursor = conn.execute("""
                    DELETE FROM Destinations
                    WHERE destination_id = ?
                """, (destination_id,))
                print(
                    "Destination deleted."
                    if cursor.rowcount
                    else "Destination not found."
                )

            else:
                print("Invalid option.")

    except sqlite3.IntegrityError as error:
        print(f"Operation failed: {error}")

def view_assignments():
    """Display all pilot assignments."""

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                f.flight_number,
                p.first_name || ' ' || p.last_name AS pilot_name,
                a.assignment_role
            FROM FlightAssignments a
            JOIN Flights f
                ON a.flight_id = f.flight_id
            JOIN Pilots p
                ON a.pilot_id = p.pilot_id
            ORDER BY f.flight_number
        """).fetchall()

        show_rows(rows)


def flights_by_status_summary():
    """Display number of flights for each status."""

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                status,
                COUNT(*) AS total_flights
            FROM Flights
            GROUP BY status
            ORDER BY total_flights DESC
        """).fetchall()

        show_rows(rows)

def manage_pilots():
    """View pilots, add pilots, update active status or delete."""
    print("1. View all pilots")
    print("2. Add pilot")
    print("3. Change pilot active status")
    print("4. Delete pilot")
    choice = input("Select option: ").strip()

    try:
        with get_connection() as conn:
            if choice == "1":
                show_rows(conn.execute("""
                    SELECT * FROM Pilots ORDER BY last_name
                """).fetchall())

            elif choice == "2":
                first = read_value("First name: ")
                last = read_value("Last name: ")
                licence = read_value("Licence number: ")
                hire_date = read_value("Hire date YYYY-MM-DD: ")

                conn.execute("""
                    INSERT INTO Pilots
                    (first_name, last_name, licence_number, hire_date)
                    VALUES (?, ?, ?, ?)
                """, (first, last, licence, hire_date))
                print("Pilot added.")

            elif choice == "3":
                pilot_id = read_int("Pilot ID: ")
                active = read_int("Enter 1 for active, 0 for inactive: ")

                if active not in (0, 1):
                    print("Status must be 0 or 1.")
                    return

                cursor = conn.execute("""
                    UPDATE Pilots SET active = ?
                    WHERE pilot_id = ?
                """, (active, pilot_id))
                print(
                    "Pilot status updated."
                    if cursor.rowcount else "Pilot not found."
                )

            elif choice == "4":
                pilot_id = read_int("Pilot ID: ")
                cursor = conn.execute("""
                    DELETE FROM Pilots WHERE pilot_id = ?
                """, (pilot_id,))
                print(
                    "Pilot deleted."
                    if cursor.rowcount else "Pilot not found."
                )

            else:
                print("Invalid option.")

    except sqlite3.IntegrityError as error:
        print(f"Operation failed: {error}")


def show_summaries():
    """Run aggregate queries for destinations and pilots."""
    with get_connection() as conn:
        print("\nFlights per destination:")
        rows = conn.execute("""
            SELECT d.city, d.airport_code,
                   COUNT(f.flight_id) AS flight_count
            FROM Destinations d
            LEFT JOIN Flights f
              ON d.destination_id = f.destination_id
            GROUP BY d.destination_id, d.city, d.airport_code
            ORDER BY flight_count DESC
        """).fetchall()
        show_rows(rows)

        print("\nFlights per pilot:")
        rows = conn.execute("""
            SELECT p.pilot_id, p.first_name, p.last_name,
                   COUNT(a.flight_id) AS flight_count
            FROM Pilots p
            LEFT JOIN FlightAssignments a
              ON p.pilot_id = a.pilot_id
            GROUP BY p.pilot_id
            ORDER BY flight_count DESC
        """).fetchall()
        show_rows(rows)

def flight_details_report():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                f.flight_number,
                f.origin,
                d.city AS destination,
                f.departure_time,
                f.arrival_time,
                f.status,
                p.first_name || ' ' || p.last_name AS pilot_name,
                a.assignment_role
            FROM Flights f
            JOIN Destinations d
                ON f.destination_id = d.destination_id
            LEFT JOIN FlightAssignments a
                ON f.flight_id = a.flight_id
            LEFT JOIN Pilots p
                ON a.pilot_id = p.pilot_id
            ORDER BY f.flight_number
        """).fetchall()

        show_rows(rows)

def delayed_cancelled_flights():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                flight_number,
                origin,
                departure_time,
                status
            FROM Flights
            WHERE status IN ('Delayed', 'Cancelled')
            ORDER BY departure_time
        """).fetchall()

        show_rows(rows)

def upcoming_flights():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                flight_number,
                origin,
                departure_time,
                status
            FROM Flights
            WHERE departure_time >= datetime('now')
            ORDER BY departure_time
            LIMIT 10
        """).fetchall()

        show_rows(rows)




def main():
    """Display the main menu until the user exits."""

    if not DB_FILE.exists():
        print("Database not found. Run setup_database.py first.")
        return

    while True:

        print("""
============== FLIGHT MANAGEMENT SYSTEM ==============

1.  Add a New Flight
2.  View All Flights
3.  Search Flight by Flight Number
4.  View Flights by Criteria
5.  Update Flight Information
6.  Delete a Flight

7.  Assign Pilot to Flight
8.  View Pilot Schedule
9.  View Flight Assignments

10. Manage Destinations
11. Manage Pilots

12. Flight Details Report
13. Database Summaries
14. Delayed / Cancelled Flights
15. Upcoming Flights
16. View Flights by Status Summary

0.  Exit

======================================================
""")

        choice = input("Enter your choice: ").strip()

        actions = {
            "1": add_flight,
            "2": view_all_flights,
            "3": search_flight,
            "4": view_flights,
            "5": update_flight,
            "6": delete_flight,
            "7": assign_pilot,
            "8": view_pilot_schedule,
            "9": view_assignments,
            "10": manage_destinations,
            "11": manage_pilots,
            "12": flight_details_report,
            "13": show_summaries,
            "14": delayed_cancelled_flights,
            "15": upcoming_flights,
            "16": flights_by_status_summary
        }

        if choice == "0":
            print("Thank you for using Flight Management System.")
            break

        action = actions.get(choice)

        if action:
            try:
                action()

            except sqlite3.Error as error:
                print(f"Database error: {error}")

            except (ValueError, TypeError) as error:
                print(f"Invalid input: {error}")

            except Exception as error:
                print(f"Unexpected error: {error}")

        else:
            print("Invalid menu choice. Please try again.")


if __name__ == "__main__":
    main()