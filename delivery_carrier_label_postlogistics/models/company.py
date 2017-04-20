# -*- coding: utf-8 -*-
# Copyright 2013-2017 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import file_open


class ResCompany(models.Model):
    _inherit = 'res.company'

    postlogistics_wsdl_url = fields.Char(compute='_compute_wsdl_url',
                                         string='WSDL URL',
                                         store=True)
    postlogistics_test_mode = fields.Boolean()
    postlogistics_username = fields.Char('Username')
    postlogistics_password = fields.Char('Password')
    postlogistics_license_ids = fields.One2many(
        comodel_name='postlogistics.license',
        inverse_name='company_id',
        string='PostLogistics Franking License',
    )
    postlogistics_logo = fields.Binary(
        string='Company Logo on Post labels',
        help="Optional company logo to show on label.\n"
             "If using an image / logo, please note the following:\n"
             "– Image width: 47 mm\n"
             "– Image height: 25 mm\n"
             "– File size: max. 30 kb\n"
             "– File format: GIF or PNG\n"
             "– Colour table: indexed colours, max. 200 colours\n"
             "– The logo will be printed rotated counter-clockwise by 90°"
             "\n"
             "We recommend using a black and white logo for printing in "
             " the ZPL2 format.",
        )
    postlogistics_office = fields.Char(
        string='Domicile Post office',
        help="Post office which will receive the shipped goods"
    )

    postlogistics_default_label_layout = fields.Many2one(
        comodel_name='delivery.carrier.template.option',
        string='Default label layout',
        domain=[('postlogistics_type', '=', 'label_layout')],
    )
    postlogistics_default_output_format = fields.Many2one(
        comodel_name='delivery.carrier.template.option',
        string='Default output format',
        domain=[('postlogistics_type', '=', 'output_format')],
    )
    postlogistics_default_resolution = fields.Many2one(
        comodel_name='delivery.carrier.template.option',
        string='Default resolution',
        domain=[('postlogistics_type', '=', 'resolution')],
    )
    postlogistics_tracking_format = fields.Selection(
        [('postlogistics', "Use default postlogistics tracking numbers"),
         ('picking_num', 'Use picking number with pack counter')],
        string="Tracking number format",
        default='postlogistics',
    )
    postlogistics_proclima_logo = fields.Boolean('Print ProClima logo')

    @api.depends('postlogistics_test_mode')
    def _compute_wsdl_url(self):
        path = 'delivery_carrier_label_postlogistics/data/'
        filename = 'barcode_v2_2_wsbc.wsdl'
        wsdl_file, wsdl_path = file_open(
            path + 'production/' + filename,
            pathinfo=True)
        wsdl_url = 'file://' + wsdl_path
        wsdl_file, wsdl_path_int = file_open(
            path + 'integration/' + filename,
            pathinfo=True)
        wsdl_int_url = 'file://' + wsdl_path_int
        for cp in self:
            if cp.postlogistics_test_mode:
                cp.postlogistics_wsdl_url = wsdl_int_url
            else:
                cp.postlogistics_wsdl_url = wsdl_url
