# Copyright 2019 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase


class TestDeliveryFreeFeeRemoval(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestDeliveryFreeFeeRemoval, cls).setUpClass()

        product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        product_delivery = cls.env["product.product"].create(
            {"name": "Delivery Product", "type": "service"}
        )
        cls.delivery = cls.env["delivery.carrier"].create(
            {
                "name": "Delivery",
                "delivery_type": "fixed",
                "fixed_price": 10,
                "free_over": True,
                "product_id": product_delivery.id,
            }
        )
        partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "product_uom": product.uom_id.id,
                            "price_unit": 3.0,
                        },
                    )
                ],
            }
        )
        # Get the product in stock
        stock_inventory = cls.env["stock.inventory"].create(
            {
                "name": "Stock Inventory",
                "product_ids": [(4, product.id)],
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_id": product.uom_id.id,
                            "product_qty": 12,
                            "location_id": cls.env.ref("stock.stock_location_14").id,
                        },
                    )
                ],
            }
        )
        stock_inventory._action_start()
        stock_inventory.action_validate()

    def test_delivery_free_fee_removal_with_fee(self):
        self.sale.set_delivery_line(self.delivery, 100)
        delivery_line = self.sale.mapped("order_line").filtered(lambda x: x.is_delivery)
        self.sale.action_confirm()
        self.assertRecordValues(
            delivery_line, [{"is_free_delivery": False, "qty_to_invoice": 1}]
        )
        self.deliver_and_invoice_order(self.sale)

    def test_delivery_free_fee_removal_free_fee(self):
        self.sale.set_delivery_line(self.delivery, 0)
        delivery_line = self.sale.mapped("order_line").filtered(lambda x: x.is_delivery)
        self.sale.action_confirm()
        self.assertRecordValues(
            delivery_line, [{"is_free_delivery": True, "qty_to_invoice": 0}]
        )
        self.deliver_and_invoice_order(self.sale)

    def deliver_and_invoice_order(self, order):
        """Check delivery line state for invoicing and delivery."""
        # Deliver the order
        picking = order.picking_ids
        self.assertEqual(picking.state, "assigned")
        picking.move_line_ids[0].qty_done = 1.0
        picking.action_done()
        self.assertEqual(picking.state, "done")
        # Invoice the order
        self.wizard_obj = self.env["sale.advance.payment.inv"]
        wizard = self.wizard_obj.with_context(
            active_ids=order.ids, active_model=order._name
        ).create({})
        wizard.create_invoices()
        self.assertTrue(order.invoice_ids)
        # Check delivery lines are properly invoiced and delivered
        fee_line = order.order_line.filtered("is_delivery")
        self.assertEqual(fee_line.invoice_status, "invoiced")
        # Check the order is fully invoiced
        self.assertEqual(self.sale.invoice_status, "invoiced")
