# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import SQL

# Danh sách các bảng/model hệ thống trọng yếu được bảo vệ tuyệt đối không cho phép Truncate
PROTECTED_TABLES = {
    'ir_model',
    'ir_model_fields',
    'ir_module_module',
    'res_users',
    'res_company',
    'ir_attachment',
    'ir_cron',
    'res_groups',
}

PROTECTED_MODELS = {
    'ir.model',
    'ir.model.fields',
    'ir.module.module',
    'res.users',
    'res.company',
    'ir.attachment',
    'ir.cron',
    'res.groups',
}


class DeleteAnythingWizard(models.TransientModel):
    _name = 'delete.anything.wizard'
    _description = 'Delete Anything Wizard'

    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        domain="[('transient', '=', False)]",
        help="Select the model whose records or table you wish to delete."
    )
    model_name = fields.Char(
        related='model_id.model',
        readonly=True,
        string='Technical Model'
    )
    table_name = fields.Char(
        string='Database Table Name',
        compute='_compute_table_name',
        readonly=True
    )
    target_type = fields.Selection([
        ('record', 'Specific Record(s)'),
        ('table', 'Entire Table (Truncate)')
    ], default='record', required=True, string='Target Type')

    record_ids_input = fields.Char(
        string='Record IDs',
        help='Enter comma-separated IDs, e.g.: 10, 11, 45'
    )
    mode = fields.Selection([
        ('safe', 'Safe Mode (Odoo ORM unlink)'),
        ('force', 'Force Mode (Raw SQL CASCADE)')
    ], default='force', required=True, string='Deletion Mode')

    restart_identity = fields.Boolean(
        string='Restart Sequence / Identity',
        default=True,
        help='Reset ID auto-increment sequence back to 1 when truncating table.'
    )

    @api.depends('model_id', 'model_name')
    def _compute_table_name(self):
        # Tính toán tên bảng vật lý tương ứng trong PostgreSQL
        for record in self:
            if record.model_name and record.model_name in self.env:
                record.table_name = self.env[record.model_name]._table
            else:
                record.table_name = False

    def action_execute_delete(self):
        """Thực thi xóa bản ghi hoặc truncate bảng theo cấu hình đã chọn"""
        self.ensure_one()

        # 1. Kiểm tra quyền bảo mật tối cao: chỉ Admin mới được phép
        if not self.env.is_admin():
            raise AccessError(_("Only administrators are permitted to perform delete operations."))

        if not self.model_name or self.model_name not in self.env:
            raise UserError(_("Invalid model specified."))

        table_name = self.env[self.model_name]._table

        # 2. Xử lý xóa toàn bộ bảng (Truncate Table)
        if self.target_type == 'table':
            if table_name in PROTECTED_TABLES or self.model_name in PROTECTED_MODELS:
                raise UserError(
                    _("Truncating critical system table '%s' is strictly prohibited to prevent damaging the system.")
                    % table_name
                )

            if self.mode == 'safe':
                records = self.env[self.model_name].search([])
                count = len(records)
                records.unlink()
                msg = _("Successfully deleted %s records from '%s' via ORM unlink.") % (count, self.model_name)
            else:
                # Force Mode: Truncate Table CASCADE bằng Raw SQL
                if self.restart_identity:
                    query = SQL("TRUNCATE TABLE %s RESTART IDENTITY CASCADE", SQL.identifier(table_name))
                else:
                    query = SQL("TRUNCATE TABLE %s CASCADE", SQL.identifier(table_name))
                self.env.cr.execute(query)
                msg = _("Successfully truncated table '%s' with CASCADE.") % table_name

        # 3. Xử lý xóa bản ghi cụ thể theo danh sách ID
        else:
            raw_ids = [x.strip() for x in (self.record_ids_input or '').split(',') if x.strip()]
            valid_ids = [int(x) for x in raw_ids if x.isdigit()]
            if not valid_ids:
                raise UserError(_("Please provide at least one valid numeric Record ID."))

            if self.mode == 'safe':
                records = self.env[self.model_name].browse(valid_ids).exists()
                count = len(records)
                records.unlink()
                msg = _("Successfully deleted %s records from '%s' via ORM unlink.") % (count, self.model_name)
            else:
                # Force Mode: Xóa trực tiếp bằng SQL DELETE
                query = SQL("DELETE FROM %s WHERE id IN %s", SQL.identifier(table_name), tuple(valid_ids))
                self.env.cr.execute(query)
                rowcount = self.env.cr.rowcount
                msg = _("Successfully deleted %s records from '%s' via Raw SQL.") % (rowcount, table_name)

        # 4. Làm sạch triệt để bộ nhớ đệm (Cache Invalidation)
        self.env.invalidate_all()
        self.env.registry.clear_cache()

        # 5. Trả về thông báo thành công và đóng wizard
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Deletion Completed"),
                'message': msg,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
