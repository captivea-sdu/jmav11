# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    import_ref = fields.Char(string=u"Import ref")
    import_old_ref = fields.Char(string=u"Import old ref")
    import_spe_oasis = fields.Boolean(string=u"Import special oasis")
    
    @api.model
    def cron_import_ref_product(self):
        #print "cron_import_ref_product"
        # TRANSFERT IMPORT REF IN REF
        product_ids = self.env['product.product'].search([('import_ref','!=',False),('|'),('active','=',True),('active','=',False)])
        for product in product_ids:
            if product.default_code:
                product.default_code = product.import_ref
            self._cr.commit()
                                
        return True

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    import_ref = fields.Char(string=u"Import ref")
    import_old_ref = fields.Char(string=u"Import old ref")
