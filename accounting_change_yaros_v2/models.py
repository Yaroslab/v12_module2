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

    @api.onchange('partner_id', 'company_id', 'journal_id', 'currency_id')
    def _onchange_partner_id(self):
        self.account_id = False
        if self.journal_id and self.currency_id:
            account_change = self.env['account.change.by.type'].search([
                ('journal_id', '=', self.journal_id.id),
                ('currency_id', '=', self.currency_id.id)
            ], limit=1)
            if account_change:
                if self.type == 'out_invoice':
                    self.account_id = account_change.sale_account_id.id
                elif self.type == 'in_invoice':
                    self.account_id = account_change.purchase_account_id.id
        if not self.account_id:
            return super(AccountInvoice, self)._onchange_partner_id()

    @api.multi
    def action_invoice_open(self):
        self._onchange_partner_id()
        return super(AccountInvoice, self).action_invoice_open()
