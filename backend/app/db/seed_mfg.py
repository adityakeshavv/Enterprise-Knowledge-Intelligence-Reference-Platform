import sqlite3
from pathlib import Path
from app.core.config import settings
from app.core.logging import logger

def seed_manufacturing_database(db_path: Path = None):
    target_path = db_path or (settings.ROOT_DIR / "data" / "manufacturing" / "manufacturing.db")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(target_path)
    cur = conn.cursor()
    
    # 1. Table: production_lines
    cur.execute("""
    CREATE TABLE IF NOT EXISTS production_lines (
        line_id TEXT PRIMARY KEY,
        plant_id TEXT NOT NULL,
        equipment_name TEXT NOT NULL,
        oee_target REAL NOT NULL,
        actual_oee REAL NOT NULL,
        installed_year INTEGER NOT NULL,
        status TEXT NOT NULL
    );
    """)

    # 2. Table: downtime_events
    cur.execute("""
    CREATE TABLE IF NOT EXISTS downtime_events (
        event_id TEXT PRIMARY KEY,
        line_id TEXT NOT NULL,
        plant_id TEXT NOT NULL,
        equipment_id TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        duration_hours REAL NOT NULL,
        category_code TEXT NOT NULL,
        recorded_cause TEXT NOT NULL,
        financial_impact_usd REAL NOT NULL,
        FOREIGN KEY (line_id) REFERENCES production_lines(line_id)
    );
    """)

    # 3. Table: supplier_quality
    cur.execute("""
    CREATE TABLE IF NOT EXISTS supplier_quality (
        lot_id TEXT PRIMARY KEY,
        supplier_name TEXT NOT NULL,
        component_category TEXT NOT NULL,
        defect_rate_ppm REAL NOT NULL,
        inspection_date TEXT NOT NULL,
        audit_status TEXT NOT NULL
    );
    """)

    # Clear existing demo records
    cur.execute("DELETE FROM downtime_events;")
    cur.execute("DELETE FROM production_lines;")
    cur.execute("DELETE FROM supplier_quality;")

    # Seed production_lines
    lines_data = [
        ("LINE-01", "PLANT-A", "Chassis Framing Cell", 0.85, 0.83, 2021, "OPERATIONAL"),
        ("LINE-02", "PLANT-A", "Robotic Arm Welding Cell (ARM-02)", 0.85, 0.71, 2022, "DEGRADED"),
        ("LINE-03", "PLANT-A", "Paint & Precision Coating", 0.88, 0.86, 2020, "OPERATIONAL"),
        ("LINE-04", "PLANT-A", "Final Inspection & Dyno Test", 0.90, 0.89, 2023, "OPERATIONAL"),
        ("LINE-B1", "PLANT-B", "Continuous Casting Furnace 1", 0.82, 0.81, 2019, "OPERATIONAL"),
    ]
    cur.executemany("INSERT INTO production_lines VALUES (?, ?, ?, ?, ?, ?, ?);", lines_data)

    # Seed downtime_events (Crucial: Event EVT-8401 contains the 14.2h Hydraulic Valve Seizure on Line 2)
    downtime_data = [
        ("EVT-8401", "LINE-02", "PLANT-A", "ARM-02", "2026-08-14 06:15:00", "2026-08-14 20:27:00", 14.2, "HYD-04", "Hydraulic valve seizure on robotic arm actuator", 42600.0),
        ("EVT-8312", "LINE-01", "PLANT-A", "CONV-04", "2026-08-02 11:00:00", "2026-08-02 15:30:00", 4.5, "MEC-01", "Conveyor motor bearing overheating", 11250.0),
        ("EVT-8499", "LINE-03", "PLANT-A", "SEAL-01", "2026-08-22 09:20:00", "2026-08-22 11:26:00", 2.1, "ELE-03", "Heating element thermocouple drift", 4800.0),
        ("EVT-8520", "LINE-02", "PLANT-A", "ARM-02", "2026-09-05 14:10:00", "2026-09-05 17:40:00", 3.5, "HYD-04", "Proportional pressure valve chatter and oscillation", 10500.0),
        ("EVT-8588", "LINE-04", "PLANT-A", "DYNO-01", "2026-09-18 08:00:00", "2026-09-18 09:12:00", 1.2, "CAL-02", "Routine dynamometer recalibration timeout", 2400.0),
    ]
    cur.executemany("INSERT INTO downtime_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", downtime_data)

    # Seed supplier_quality
    supplier_data = [
        ("LOT-2026-441", "Apex Hydraulics Inc", "Proportional Flow Valves", 840.5, "2026-07-28", "CORRECTIVE_ACTION_REQUIRED"),
        ("LOT-2026-402", "Apex Hydraulics Inc", "High Pressure Seal Kits", 620.0, "2026-08-04", "FLAGGED"),
        ("LOT-2026-512", "Vortex Robotics Components", "Actuator Servo Drives", 45.2, "2026-08-11", "PASSED"),
        ("LOT-2026-590", "Precision Castings LLC", "Furnace Liner Bricks", 88.0, "2026-08-19", "PASSED"),
    ]
    cur.executemany("INSERT INTO supplier_quality VALUES (?, ?, ?, ?, ?, ?);", supplier_data)

    conn.commit()
    conn.close()
    logger.info(f"Successfully seeded manufacturing database at {target_path}")

if __name__ == "__main__":
    seed_manufacturing_database()
