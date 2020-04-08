# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    import_ref = fields.Char(string=u"Import ref")
    import_old_ref = fields.Char(string=u"Import old ref")

    # # TODO : A TESTER
    # @api.model
    # def cron_import_ref_order(self):
    #     # TRANSFERT IMPORT REF IN NAME
    #     order_ids = self.env['sale.order'].search([('import_ref','!=',False)])
    #     #partner_ids = self.env['res.partner'].search([('id','=',989)])
    #     for order in order_ids:
    #         if order.import_ref:
    #             order.name = order.import_ref
    #
    #     return True
