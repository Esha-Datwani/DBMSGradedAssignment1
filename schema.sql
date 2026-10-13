PRAGMA foreign_keys = ON;

-- 1. Store airport and destination information.
CREATE TABLE IF NOT EXISTS Destinations (
    destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    airport_code TEXT NOT NULL UNIQUE
    CHECK (length(airport_code) = 3)
);

-- 2. Store pilot information.
CREATE TABLE IF NOT EXISTS Pilots (
    pilot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    licence_number TEXT NOT NULL UNIQUE,
    rank TEXT NOT NULL CHECK (rank IN ('Captain','First Officer')),
    hire_date TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
    CHECK (active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS Aircraft (
    aircraft_id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number TEXT NOT NULL UNIQUE,
    model TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    seating_capacity INTEGER NOT NULL CHECK(seating_capacity > 0),
    status TEXT NOT NULL DEFAULT 'Available'
        CHECK(status IN (
            'Available',
            'Maintenance',
            'Out of Service'
        ))
);

-- 3. Store flight schedules.
CREATE TABLE IF NOT EXISTS Flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT NOT NULL UNIQUE,
    origin_destination_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    aircraft_id INTEGER NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Scheduled'
        CHECK(
            status IN (
                'Scheduled',
                'Boarding',
                'Departed',
                'Landed',
                'Delayed',
                'Cancelled'
            )
        ),
    FOREIGN KEY(origin_destination_id)
        REFERENCES Destinations(destination_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY(destination_id)
        REFERENCES Destinations(destination_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY(aircraft_id)
        REFERENCES Aircraft(aircraft_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CHECK(arrival_time > departure_time),
    CHECK(origin_destination_id <> destination_id)
);

-- 4. Link pilots to flights.
CREATE TABLE IF NOT EXISTS FlightAssignments (
    flight_id INTEGER NOT NULL,
    pilot_id INTEGER NOT NULL,
    assignment_role TEXT NOT NULL
        CHECK (assignment_role IN (
            'Captain', 'First Officer', 'Relief Pilot'
        )),
    PRIMARY KEY (flight_id, pilot_id),
    FOREIGN KEY (flight_id)
        REFERENCES Flights(flight_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (pilot_id)
        REFERENCES Pilots(pilot_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Indexes for common searches.
CREATE INDEX IF NOT EXISTS idx_flights_departure
    ON Flights(departure_time);

CREATE INDEX IF NOT EXISTS idx_flights_destination
    ON Flights(destination_id);

CREATE INDEX IF NOT EXISTS idx_assignments_pilot
    ON FlightAssignments(pilot_id);

CREATE INDEX IF NOT EXISTS idx_flights_origin
ON Flights(origin_destination_id);

CREATE INDEX IF NOT EXISTS idx_flights_aircraft
ON Flights(aircraft_id);


CREATE VIEW FlightOverview AS
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
JOIN Destinations o
ON f.origin_destination_id =
   o.destination_id
JOIN Destinations d
ON f.destination_id =
   d.destination_id
JOIN Aircraft a
ON f.aircraft_id =
   a.aircraft_id;


CREATE TRIGGER prevent_inactive_pilot_assignment
BEFORE INSERT ON FlightAssignments
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (
            SELECT active
            FROM Pilots
            WHERE pilot_id = NEW.pilot_id
        ) = 0
        THEN RAISE(
            ABORT,
            'Inactive pilot cannot be assigned'
        )
    END;
END;