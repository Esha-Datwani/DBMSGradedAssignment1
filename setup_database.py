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
    
    # Allow rows to be accessed using column names.
    conn.row_factory = sqlite3.Row

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
            ("Aisha", "Khan", "LIC1001", "Captain", "2018-05-12"),
            ("Oliver", "Smith", "LIC1002", "Captain", "2017-03-08"),
            ("Priya", "Patel", "LIC1003", "First Officer", "2020-07-19"),
            ("James", "Wilson", "LIC1004", "Captain", "2016-11-21"),
            ("Meera", "Shah", "LIC1005", "First Officer", "2019-02-14"),
            ("Daniel", "Brown", "LIC1006", "Captain", "2015-06-10"),
            ("Sofia", "Garcia", "LIC1007", "First Officer", "2021-01-25"),
            ("Arjun", "Mehta", "LIC1008", "Captain", "2018-09-17"),
            ("Emily", "Taylor", "LIC1009", "First Officer", "2022-04-03"),
            ("Noah", "Martin", "LIC1010", "Captain", "2014-08-29"),
            ("Fatima", "Ali", "LIC1011", "First Officer", "2020-12-01"),
            ("Lucas", "Anderson", "LIC1012", "Captain", "2017-10-15")
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO Pilots
            (first_name, last_name, licence_number, rank, hire_date)
            VALUES (?, ?, ?, ?, ?)
        """, pilots)


        aircraft = [
            ("G-BOAA", "A380", "Airbus", 525, "Available"),
            ("N-747AA", "747-400", "Boeing", 416, "Available"),
            ("VT-A101", "A320", "Airbus", 180, "Available"),
            ("VT-A102", "A321", "Airbus", 220, "Available"),
            ("A6-E201", "777-300ER", "Boeing", 396, "Available"),
            ("9V-S301", "787-9", "Boeing", 290, "Available"),
            ("F-G401", "A350-900", "Airbus", 325, "Available"),
            ("D-A501", "A330-300", "Airbus", 300, "Available"),
            ("JA601", "787-8", "Boeing", 242, "Available"),
            ("VH-701", "A380", "Airbus", 525, "Available"),
            ("C-F801", "777-200LR", "Boeing", 317, "Available"),
            ("ZS-901", "737-800", "Boeing", 189, "Available")
        ]
        conn.executemany("""
            INSERT OR IGNORE INTO Aircraft
            (
                registration_number,
                model,
                manufacturer,
                seating_capacity,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, aircraft)


        # -----------------------------------------
        # 3. Insert 12 flights.
        # Airport codes link flights to destinations.
        # -----------------------------------------
        flights = [
            ("FM101","BOM","LHR",1,"2027-04-12 06:00","2027-04-12 14:00","Scheduled"),
            ("FM102","LHR","JFK",2,"2027-04-12 08:00","2027-04-12 16:00","Boarding"),
            ("FM103","DEL","DXB",3,"2027-04-12 09:00","2027-04-12 12:00","Scheduled"),
            ("FM104","BOM","SIN",4,"2027-04-12 10:00","2027-04-12 18:00","Delayed"),
            ("FM105","DXB","BOM",5,"2027-04-12 11:00","2027-04-12 15:00","Scheduled"),
            ("FM106","LHR","CDG",6,"2026-04-12 12:00","2026-04-12 14:00","Landed"),
            ("FM107","DEL","FRA",7,"2027-04-12 13:00","2027-04-12 22:00","Scheduled"),
            ("FM108","SIN","HND",8,"2027-04-12 14:00","2027-04-13 01:00","Scheduled"),
            ("FM109","SYD","YYZ",9,"2026-04-12 15:00","2026-12-13 05:00","Cancelled"),
            ("FM110","LHR","SYD",10,"2027-04-12 16:00","2027-04-13 10:00","Scheduled"),
            ("FM111","BOM","CPT",11,"2027-04-12 17:00","2027-04-13 01:00","Scheduled"),
            ("FM112","DEL","JFK",12,"2027-04-12 18:00","2027-04-13 06:00","Scheduled")
        ]
        conn.executemany("""
            INSERT OR IGNORE INTO Flights
            (
                flight_number,
                origin_destination_id,
                destination_id,
                aircraft_id,
                departure_time,
                arrival_time,
                status
            )
            VALUES
            (
                ?,

                (
                    SELECT destination_id
                    FROM Destinations
                    WHERE airport_code = ?
                ),

                (
                    SELECT destination_id
                    FROM Destinations
                    WHERE airport_code = ?
                ),

                ?,
                ?,
                ?,
                ?
            )
        """, flights)


        # -----------------------------------------
        # 4. Assign one Captain and one First Office to each flight.
        # -----------------------------------------

        # Retrieve active pilots according to their rank.
        captains = conn.execute("""
            SELECT pilot_id
            FROM Pilots
            WHERE rank = 'Captain'
              AND active = 1
            ORDER BY pilot_id
        """).fetchall()

        first_officers = conn.execute("""
            SELECT pilot_id
            FROM Pilots
            WHERE rank = 'First Officer'
              AND active = 1
            ORDER BY pilot_id
        """).fetchall()

        if not captains or not first_officers:
            raise ValueError(
                "Sample data must include at least one active Captain "
                "and one active First Officer."
            )

        # Retrieve all flights in a predictable order.
        flights_to_assign = conn.execute("""
            SELECT flight_id, flight_number
            FROM Flights
            ORDER BY flight_number
        """).fetchall()

        # Assign pilots according to their actual ranks.
        for i, flight in enumerate(flights_to_assign):

            captain_id = captains[i % len(captains)]["pilot_id"]
            officer_id = first_officers[i % len(first_officers)]["pilot_id"]

            conn.execute("""
                INSERT OR IGNORE INTO FlightAssignments
                    (flight_id, pilot_id, assignment_role)
                VALUES (?, ?, 'Captain')
            """, (flight["flight_id"], captain_id))

            conn.execute("""
                INSERT OR IGNORE INTO FlightAssignments
                    (flight_id, pilot_id, assignment_role)
                VALUES (?, ?, 'First Officer')
            """, (flight["flight_id"], officer_id))

        conn.commit()

        print("\nDatabase created and populated successfully.")
        print(f"Database location: {DB_FILE}")

        # Display row counts to confirm setup.
        for table in (
            "Destinations", "Pilots", "Aircraft", "Flights", "FlightAssignments"
        ):
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count} records")

        view_count = conn.execute("""SELECT COUNT(*) FROM FlightOverview""").fetchone()[0]
        print(f"FlightOverview: {view_count} rows")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    setup_database()