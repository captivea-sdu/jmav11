# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class MagentoConfigure(models.Model):
    _inherit = "magento.configure"

    last_id_export_magento = fields.Char('ID dernier objet exporter')
    error_id_export_magento = fields.Char('ID en erreur')

##########################################
# PRODUCT SYNC
    @api.model
    def cron_export_magento_product(self,error=False):
        if error:
            _logger.info("CRON CAPTIVEA : export product ERROR => magento")
        else:
            _logger.info("CRON CAPTIVEA : export product => magento")

        mag_conf_id = self.env['magento.configure'].search([],limit=1)
        if not mag_conf_id.error_id_export_magento:
            mag_conf_id.error_id_export_magento = ''

        # GESTION CRON PRODUCT SYNC IN ERROR
        str_error = mag_conf_id.error_id_export_magento.split("|")
        del str_error[0]
        erray = map(int, str_error)
        if error:
            str_ids = mag_conf_id.error_id_export_magento.split("|")
            del str_ids[0]
            product_ids = self.env['product.template'].browse(map(int, str_ids)).sorted(key=lambda p: p.id)
        else:
            cur_id = 0 if not mag_conf_id.last_id_export_magento else mag_conf_id.last_id_export_magento
            product_ids = self.env['product.template'].search([('id','>',cur_id), ('id','not in',erray),
                                                               ('|'), ('active', '=', False), ('active', '=', True)],order='id asc',limit=40)

            product_sync = self.env['magento.product.template'].search([('erp_template_id', 'in', product_ids.mapped('id'))])
            product_sync_ids = self.env['product.template'].browse(product_sync.mapped('erp_template_id'))
            product_ids -= product_sync_ids

            #  TRAITEMENT SPE si il reste des objets à traité, mais qui ne sont pas dans les 40 selectionné
            if not product_ids:
                _logger.debug("TRAITEMENT SPE si il reste des objets à traité")
                todo_product_ids = self.env['product.template'].search([('id', '>', cur_id),('id','not in',erray),
                                                                        ('|'), ('active', '=', False), ('active', '=', True)], order='id asc')
                product_sync = self.env['magento.product.template'].search([])
                product_sync_ids = self.env['product.template'].browse(product_sync.mapped('erp_template_id'))
                todo_product_ids -= product_sync_ids
                if todo_product_ids:
                    product_ids = self.env['product.template'].search([('id', '>=', todo_product_ids[0].id),('id','not in',erray),
                                                                  ('|'), ('active', '=', False), ('active', '=', True)], order='id asc', limit=40)

        _logger.debug(product_ids)

        # SOUSTRACTION DES PRODUIT DEJA SYNCHRO
        product_sync = self.env['magento.product.template'].search([('erp_template_id', 'in', product_ids.mapped('id'))])
        product_sync_ids = self.env['product.template'].browse(product_sync.mapped('erp_template_id'))
        product_ids -= product_sync_ids

        _logger.debug(product_ids)
        for product in product_ids:
            if error and not hasattr(product,'name'):
                _logger.info("NOT SYNC > OBJET NOT EXIST")
                mag_conf_id.error_id_export_magento = mag_conf_id.error_id_export_magento.replace('|' + str(product.id), '')
                continue

            _logger.info("CRON CAPTIVEA : export product => magento")
            ctx = dict(self._context or {})
            ctx.update({'active_model':'product.template','active_ids':[product.id],'sync_opr':'export'})
            res = self.env['magento.synchronization'].with_context(ctx).export_product_check()

            if not res:
                _logger.info("NOT SYNC > not connection")
                if not error:
                    mag_conf_id.error_id_export_magento += "|" + str(product.id)
                continue

            res_wiz = self.env['message.wizard'].browse(res['res_id'])
            _logger.info(res_wiz.text)
            # TEST IF SYNC IS NOT OK
            if "does not synchronized" in res_wiz.text:
                _logger.info("NOT SYNC")
                if not error:
                    mag_conf_id.error_id_export_magento += "|"+str(product.id)
            else:
                _logger.info("SYNC")
                if error:
                    mag_conf_id.error_id_export_magento = mag_conf_id.error_id_export_magento.replace('|' + str(product.id), '')
                    mag_conf_id.last_id_export_magento = 100000
                else:
                    mag_conf_id.last_id_export_magento = product.id

            self._cr.commit()

        if not product_ids:
            if mag_conf_id.error_id_export_magento:
                mag_conf_id.cron_export_magento_product(error=True)

        return True
