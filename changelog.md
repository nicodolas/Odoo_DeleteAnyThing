# Changelog - Delete Anything

Tất cả các thay đổi của module **Delete Anything** (`delete_anything`) được ghi nhận tại đây.

## [2026-09-28]
- **Tác giả:** Johnny
- **Nội dung khởi tạo & triển khai:**
  - Khởi tạo module `delete_anything` tại thư mục `addons_custom` và đăng ký đường dẫn vào `odoo-local.conf`.
  - Thiết lập phân quyền truy cập `ir.model.access.csv` giới hạn riêng cho nhóm Quản trị viên tối cao (`base.group_system`).
  - Xây dựng Wizard `delete.anything.wizard` hỗ trợ:
    + Chọn Model và tự động nhận diện Database Table Name.
    + Xóa bản ghi cụ thể theo danh sách ID hoặc Truncate toàn bộ bảng.
    + Dual Mode: **Safe Mode** (Odoo ORM `unlink`) và **Force Mode** (Raw SQL `DELETE` / `TRUNCATE TABLE ... CASCADE` theo chuẩn Odoo 19 `from odoo.tools import SQL`).
    + Tự động làm sạch bộ nhớ đệm (`self.env.invalidate_all()` và `self.env.registry.clear_cache()`).
    + Danh sách cấm bảo vệ các bảng hệ thống quan trọng (`res_users`, `ir_model`, `res_company`, `ir_cron`, ...).
  - Xây dựng giao diện Form Wizard kèm cảnh báo màu đỏ (`alert-danger`) và hộp thoại xác nhận an toàn `confirm`.
  - Xây dựng Owl Frontend Component:
    + Biểu tượng thùng rác màu đỏ trên Systray nằm ngay cạnh Debug menu (`sequence: 99`).
    + Lắng nghe phím tắt toàn cục **`Ctrl + D`** (chặn hành vi bookmark mặc định của trình duyệt) và tự động mở Form Wizard cho Admin.
  - **Kết quả Unit Test:** Đã chạy kiểm thử với `odoo --test-enable --test-tags /delete_anything`, toàn bộ 5/5 test cases đều **PASS 100%** (0 errors, 0 failures):
    + `test_01_non_admin_access_error`: PASS
    + `test_02_safe_mode_delete_records`: PASS
    + `test_03_force_mode_delete_records`: PASS
    + `test_04_protected_table_truncate_block`: PASS
    + `test_05_force_mode_truncate_table`: PASS
