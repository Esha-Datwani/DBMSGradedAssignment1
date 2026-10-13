import sqlite3
from pathlib import Path

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

    separator = "+-" + "-+-".join(
        "-" * width for width in widths
    ) + "-+"

    print("\n" + separator)
    print("| " + " | ".join(
        headers[i].replace("_", " ").title().ljust(widths[i])
        for i in range(len(headers))
    ) + " |")
    print(separator)

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

                o.city AS origin_city,
                o.airport_code AS origin_code,

                d.city AS destination_city,
                d.airport_code AS destination_code,

                a.registration_number,
                a.model,

                f.departure_time,
                f.arrival_time,
                f.status

            FROM Flights f

            JOIN Destinations o ON f.origin_destination_id = o.destination_id

            JOIN Destinations d ON f.destination_id = d.destination_id

            JOIN Aircraft a ON f.aircraft_id = a.aircraft_id

            ORDER BY f.departure_time
        """).fetchall()

        show_rows(rows)


def add_flight():
    """Insert a new flight after validating aircraft and schedule."""
    flight_number = read_value("Flight number: ").upper()

    origin_destination_id = read_int("Origin Destination ID: ")
    destination_id = read_int("Destination ID: ")
    if origin_destination_id == destination_id:
        print("Origin and destination cannot be the same.")
        return

    aircraft_id = read_int("Aircraft ID: ")
    departure = read_value("Departure (YYYY-MM-DD HH:MM): ")
    arrival = read_value("Arrival (YYYY-MM-DD HH:MM): ")
    status = input(
        "Status (Scheduled/Boarding/Departed/Landed/"
        "Delayed/Cancelled) [Scheduled]: "
    ).strip() or "Scheduled"

    valid_statuses = ("Scheduled","Boarding","Departed","Landed","Delayed","Cancelled")

    if status not in valid_statuses:
        print("Invalid flight status.")
        return

    # Validate the timestamp format and chronological order.
    from datetime import datetime

    try:
        departure_dt = datetime.strptime(departure, "%Y-%m-%d %H:%M")
        arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date/time. Use YYYY-MM-DD HH:MM.")
        return

    if departure_dt >= arrival_dt:
        print("Arrival must be after departure.")
        return

    try:
        with get_connection() as conn:
            # Confirm that the selected aircraft exists and is available for assignment.
            aircraft = conn.execute("""
                SELECT status
                FROM Aircraft
                WHERE aircraft_id = ?
            """, (aircraft_id,)).fetchone()

            if aircraft is None:
                print("Aircraft ID not found.")
                return

            if aircraft["status"] != "Available":
                print(
                    "Cannot assign this aircraft. "
                    f"Current status: {aircraft['status']}."
                )
                return

            conn.execute("""
                INSERT INTO Flights (
                    flight_number,
                    origin_destination_id,
                    destination_id,
                    aircraft_id,
                    departure_time,
                    arrival_time,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                flight_number,
                origin_destination_id,
                destination_id,
                aircraft_id,
                departure,
                arrival,
                status
            ))

        print("Flight added successfully.")

    except sqlite3.IntegrityError as error:
        print(f"Could not add flight: {error}")


def view_flights():
    """Retrieve flights using optional search criteria."""
    destination = input("Destination airport code (Enter to skip): ").strip().upper()
    status = input("Status (Enter to skip): ").strip()
    departure_date = input("Departure date YYYY-MM-DD (Enter to skip): ").strip()

    query = """
        SELECT
            f.flight_id,
            f.flight_number,

            o.city AS origin_city,

            d.city AS destination_city,
            d.airport_code,

            a.registration_number,

            f.departure_time,
            f.arrival_time,
            f.status

        FROM Flights f

        JOIN Destinations o
        ON f.origin_destination_id = o.destination_id

        JOIN Destinations d
        ON f.destination_id = d.destination_id

        JOIN Aircraft a
        ON f.aircraft_id = a.aircraft_id

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
                o.city AS origin,
                d.city AS destination,
                d.airport_code,
                a.registration_number,
                a.model,
                f.departure_time,
                f.arrival_time,
                f.status

            FROM Flights f
            JOIN Destinations o ON f.origin_destination_id = o.destination_id
            JOIN Destinations d ON f.destination_id = d.destination_id
            JOIN Aircraft a ON f.aircraft_id = a.aircraft_id
            WHERE f.flight_number = ?
        """, (flight_number,)).fetchall()

        show_rows(rows)