##########################################
#  PARTNER SYNC
    @api.model
    def cron_export_magento_partner(self,error=False):
        if error:
            _logger.info("CRON CAPTIVEA : export partner ERROR => magento")
        else:
            _logger.info("CRON CAPTIVEA : export partner => magento")

        mag_conf_id = self.env['magento.configure'].search([],limit=1)
        if not mag_conf_id.error_id_export_magento:
            mag_conf_id.error_id_export_magento = ''

        # GESTION CRON PRODUCT SYNC IN ERROR
        if error:
            str_ids = mag_conf_id.error_id_export_magento.split("|")
            del str_ids[0]
            partner_ids = self.env['res.partner'].browse(map(int, str_ids)).sorted(key=lambda p: p.id)
        else:
            cur_id = 0 if not mag_conf_id.last_id_export_magento else mag_conf_id.last_id_export_magento
            partner_ids = self.env['res.partner'].search([('parent_id','=',False),('id','>',cur_id),
                                                          ('|'), ('active', '=', False), ('active', '=', True)],order='id asc',limit=80)

            partner_sync = self.env['magento.customers'].search([('oe_customer_id', 'in', partner_ids.mapped('id'))])
            product_sync_ids = self.env['res.partner'].browse(partner_sync.mapped('oe_customer_id'))
            partner_ids -= product_sync_ids

            #  TRAITEMENT SPE si il reste des objets à traité, mais qui ne sont pas dans les 40 selectionné
            if not partner_ids:
                todo_partner_ids = self.env['res.partner'].search([('parent_id','=',False),('id', '>', cur_id), ('|'), ('active', '=', False), ('active', '=', True)], order='id asc')
                partner_sync = self.env['magento.customers'].search([])
                partner_sync_ids = self.env['res.partner'].browse(partner_sync.mapped('oe_customer_id'))
                todo_partner_ids -= partner_sync_ids
                if todo_partner_ids:
                    partner_ids = self.env['res.partner'].search([('parent_id','=',False),('id', '>=', todo_partner_ids[0].id),
                                                                  ('|'), ('active', '=', False), ('active', '=', True)], order='id asc', limit=40)

        # SOUSTRACTION DES PRODUIT DEJA SYNCHRO
        partner_sync = self.env['magento.customers'].search([('oe_customer_id', 'in', partner_ids.mapped('id'))])
        product_sync_ids = self.env['res.partner'].browse(partner_sync.mapped('oe_customer_id'))
        partner_ids -= product_sync_ids

        _logger.info(partner_ids)
        for partner in partner_ids:
            if error and not hasattr(partner,'name'):
                _logger.info("NOT SYNC > OBJET NOT EXIST")
                mag_conf_id.error_id_export_magento = mag_conf_id.error_id_export_magento.replace('|' + str(partner.id), '')
                continue

            _logger.info("CRON CAPTIVEA : export partner => magento")
            ctx = dict(self._context or {})
            ctx.update({'active_model':'res.partner','active_ids':[partner.id],'sync_opr':'export'})
            res = self.env['magento.synchronization'].with_context(ctx).export_partner_check()
            if not res:
                _logger.info("NOT SYNC > not connection")
                if not error:
                    mag_conf_id.error_id_export_magento += "|" + str(partner.id)
                continue

            res_wiz = self.env['message.wizard'].browse(res['res_id'])
            _logger.info(res_wiz.text)

            # TEST IF SYNC IS NOT OK
            if "does not synchronized" in res_wiz.text:
                _logger.info("NOT SYNC")
                if not error:
                    mag_conf_id.error_id_export_magento += "|"+str(partner.id)
            else:
                _logger.info("SYNC")
                if error:
                    mag_conf_id.error_id_export_magento = mag_conf_id.error_id_export_magento.replace('|'+str(partner.id),'')
                    mag_conf_id.last_id_export_magento = 100000
                else:
                    mag_conf_id.last_id_export_magento = partner.id

            self._cr.commit()

        if not partner_ids:
            mag_conf_id.last_id_export_magento = 100000
            if mag_conf_id.error_id_export_magento:
                mag_conf_id.cron_export_magento_partner(error=True)

        return True

