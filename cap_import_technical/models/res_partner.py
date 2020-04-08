# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    import_ref = fields.Char(string=u"Import ref")
    import_old_ref = fields.Char(string=u"Import old ref")

    # TODO : A TESTER
    @api.model
    def cron_import_ref_partner(self):
        print "cron_import_ref_partner"
        # TRANSFERT IMPORT REF IN REF
        partner_ids = self.env['res.partner'].search([('import_ref','!=',False),('ref','=',False),('|'),('active','=',True),('active','=',False)])
        #partner_ids = self.env['res.partner'].search([('id','=',989)])
        print partner_ids
        for partner in partner_ids:
            print "START partner " + partner.import_ref
            partner.ref = partner.import_ref
            # CREATE COMPTE COMPTABLE
            partner.set_partner_fiscal_position()

            # INACTIVE CONTACT ET ADRESSE SI PARTNER INACTIF
            if not partner.active:
                for child in partner.child_ids:
                    child.active = False

            self._cr.commit()
            print "END partner " + partner.ref
                
        return True
