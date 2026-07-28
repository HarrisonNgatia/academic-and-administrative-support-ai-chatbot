PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS CLASSES (
    class_id TEXT PRIMARY KEY,
    class_name TEXT NOT NULL,
    semester TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS STUDENTS (
    admission_no TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    department TEXT NOT NULL,
    class_id TEXT NOT NULL,
    phone_number TEXT UNIQUE,
    FOREIGN KEY (class_id) REFERENCES CLASSES(class_id)
);

CREATE TABLE IF NOT EXISTS TIMETABLES (
    timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id TEXT NOT NULL,
    day TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    unit_name TEXT NOT NULL,
    venue TEXT NOT NULL,
    FOREIGN KEY (class_id) REFERENCES CLASSES(class_id)
);

CREATE TABLE IF NOT EXISTS RESULTS (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT NOT NULL,
    unit_code TEXT NOT NULL,
    semester TEXT NOT NULL,
    grade TEXT NOT NULL,
    FOREIGN KEY (admission_no) REFERENCES STUDENTS(admission_no)
);

CREATE TABLE IF NOT EXISTS FEE_ACCOUNTS (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT NOT NULL UNIQUE,
    balance REAL NOT NULL,
    amount_paid REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (admission_no) REFERENCES STUDENTS(admission_no)
);

CREATE TABLE IF NOT EXISTS KNOWN_IDENTITIES (
    channel_id TEXT PRIMARY KEY,
    admission_no TEXT NOT NULL,
    verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_no) REFERENCES STUDENTS(admission_no)
);