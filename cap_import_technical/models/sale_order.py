# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    import_description = fields.Text(string=u"Description Import")

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    import_ref = fields.Char(string=u"Import ref")
    import_state = fields.Char(string=u"Import state")
    import_old_ref = fields.Char(string=u"Import old ref")
    import_old_ref_payment = fields.Char(string=u"Import old ref paiement")


    # TODO : A TESTER
    @api.model
    def cron_import_order(self):
        print "cron_import_order"
        # TRANSFERT IMPORT REF IN NAME & confirmation commande
        order_ids = self.env['sale.order'].search([('import_ref','!=',False),('state','!=','done')])
        for order in order_ids:
            for line in order.order_line:
                name_line = line.import_description if line.import_description else line.name
                categ_fdp_id = self.env['product.category'].search([('name','=','Frais de port')],limit=1)
                is_delivery = 1 if line.product_id.categ_id == categ_fdp_id else 0
                self._cr.execute("UPDATE sale_order_line SET state=%s,name=%s,is_delivery=%s WHERE id=%s",('done',name_line,str(is_delivery),line.id))

            self._cr.execute("UPDATE sale_order SET state=%s,name=%s,display_name=%s,confirmation_date=%s,payment_term_id=1 WHERE id=%s",('done', order.import_ref,order.import_ref,
                                                                                                                                                    order.date_order,order.id))
        return True