def update_flight():
    """Update a flight's schedule or status with validation."""

    from datetime import datetime

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

    valid_statuses = (
        "Scheduled",
        "Boarding",
        "Departed",
        "Landed",
        "Delayed",
        "Cancelled"
    )

    try:
        with get_connection() as conn:
            # Get the existing flight.
            flight = conn.execute("""
                SELECT departure_time, arrival_time, status
                FROM Flights
                WHERE flight_id = ?
            """, (flight_id,)).fetchone()

            if flight is None:
                print("Flight ID not found.")
                return

            # Determine the resulting values before updating.
            departure = (
                new_value if column == "departure_time"
                else flight["departure_time"]
            )

            arrival = (
                new_value if column == "arrival_time"
                else flight["arrival_time"]
            )

            status = (
                new_value if column == "status"
                else flight["status"]
            )

            # Validate the new status.
            if status not in valid_statuses:
                raise ValueError("Invalid flight status.")

            # Validate date/time format and schedule.
            departure_dt = datetime.strptime(departure, "%Y-%m-%d %H:%M")
            arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M")

            if departure_dt >= arrival_dt:
                raise ValueError("Departure must be before arrival.")

            # Prevent premature landed status.
            if (
                status == "Landed"
                and arrival_dt > datetime.now()
            ):
                raise ValueError(
                    "A flight cannot be marked Landed "
                    "before its scheduled arrival time."
                )

            # Update only after all validations pass.
            conn.execute(
                f"UPDATE Flights SET {column} = ? "
                "WHERE flight_id = ?",
                (new_value, flight_id)
            )

        print("Flight updated successfully.")

    except (sqlite3.IntegrityError, ValueError) as error:
        print(f"Update failed: {error}")


def delete_flight():
    """Delete a flight and its associated assignments."""
    flight_id = read_int("Flight ID to delete: ")
    confirm = input("Delete this flight? Type YES to confirm: ").strip()

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
    """Assign a pilot to a flight."""

    flight_id = read_int("Flight ID: ")
    pilot_id = read_int("Pilot ID: ")
    role = read_value("Role (Captain/First Officer/Relief Pilot): ")
    if role not in ("Captain","First Officer","Relief Pilot"):
        print("Invalid assignment role.")
        return

    try:
        with get_connection() as conn:
            pilot = conn.execute("""
                SELECT
                    active,
                    rank
                FROM Pilots
                WHERE pilot_id = ?
            """, (pilot_id,)).fetchone()

            if pilot is None:
                print("Pilot not found.")
                return

            if pilot["active"] != 1:
                print("Cannot assign an inactive pilot.")
                return

            if (role == "Captain" and pilot["rank"] != "Captain"):
                print("Only pilots with Captain rank can be assigned as Captain.")
                return

            if (role == "First Officer" and pilot["rank"] != "First Officer"):
                print("Only pilots with First Officer rank can be assigned as First Officer.")
                return

            if role == "Captain":
                existing = conn.execute("""
                    SELECT 1
                    FROM FlightAssignments
                    WHERE flight_id = ?
                    AND assignment_role = 'Captain'
                """, (flight_id,)).fetchone()

                if existing:
                    print("This flight already has a Captain.")
                    return

            conn.execute("""
                INSERT INTO FlightAssignments
                (flight_id, pilot_id,assignment_role)
                VALUES (?, ?, ?)
            """, (
                flight_id,
                pilot_id,
                role
            ))

        print("Pilot assigned successfully.")

    except sqlite3.IntegrityError as error:
        print(f"Assignment failed: {error}")