##########################################
#  ORDER SYNC
    @api.model
    def cron_export_magento_order(self,error=False):
        if error:
            _logger.info("CRON CAPTIVEA : export order ERROR => magento")
        else:
            _logger.info("CRON CAPTIVEA : export order => magento")

        mag_conf_id = self.env['magento.configure'].search([],limit=1)
        if not mag_conf_id.error_id_export_magento:
            mag_conf_id.error_id_export_magento = ''

        # GESTION CRON order SYNC IN ERROR
        if error:
            str_ids = mag_conf_id.error_id_export_magento.split("|")
            del str_ids[0]
            order_ids = self.env['sale.order'].browse(map(int, str_ids)).sorted(key=lambda p: p.id)
        else:
            cur_id = 0 if not mag_conf_id.last_id_export_magento else mag_conf_id.last_id_export_magento
            order_ids = self.env['sale.order'].search([('id','>',cur_id),('state','=','done')],order='id asc',limit=40)
            _logger.debug("START")
            _logger.debug(order_ids)
            order_sync = self.env['wk.order.mapping'].search([('erp_order_id', 'in', order_ids.mapped('id'))])
            order_sync_ids = order_sync.mapped('erp_order_id')
            order_ids -= order_sync_ids

            _logger.debug("BEFORE TRAITEMENT SPE")
            _logger.debug(order_ids)
            #  TRAITEMENT SPE si il reste des objets à traité, mais qui ne sont pas dans les 40 selectionné
            if not order_ids:
                _logger.debug("TRAITEMENT SPE si il reste des objets à traité")
                _logger.debug(order_ids)
                todo_order_ids = self.env['sale.order'].search([('id', '>', cur_id),('state','=','done')], order='id asc')
                order_sync = self.env['wk.order.mapping'].search([])
                order_sync_ids = order_sync.mapped('erp_order_id')
                todo_order_ids -= order_sync_ids
                _logger.debug("TODO ORDER")
                _logger.debug(todo_order_ids)
                if todo_order_ids:
                    _logger.debug("IN")
                    order_ids = self.env['sale.order'].search([('id', '>=', todo_order_ids[0].id),('state','=','done')],order='id asc', limit=40)

        _logger.debug("SELECT")
        _logger.debug(order_ids)
        # SOUSTRACTION DES COMMANDES DEJA SYNCHRO
        order_sync = self.env['wk.order.mapping'].search([('erp_order_id', 'in', order_ids.mapped('id'))])
        order_sync_ids = order_sync.mapped('erp_order_id')
        order_ids -= order_sync_ids

        _logger.debug(order_ids)
        for order in order_ids:
            if error and not hasattr(order,'name'):
                _logger.info("NOT SYNC > OBJET NOT EXIST")
                mag_conf_id.error_id_export_magento = mag_conf_id.error_id_export_magento.replace('|' + str(order.id), '')
                continue

            _logger.info("CRON CAPTIVEA : export order => magento")
            ctx = dict(self._context or {})
            ctx.update({'active_model':'sale.order','active_ids':[order.id],'sync_opr':'export'})
            res = self.env['magento.synchronization'].with_context(ctx).export_order_check()
            if not res:
                _logger.info("NOT SYNC > not connection")
                if not error:
                    mag_conf_id.error_id_export_magento += "|" + str(order.id)
                continue

            res_wiz = self.env['message.wizard'].browse(res['res_id'])
            _logger.info(res_wiz.text)

            # TEST IF SYNC IS NOT OK
            if "does not synchronized" in res_wiz.text:
                _logger.info("NOT SYNC")
                if not error:
                    mag_conf_id.error_id_export_magento += "|"+str(order.id)
            else:
                _logger.info("SYNC")
                if error:
                    mag_conf_id.error_id_export_magento = mag_conf_id.error_id_export_magento.replace('|'+str(order.id),'')
                    mag_conf_id.last_id_export_magento = 999999
                else:
                    mag_conf_id.last_id_export_magento = order.id

            self._cr.commit()

        if not order_ids:
            mag_conf_id.last_id_export_magento = 999999
            if mag_conf_id.error_id_export_magento:
                mag_conf_id.cron_export_magento_order(error=True)

        return True