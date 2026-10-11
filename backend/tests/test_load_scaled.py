"""AC-07-08 แบบย่อส่วน (T-09) ย่อจากผู้ใช้ 500 คน เป็น 20 คำขอพร้อมกัน (บันทึกใน ac-results.md)
ฉบับวัดได้จริงรอ CR-02 (quality-requirements.md) ผลบนเครื่องนักศึกษาเป็นเพียงสัญญาณ ไม่ใช่ผลตรวจรับจริง"""
from datetime import timedelta
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import session as db_session
from app.db.migrations.m001_init import upgrade
from app.db.models import Customer, ServiceAddress, Technician, TimeSlot
from tests.conftest import NOW, TOMORROW_14


# รองรับ AC-07-08 (REQ-QA-003) ฉบับย่อส่วน
def test_AC_07_08_search_under_load_scaled(tmp_path):
    # Use a file-backed database so concurrent requests get separate SQLite connections.
    engine = create_engine(
        f"sqlite:///{tmp_path / 'ac_07_08.sqlite3'}",
        connect_args={"check_same_thread": False},
        pool_size=20,
        max_overflow=0,
    )
    upgrade(engine)
    load_session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    previous_session_factory = db_session.SessionLocal
    db_session.SessionLocal = load_session_factory

    try:
        with load_session_factory() as db:
            customer = Customer(name="สมชาย", phone="081-234-5678")
            db.add(customer)
            db.flush()
            address = ServiceAddress(
                customer_id=customer.id,
                text="บ้านเลขที่ 12 ซอยสุขใจ",
                lat=13.7400,
                lng=100.5300,
            )
            technician = Technician(
                name="ประสิทธิ์",
                skills="ประปา",
                base_lat=13.7050,
                base_lng=100.5300,
            )
            db.add_all([address, technician])
            db.flush()
            slots = [
                TimeSlot(
                    technician_id=technician.id,
                    start=TOMORROW_14 + timedelta(days=day),
                    end=TOMORROW_14 + timedelta(days=day, hours=2),
                )
                for day in range(2)
            ]
            db.add_all(slots)
            db.commit()
            address_id = address.id
            technician_id = technician.id
            slot_ids = {slot.id for slot in slots}

        from app.main import app

        url = f"/technicians?category=ประปา&address_id={address_id}&now={NOW.isoformat()}"

        def timed_get(_):
            t0 = time.perf_counter()
            response = client.get(url)
            return response.status_code, response.json(), time.perf_counter() - t0

        with TestClient(app) as client:
            # Given ผู้ใช้ 20 คน (ย่อจาก 500) ส่งคำขอค้นหาช่างพร้อมกัน
            with ThreadPoolExecutor(max_workers=20) as pool:
                results = list(pool.map(timed_get, range(20)))

        # Then ทุกคำขอได้ช่างและช่วงเวลาที่ตั้งต้นไว้ครบ
        assert all(status == 200 for status, _, _ in results)
        assert all(
            len(body) == 1
            and body[0]["technician_id"] == technician_id
            and {slot["slot_id"] for slot in body[0]["slots"]} == slot_ids
            for _, body, _ in results
        )
        # Then 19 ใน 20 (ย่อจาก 95 ใน 100) ใช้เวลาไม่เกิน 2 วินาที
        fast = [elapsed for _, _, elapsed in results if elapsed <= 2.0]
        assert len(fast) >= 19
    finally:
        db_session.SessionLocal = previous_session_factory
        engine.dispose()