def view_pilot_schedule():
    """Show all flights assigned to a pilot."""
    pilot_id = read_int("Pilot ID: ")

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.first_name, p.last_name,
                   f.flight_number, o.city AS origin,
                   d.city AS destination,
                   f.departure_time, f.arrival_time,
                   f.status, a.assignment_role
            FROM FlightAssignments a
            JOIN Pilots p ON a.pilot_id = p.pilot_id
            JOIN Flights f ON a.flight_id = f.flight_id
            JOIN Destinations o ON f.origin_destination_id = o.destination_id
            JOIN Destinations d ON f.destination_id = d.destination_id
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
                airport_code = read_value("New Airport code: ")

                cursor = conn.execute("""
                    UPDATE Destinations
                    SET city = ?, country = ?,
                        destination_name = ?, airport_code = ?
                    WHERE destination_id = ?
                """, (city, country, name, airport_code,destination_id))

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
                rank = read_value("Rank (Captain/First Officer): ")


                conn.execute("""
                    INSERT INTO Pilots
                    (first_name, last_name, licence_number, rank, hire_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (first, last, licence, rank, hire_date))
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


def manage_aircraft():
    """Manage aircraft records."""

    print("1. View Aircraft")
    print("2. Add Aircraft")
    print("3. Update Aircraft Status")
    print("4. Delete Aircraft")

    choice = input(
        "Select option: "
    ).strip()

    valid_statuses = (
        "Available",
        "Maintenance",
        "Out of Service"
    )

    try:

        with get_connection() as conn:

            if choice == "1":

                rows = conn.execute("""
                    SELECT *
                    FROM Aircraft
                    ORDER BY registration_number
                """).fetchall()

                show_rows(rows)

            elif choice == "2":

                registration = read_value("Registration Number: ")
                model = read_value("Model: ")
                manufacturer = read_value("Manufacturer: ")
                capacity = read_int("Seating Capacity: ")

                conn.execute("""
                    INSERT INTO Aircraft
                    (
                        registration_number,
                        model,
                        manufacturer,
                        seating_capacity
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    registration,
                    model,
                    manufacturer,
                    capacity
                ))

                print("Aircraft added.")

            elif choice == "3":

                aircraft_id = read_int("Aircraft ID: ")

                status = read_value(
                    "Status "
                    "(Available/Maintenance/"
                    "Out of Service): "
                )

                if status not in valid_statuses:
                    print("Invalid aircraft status.")
                    return

                cursor = conn.execute("""
                    UPDATE Aircraft
                    SET status = ?
                    WHERE aircraft_id = ?
                """, (
                    status,
                    aircraft_id
                ))

                print(
                    "Aircraft updated."
                    if cursor.rowcount
                    else "Aircraft not found."
                )

            elif choice == "4":

                aircraft_id = read_int("Aircraft ID: ")

                cursor = conn.execute("""
                    DELETE FROM Aircraft
                    WHERE aircraft_id = ?
                """, (aircraft_id,))

                print(
                    "Aircraft deleted."
                    if cursor.rowcount
                    else "Aircraft not found."
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
            SELECT
                d.city,
                d.airport_code,
                COUNT(f.flight_id) AS flight_count
            FROM Destinations d
            LEFT JOIN Flights f
                ON d.destination_id = f.destination_id
            GROUP BY
                d.destination_id,
                d.city,
                d.airport_code
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


        print("\nAircraft Utilisation:")
        rows = conn.execute("""
            SELECT
                a.registration_number,
                a.model,
                COUNT(f.flight_id) AS total_flights
            FROM Aircraft a
            LEFT JOIN Flights f ON a.aircraft_id = f.aircraft_id GROUP BY a.aircraft_id
            ORDER BY total_flights DESC
        """).fetchall()
        show_rows(rows)

        print("\nFlights by Status:")
        rows = conn.execute("""
            SELECT
                status,
                COUNT(*) AS total
            FROM Flights
            GROUP BY status
        """).fetchall()
        show_rows(rows)

        print("\nMost Active Pilots:")
        rows = conn.execute("""
            SELECT
                p.first_name,
                p.last_name,
                COUNT(a.flight_id) AS total_flights
            FROM Pilots p
            LEFT JOIN FlightAssignments a
                ON p.pilot_id = a.pilot_id
            GROUP BY p.pilot_id
            ORDER BY total_flights DESC
            LIMIT 5
        """).fetchall()

        show_rows(rows)

def flight_details_report():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT *
            FROM FlightOverview
            ORDER BY departure_time
        """).fetchall()

        show_rows(rows)

def delayed_cancelled_flights():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                flight_number,
                origin_city,
                destination_city,
                departure_time,
                status
            FROM FlightOverview
            WHERE status IN ('Delayed', 'Cancelled','Landed')
            ORDER BY departure_time
        """).fetchall()

        show_rows(rows)


def upcoming_flights():
    """Display upcoming flights that have not landed or been cancelled."""

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                flight_number,
                origin_city,
                destination_city,
                departure_time,
                status
            FROM FlightOverview
            WHERE departure_time >= datetime('now', 'localtime')
              AND status NOT IN ('Landed', 'Cancelled')
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
12. Manage Aircraft

13. Flight Details Report
14. Database Summaries
15. Delayed / Cancelled Flights
16. Upcoming Flights
17. View Flights by Status Summary

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
            "12": manage_aircraft,
            "13": flight_details_report,
            "14": show_summaries,
            "15": delayed_cancelled_flights,
            "16": upcoming_flights,
            "17": flights_by_status_summary
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