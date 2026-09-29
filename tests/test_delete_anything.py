# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError, UserError


@tagged('post_install', '-at_install', 'delete_anything')
class TestDeleteAnything(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Tìm hoặc gán model res.partner.category để kiểm thử
        cls.category_model = cls.env['ir.model'].search([('model', '=', 'res.partner.category')], limit=1)
        cls.user_model = cls.env['ir.model'].search([('model', '=', 'res.users')], limit=1)

        # Tạo user thường không có quyền admin
        cls.regular_user = cls.env['res.users'].create({
            'name': 'Regular Test User',
            'login': 'regular_test_user_delete_anything',
            'email': 'regular@example.com',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

    def test_01_non_admin_access_error(self):
        """Kiểm tra người dùng không phải Admin sẽ bị chặn bởi AccessError ở cả ACL và phương thức thực thi"""
        # 1. Chặn ngay từ cấp độ tạo wizard do ACL
        with self.assertRaises(AccessError):
            self.env['delete.anything.wizard'].with_user(self.regular_user).create({
                'model_id': self.category_model.id,
                'target_type': 'record',
                'record_ids_input': '999999',
                'mode': 'safe',
            })

        # 2. Chặn ở cấp độ phương thức action_execute_delete
        wizard = self.env['delete.anything.wizard'].create({
            'model_id': self.category_model.id,
            'target_type': 'record',
            'record_ids_input': '999999',
            'mode': 'safe',
        })
        with self.assertRaises(AccessError):
            wizard.with_user(self.regular_user).action_execute_delete()

    def test_02_safe_mode_delete_records(self):
        """Kiểm tra Safe Mode xóa thành công các bản ghi qua ORM unlink"""
        cat1 = self.env['res.partner.category'].create({'name': 'Test Cat Safe 1'})
        cat2 = self.env['res.partner.category'].create({'name': 'Test Cat Safe 2'})
        ids_input = f"{cat1.id}, {cat2.id}"

        wizard = self.env['delete.anything.wizard'].create({
            'model_id': self.category_model.id,
            'target_type': 'record',
            'record_ids_input': ids_input,
            'mode': 'safe',
        })
        wizard.action_execute_delete()

        self.assertFalse(cat1.exists(), "Bản ghi cat1 phải bị xóa khỏi database.")
        self.assertFalse(cat2.exists(), "Bản ghi cat2 phải bị xóa khỏi database.")

    def test_03_force_mode_delete_records(self):
        """Kiểm tra Force Mode xóa thành công các bản ghi qua Raw SQL"""
        cat1 = self.env['res.partner.category'].create({'name': 'Test Cat Force 1'})
        cat2 = self.env['res.partner.category'].create({'name': 'Test Cat Force 2'})
        ids_input = f"{cat1.id}, {cat2.id}"

        wizard = self.env['delete.anything.wizard'].create({
            'model_id': self.category_model.id,
            'target_type': 'record',
            'record_ids_input': ids_input,
            'mode': 'force',
        })
        wizard.action_execute_delete()

        self.assertFalse(cat1.exists(), "Bản ghi cat1 phải bị xóa trực tiếp bằng SQL.")
        self.assertFalse(cat2.exists(), "Bản ghi cat2 phải bị xóa trực tiếp bằng SQL.")

    def test_04_protected_table_truncate_block(self):
        """Kiểm tra hệ thống chặn truncate các bảng hệ thống quan trọng như res_users"""
        wizard = self.env['delete.anything.wizard'].create({
            'model_id': self.user_model.id,
            'target_type': 'table',
            'mode': 'force',
        })
        with self.assertRaises(UserError):
            wizard.action_execute_delete()

    def test_05_force_mode_truncate_table(self):
        """Kiểm tra Force Mode Truncate Table làm sạch toàn bộ dữ liệu bảng"""
        # Tạo bản ghi test
        self.env['res.partner.category'].create({'name': 'Test Truncate 1'})
        self.env['res.partner.category'].create({'name': 'Test Truncate 2'})

        wizard = self.env['delete.anything.wizard'].create({
            'model_id': self.category_model.id,
            'target_type': 'table',
            'mode': 'force',
            'restart_identity': True,
        })
        wizard.action_execute_delete()

        count = self.env['res.partner.category'].search_count([])
        self.assertEqual(count, 0, "Toàn bộ dữ liệu bảng res.partner.category phải được làm sạch sau khi Truncate.")
