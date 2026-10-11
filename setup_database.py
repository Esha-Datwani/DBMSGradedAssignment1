import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "flight_management.db"
SCHEMA_FILE = BASE_DIR / "schema.sql"


def setup_database():
    """Create the tables and insert initial sample records."""

    if not SCHEMA_FILE.exists():
        raise FileNotFoundError("schema.sql was not found.")

    conn = sqlite3.connect(DB_FILE)

    # Foreign keys must be enabled for each SQLite connection.
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # Execute the SQL statements from schema.sql.
        schema = SCHEMA_FILE.read_text(encoding="utf-8")
        conn.executescript(schema)

        # -----------------------------------------
        # 1. Insert 12 destinations.
        # -----------------------------------------
        destinations = [
            ("Heathrow Airport", "London", "United Kingdom", "LHR"),
            ("John F. Kennedy Airport", "New York", "USA", "JFK"),
            ("Chhatrapati Shivaji Maharaj Airport", "Mumbai", "India", "BOM"),
            ("Dubai International Airport", "Dubai", "UAE", "DXB"),
            ("Singapore Changi Airport", "Singapore", "Singapore", "SIN"),
            ("Indira Gandhi Airport", "Delhi", "India", "DEL"),
            ("Charles de Gaulle Airport", "Paris", "France", "CDG"),
            ("Frankfurt Airport", "Frankfurt", "Germany", "FRA"),
            ("Tokyo Haneda Airport", "Tokyo", "Japan", "HND"),
            ("Sydney Kingsford Smith Airport", "Sydney", "Australia", "SYD"),
            ("Toronto Pearson Airport", "Toronto", "Canada", "YYZ"),
            ("Cape Town International Airport", "Cape Town", "South Africa", "CPT"),
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO Destinations
            (destination_name, city, country, airport_code)
            VALUES (?, ?, ?, ?)
        """, destinations)

        # -----------------------------------------
        # 2. Insert 12 pilots.
        # -----------------------------------------
        pilots = [
            ("Aisha", "Khan", "LIC1001", "2018-05-12"),
            ("Oliver", "Smith", "LIC1002", "2017-03-08"),
            ("Priya", "Patel", "LIC1003", "2020-07-19"),
            ("James", "Wilson", "LIC1004", "2016-11-21"),
            ("Meera", "Shah", "LIC1005", "2019-02-14"),
            ("Daniel", "Brown", "LIC1006", "2015-06-10"),
            ("Sofia", "Garcia", "LIC1007", "2021-01-25"),
            ("Arjun", "Mehta", "LIC1008", "2018-09-17"),
            ("Emily", "Taylor", "LIC1009", "2022-04-03"),
            ("Noah", "Martin", "LIC1010", "2014-08-29"),
            ("Fatima", "Ali", "LIC1011", "2020-12-01"),
            ("Lucas", "Anderson", "LIC1012", "2017-10-15"),
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO Pilots
            (first_name, last_name, licence_number, hire_date)
            VALUES (?, ?, ?, ?)
        """, pilots)

        # -----------------------------------------
        # 3. Insert 12 flights.
        # Airport codes link flights to destinations.
        # -----------------------------------------
        flights = [
            ("FM101", "Mumbai", "LHR", "2027-04-12 06:00", "2027-04-12 14:00", "Scheduled"),
            ("FM102", "London", "JFK", "2027-04-12 08:00", "2027-04-12 16:00", "Boarding"),
            ("FM103", "Delhi", "DXB", "2027-04-12 09:00", "2027-04-12 12:00", "Scheduled"),
            ("FM104", "Mumbai", "SIN", "2027-04-12 10:00", "2027-04-12 18:00", "Delayed"),
            ("FM105", "Dubai", "BOM", "2027-04-12 11:00", "2027-04-12 15:00", "Scheduled"),
            ("FM106", "London", "CDG", "2027-04-12 12:00", "2027-04-12 14:00", "Landed"),
            ("FM107", "Delhi", "FRA", "2027-04-12 13:00", "2027-04-12 22:00", "Scheduled"),
            ("FM108", "Singapore", "HND", "2027-04-12 14:00", "2027-04-13 01:00", "Scheduled"),
            ("FM109", "Sydney", "YYZ", "2027-04-12 15:00", "2027-04-13 05:00", "Cancelled"),
            ("FM110", "London", "SYD", "2027-04-12 16:00", "2027-04-13 10:00", "Scheduled"),
            ("FM111", "Mumbai", "CPT", "2027-04-12 17:00", "2027-04-13 01:00", "Scheduled"),
            ("FM112", "Delhi", "JFK", "2027-04-12 18:00", "2027-04-13 06:00", "Scheduled"),
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO Flights
            (flight_number, origin, destination_id,
             departure_time, arrival_time, status)
            VALUES (
                ?, ?, (
                    SELECT destination_id
                    FROM Destinations
                    WHERE airport_code = ?
                ), ?, ?, ?
            )
        """, flights)

        # -----------------------------------------
        # 4. Assign two pilots to each flight.
        # -----------------------------------------
        for i in range(12):
            flight_number = f"FM{101 + i}"

            flight = conn.execute("""
                SELECT flight_id
                FROM Flights
                WHERE flight_number = ?
            """, (flight_number,)).fetchone()

            captain_id = (i % 12) + 1
            officer_id = ((i + 1) % 12) + 1

            conn.execute("""
                INSERT OR IGNORE INTO FlightAssignments
                (flight_id, pilot_id, assignment_role)
                VALUES (?, ?, 'Captain')
            """, (flight[0], captain_id))

            conn.execute("""
                INSERT OR IGNORE INTO FlightAssignments
                (flight_id, pilot_id, assignment_role)
                VALUES (?, ?, 'First Officer')
            """, (flight[0], officer_id))

        conn.commit()

        print("\nDatabase created and populated successfully.")
        print(f"Database location: {DB_FILE}")

        # Display row counts to confirm setup.
        for table in (
            "Destinations", "Pilots", "Flights", "FlightAssignments"
        ):
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count} records")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    setup_database()