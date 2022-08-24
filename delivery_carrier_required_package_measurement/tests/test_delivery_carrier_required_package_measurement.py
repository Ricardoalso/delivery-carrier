# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.stock.tests.test_packing import TestPackingCommon


class TestStockPickingPackageMeasurement(TestPackingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_aw = cls.env["product.product"].create(
            {
                "name": "Product AW",
                "type": "product",
                "weight": 2.4,
                "uom_id": cls.uom_kg.id,
                "uom_po_id": cls.uom_kg.id,
            }
        )
        test_carrier_product = cls.env["product.product"].create(
            {
                "name": "Test carrier product",
                "type": "service",
            }
        )
        cls.test_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "delivery_type": "fixed",
                "product_id": test_carrier_product.id,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_aw, cls.stock_location, 20.0
        )
        cls.pick = cls.env["stock.picking"].create(
            {
                "partner_id": cls.env["res.partner"].create({"name": "A partner"}).id,
                "picking_type_id": cls.warehouse.out_type_id.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "carrier_id": cls.test_carrier.id,
            }
        )
        cls.env["stock.move.line"].create(
            {
                "product_id": cls.product_aw.id,
                "product_uom_id": cls.uom_kg.id,
                "picking_id": cls.pick.id,
                "qty_done": 5,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.pick.action_confirm()

    def test_required_measurement_are_set(self):
        """Check required measurement are fullfilled on validation."""
        pack_action = self.pick.action_put_in_pack()
        pack_action_ctx = pack_action["context"]
        pack_wiz = (
            self.env["choose.delivery.package"].with_context(pack_action_ctx).create({})
        )
        pack_wiz.action_put_in_pack()

        package = self.pick.move_line_ids.mapped("result_package_id")
        # No measurement required
        self.assertTrue(self.pick._check_required_package_measurement())
        # Test length required
        self.test_carrier.package_length_required = True
        self.assertFalse(self.pick._check_required_package_measurement())
        package.pack_length = 55
        self.assertTrue(self.pick._check_required_package_measurement())
        # And also width is required
        self.test_carrier.package_width_required = True
        self.assertFalse(self.pick._check_required_package_measurement())
        package.width = 25
        self.assertTrue(self.pick._check_required_package_measurement())
