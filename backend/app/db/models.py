from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="Operator")  # "CXO", "Admin", "Operator"
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)
    industry_id = Column(String(50), nullable=False)
    query_text = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="COMPLETED")
    execution_time_ms = Column(Float, nullable=False)
    agents_invoked = Column(String(255), nullable=True)

# Manufacturing Domain Seed Tables (Week 2 Foundation, expanded in Week 4 & 8)
class PlantDowntimeEvent(Base):
    __tablename__ = "plant_downtime_events"

    event_id = Column(String(50), primary_key=True, index=True)
    plant_id = Column(String(50), index=True, nullable=False)
    line_id = Column(String(50), index=True, nullable=False)
    start_timestamp = Column(DateTime, nullable=False)
    end_timestamp = Column(DateTime, nullable=False)
    downtime_minutes = Column(Integer, nullable=False)
    error_code = Column(String(50), nullable=False)
    root_cause_category = Column(String(100), nullable=False)

class MaintenanceWorkOrder(Base):
    __tablename__ = "maintenance_work_orders"

    work_order_id = Column(String(50), primary_key=True, index=True)
    plant_id = Column(String(50), index=True, nullable=False)
    line_id = Column(String(50), index=True, nullable=False)
    completion_date = Column(DateTime, nullable=False)
    component_replaced = Column(String(100), nullable=False)
    cost_usd = Column(Float, nullable=False)
    labor_hours = Column(Float, nullable=False)
    technician_id = Column(String(50), nullable=False)

class SupplierComponentQuality(Base):
    __tablename__ = "supplier_component_quality"

    batch_id = Column(String(50), primary_key=True, index=True)
    supplier_id = Column(String(100), index=True, nullable=False)
    part_number = Column(String(50), nullable=False)
    defect_rate_ppm = Column(Integer, nullable=False)
    delivery_date = Column(DateTime, nullable=False)

class ProductionLineMetric(Base):
    __tablename__ = "production_line_metrics"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(String(50), index=True, nullable=False)
    line_id = Column(String(50), index=True, nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    planned_units = Column(Integer, nullable=False)
    actual_units = Column(Integer, nullable=False)
    scrap_units = Column(Integer, nullable=False)
    oee_percentage = Column(Float, nullable=False)
