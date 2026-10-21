from datetime import datetime, timedelta
from app.db.session import engine, SessionLocal, Base
from app.db.models import (
    User,
    PlantDowntimeEvent,
    MaintenanceWorkOrder,
    SupplierComponentQuality,
    ProductionLineMetric,
)
from app.core.auth import get_password_hash

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_database():
    init_db()
    db = SessionLocal()
    try:
        # 1. Seed Initial Users (CXO, Admin, Operator)
        if db.query(User).count() == 0:
            users = [
                User(
                    username="cxo_exec",
                    email="cxo@nebula9.ai",
                    full_name="Elena Vance (Chief Operating Officer)",
                    role="CXO",
                    hashed_password=get_password_hash("Executive2026!"),
                    is_active=True
                ),
                User(
                    username="admin",
                    email="admin@nebula9.ai",
                    full_name="System Administrator",
                    role="Admin",
                    hashed_password=get_password_hash("Admin2026!"),
                    is_active=True
                ),
                User(
                    username="operator_line3",
                    email="operator@nebula9.ai",
                    full_name="Marcus Vance (Line Operator)",
                    role="Operator",
                    hashed_password=get_password_hash("Operator2026!"),
                    is_active=True
                ),
            ]
            db.add_all(users)
            db.commit()
            print("Seeded users: cxo_exec, admin, operator_line3")

        # 2. Seed Plant Downtime Events (Manufacturing Reference Dataset)
        if db.query(PlantDowntimeEvent).count() == 0:
            now = datetime.utcnow()
            events = [
                PlantDowntimeEvent(
                    event_id="DWN-2024-001",
                    plant_id="Plant_A",
                    line_id="Line_3_Assembly",
                    start_timestamp=now - timedelta(days=20, hours=4),
                    end_timestamp=now - timedelta(days=20),
                    downtime_minutes=240,
                    error_code="ERR-HYD-401",
                    root_cause_category="Hydraulic System Failure"
                ),
                PlantDowntimeEvent(
                    event_id="DWN-2024-002",
                    plant_id="Plant_A",
                    line_id="Line_3_Assembly",
                    start_timestamp=now - timedelta(days=15, hours=6),
                    end_timestamp=now - timedelta(days=15),
                    downtime_minutes=360,
                    error_code="ERR-HYD-401",
                    root_cause_category="Hydraulic System Failure"
                ),
                PlantDowntimeEvent(
                    event_id="DWN-2024-003",
                    plant_id="Plant_A",
                    line_id="Line_1_Stamping",
                    start_timestamp=now - timedelta(days=10, hours=2),
                    end_timestamp=now - timedelta(days=10),
                    downtime_minutes=120,
                    error_code="ERR-ELEC-102",
                    root_cause_category="Electrical Relay Malfunction"
                ),
                PlantDowntimeEvent(
                    event_id="DWN-2024-004",
                    plant_id="Plant_A",
                    line_id="Line_3_Assembly",
                    start_timestamp=now - timedelta(days=5, hours=8),
                    end_timestamp=now - timedelta(days=5),
                    downtime_minutes=480,
                    error_code="ERR-HYD-401",
                    root_cause_category="Hydraulic System Failure"
                ),
            ]
            db.add_all(events)
            db.commit()
            print("Seeded PlantDowntimeEvents")

        # 3. Seed Maintenance Work Orders
        if db.query(MaintenanceWorkOrder).count() == 0:
            now = datetime.utcnow()
            work_orders = [
                MaintenanceWorkOrder(
                    work_order_id="WO-8910",
                    plant_id="Plant_A",
                    line_id="Line_3_Assembly",
                    completion_date=now - timedelta(days=19),
                    component_replaced="High-Pressure Hydraulic Seal (AFD-SEAL-882)",
                    cost_usd=14200.0,
                    labor_hours=14.5,
                    technician_id="TECH-409"
                ),
                MaintenanceWorkOrder(
                    work_order_id="WO-8944",
                    plant_id="Plant_A",
                    line_id="Line_3_Assembly",
                    completion_date=now - timedelta(days=14),
                    component_replaced="Hydraulic Return Valve",
                    cost_usd=8500.0,
                    labor_hours=8.0,
                    technician_id="TECH-112"
                ),
                MaintenanceWorkOrder(
                    work_order_id="WO-9012",
                    plant_id="Plant_A",
                    line_id="Line_1_Stamping",
                    completion_date=now - timedelta(days=9),
                    component_replaced="Solid-State Contactor",
                    cost_usd=2300.0,
                    labor_hours=3.5,
                    technician_id="TECH-303"
                ),
            ]
            db.add_all(work_orders)
            db.commit()
            print("Seeded MaintenanceWorkOrders")

        # 4. Seed Supplier Quality Batch Data
        if db.query(SupplierComponentQuality).count() == 0:
            now = datetime.utcnow()
            supplier_batches = [
                SupplierComponentQuality(
                    batch_id="BATCH-APEX-24Q1-A",
                    supplier_id="Apex Fluid Dynamics",
                    part_number="AFD-SEAL-882",
                    defect_rate_ppm=1850,
                    delivery_date=now - timedelta(days=45)
                ),
                SupplierComponentQuality(
                    batch_id="BATCH-VORTEX-24Q1",
                    supplier_id="Vortex Precision Pumps",
                    part_number="VORT-VALVE-12",
                    defect_rate_ppm=140,
                    delivery_date=now - timedelta(days=60)
                ),
            ]
            db.add_all(supplier_batches)
            db.commit()
            print("Seeded SupplierComponentQuality")

        # 5. Seed Production Line Metrics & OEE (Week 4)
        if db.query(ProductionLineMetric).count() == 0:
            now = datetime.utcnow()
            metrics_data = [
                ProductionLineMetric(plant_id="Plant_A", line_id="Line_3_Assembly", date=now - timedelta(days=20), planned_units=1200, actual_units=780, scrap_units=68, oee_percentage=58.2),
                ProductionLineMetric(plant_id="Plant_A", line_id="Line_3_Assembly", date=now - timedelta(days=15), planned_units=1200, actual_units=720, scrap_units=74, oee_percentage=54.5),
                ProductionLineMetric(plant_id="Plant_A", line_id="Line_3_Assembly", date=now - timedelta(days=10), planned_units=1200, actual_units=940, scrap_units=32, oee_percentage=71.0),
                ProductionLineMetric(plant_id="Plant_A", line_id="Line_3_Assembly", date=now - timedelta(days=5), planned_units=1200, actual_units=680, scrap_units=88, oee_percentage=51.8),
                ProductionLineMetric(plant_id="Plant_A", line_id="Line_1_Stamping", date=now - timedelta(days=20), planned_units=2000, actual_units=1920, scrap_units=18, oee_percentage=86.4),
                ProductionLineMetric(plant_id="Plant_A", line_id="Line_1_Stamping", date=now - timedelta(days=10), planned_units=2000, actual_units=1850, scrap_units=22, oee_percentage=83.1),
                ProductionLineMetric(plant_id="Plant_A", line_id="Line_2_Welding", date=now - timedelta(days=20), planned_units=1500, actual_units=1420, scrap_units=25, oee_percentage=81.2),
                ProductionLineMetric(plant_id="Plant_A", line_id="Line_2_Welding", date=now - timedelta(days=10), planned_units=1500, actual_units=1390, scrap_units=30, oee_percentage=79.5),
            ]
            db.add_all(metrics_data)
            db.commit()
            print("Seeded ProductionLineMetrics")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
