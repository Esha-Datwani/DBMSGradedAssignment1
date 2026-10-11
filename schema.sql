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
    hire_date TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
    CHECK (active IN (0, 1))
);

-- 3. Store flight schedules.
CREATE TABLE IF NOT EXISTS Flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT NOT NULL UNIQUE,
    origin TEXT NOT NULL,
    destination_id INTEGER NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Scheduled'
        CHECK (status IN ('Scheduled', 'Boarding', 'Departed','Landed', 'Delayed', 'Cancelled')),
    FOREIGN KEY (destination_id)
        REFERENCES Destinations(destination_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CHECK (departure_time < arrival_time)
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