# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_required_package_measurement(self):
        self.ensure_one()
        if not self.carrier_id:
            return True
        carrier = self.carrier_id
        packages = self.move_line_ids.mapped("result_package_id")
        for package in packages:
            if carrier.package_height_required and not package.height:
                return False
            if carrier.package_length_required and not package.pack_length:
                return False
            if carrier.package_width_required and not package.width:
                return False
        return True

    def button_validate(self):
        for pick in self:
            if not pick._check_required_package_measurement():
                raise UserError(
                    _(
                        "Some destination package do not have the required measurement set."
                    )
                )
        return super().button_validate()
