# coding: utf-8

from odoo import api, fields, models, _


class AccountChangeByType(models.Model):

    _name = 'account.change.by.type'
    _description = u'Aquí se registra una relación entre el diario y la moneda que van a determinar la cuenta' \
                   u' por cobrar o pagar a utilizar en los documentos de venta o compra.'

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        required=True
    )
    sale_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta Venta',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    purchase_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta Compra',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string=u'Compañía',
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id
    )


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    document = fields.Many2one(comodel_name='account.change.by.type')
