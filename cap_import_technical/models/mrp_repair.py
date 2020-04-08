# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MrpRepaire(models.Model):
    _inherit = "mrp.repair.line"

    import_support_allowed = fields.Char(string=u"Import support allowed")


class MrpRepaire(models.Model):
    _inherit = "mrp.repair"
    
    import_ref = fields.Char(string=u"Import ref")
    import_old_ref = fields.Char(string=u"Import old ref")
    date_creation_import = fields.Datetime(string=u"Date création import")
    commande_generee = fields.Char(string=u"Commande generee")
    avoir_genere = fields.Char(string=u"avoir_genere")


    @api.model
    def cron_import_data_repair(self):
        print "cron_import_data_repair"
        # CALL COMPUTE METHOD TO SUPPORT ALLOWED
        repair_ids = self.env['mrp.repair'].search([('import_ref', '!=', False)])
        for repair in repair_ids:

            vals = {'request_date_return':repair.date_creation_import,'receipt_date_return':repair.date_creation_import,
                    'name':repair.import_ref}
            if repair.date_start_workshop:
                vals['state'] = "done"

            repair.update(vals)

            for line in repair.operations:
                if not line.support_allowed:
                    line._compute_support_allowed()
            self._cr.commit()

        return True