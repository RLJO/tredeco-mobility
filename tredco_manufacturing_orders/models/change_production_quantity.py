# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ChangeProductionQtyCT(models.TransientModel):
    _inherit = 'change.production.qty'

    @api.multi
    def change_prod_qty(self):
        res = super(ChangeProductionQtyCT, self).change_prod_qty()
        for quality_checks in self.mo_id.check_ids:
            quality_checks.quality_state = 'none'
        return res