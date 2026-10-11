# ผลตรวจ Acceptance Criteria: UC-07

อัปเดต: 11 ต.ค. 2569
อ้างอิงข้อกำหนด: `booking.feature` v1.2 และ `spec.md` v1.2
หลักฐานรอบล่าสุด: `cd backend && python -m pytest -v` หลังแก้ test AC-07-08
หมายเหตุ: AC-07-08 ยังคงเป็น test ย่อส่วน 20 คำขอ ไม่ใช่ผลตรวจรับโหลด 500 ผู้ใช้

## ผลล่าสุดราย AC

| AC ID | Test / หลักฐาน | ผลล่าสุด | หมายเหตุ |
|---|---|---|---|
| AC-07-01 | `test_AC_07_01_booking_success` | ผ่าน | สร้างงานยืนยันแล้ว ช่วงเวลาถูกจอง และมีรายการชำระหนึ่งรายการ |
| AC-07-02 | `test_AC_07_02_slot_not_rebookable` | ผ่าน | ไม่เสนอช่วงที่จองแล้ว และ test ตรวจช่างที่ไกลเกิน BR-03 ด้วย |
| AC-07-03 | `test_AC_07_03_notify_both_within_60s` | ผ่าน | มีข้อความถึงลูกค้าและช่างในคิวตามเงื่อนไข |
| AC-07-04 | `test_AC_07_04_no_charge_when_slot_taken`; `AC-07-04.test.jsx` | ผ่าน | Backend ผ่านในรอบล่าสุดที่ส่งมา; frontend test เคยผ่านตามผลที่บันทึกไว้ก่อนหน้า |
| AC-07-05 | `test_AC_07_05_payment_timeout` | ผ่าน | ตรวจ timeout ชั่วคราว 30 วินาที, inquiry ด้วย reference เดิม และไม่มีรายการชำระสำเร็จ |
| AC-07-06 | `test_AC_07_06_payment_declined` | ผ่าน | ยกเลิกอัตโนมัติ คืน slot และแจ้งลูกค้า |
| AC-07-07 | `test_AC_07_07_inquiry_approved_no_double_charge` | ผ่าน | inquiry พบ approved แล้วไม่ authorize ซ้ำ |
| AC-07-08 | `test_AC_07_08_search_under_load_scaled` | ผ่าน (ย่อส่วน) | 20 คำขอพร้อมกันผ่านและตอบข้อมูลช่าง/ช่วงเวลาตาม seed; test ใช้ฐานข้อมูล SQLite แบบไฟล์และ connection pool แทน in-memory `StaticPool` ที่แชร์ connection เดียว |
| AC-07-09 | `test_AC_07_09_phone_hidden_until_2h` | ผ่าน | ผ่านตามผล `pytest -v` ที่ทีมส่งมา |
| AC-07-10 R1, R2, R4, R5, R6 | `test_AC_07_10_refund` และ `test_AC_07_10_refund_R6_not_allowed` | ผ่าน | แถวเหล่านี้ผ่านตามผลล่าสุด |
| AC-07-10 R3 | `test_AC_07_10_refund_R3`; `test_AC_07_10_refund_R3_temporary_behaviour` | รอ Q-14 / พฤติกรรมชั่วคราวผ่าน | Test ที่ตัดสินผลคืนเงินถูก skip เพราะ Q-14 ยังเปิด; test พฤติกรรมชั่วคราวที่ไม่อนุญาตให้ยกเลิกผ่าน |

## สรุปผลรอบล่าสุด

- Backend: **15 passed, 1 skipped**
- AC-07-08 ผ่านแบบย่อส่วน หลังปรับ test ให้ใช้ฐานข้อมูลที่รองรับ concurrent connections
- รายการที่ skip: AC-07-10 R3 เนื่องจากรอคำตอบ Q-14
- Frontend: `npm test` ได้ **1 passed** ตามผลที่บันทึกไว้ก่อนหน้า (ไม่ได้รันซ้ำในรอบนี้)

## ข้อจำกัดและการติดตาม

1. Test AC-07-08 เป็นการย่อจาก 500 เหลือ 20 คำขอพร้อมกัน จึง **ยังสรุปไม่ได้ว่า REQ-QA-003 ผ่าน** และไม่ใช่ผลตรวจรับโหลด 500 ผู้ใช้
2. Failure เดิมเกิดขณะยิงคำขอพร้อมกันบน in-memory SQLite ที่ตั้ง `StaticPool` ให้ทุก session ใช้ connection เดียว ซึ่งสอดคล้องกับปัญหาการใช้ connection ร่วมกัน; เปลี่ยน test มาใช้ฐานข้อมูลแบบไฟล์พร้อม connection pool แล้วไม่พบ exception ในการรันซ้ำ
3. CR-02 ของ AC-07-08 ยังรออนุมัติตาม `booking.feature`; ต้องกำหนดวิธีวัดที่ยอมรับก่อนใช้ผล load test เป็นการตรวจรับจริง
4. AC-07-10 R3 ยังเป็นคำถามเปิด Q-14; ผลพฤติกรรมชั่วคราวไม่ถือเป็นการตัดสินนโยบายคืนเงินขั้นสุดท้าย

## ผลรอบก่อนหน้า

ก่อนแก้ test ฐานข้อมูล AC-07-08 ล้มจาก exception (`slot is None` และ `tech.base_lng is None`) ระหว่างการยิงคำขอพร้อมกัน จึงยังวัด latency ไม่ได้
