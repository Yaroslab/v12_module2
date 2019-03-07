# coding: utf-8

from odoo import fields
from odoo.tests import common
from odoo.tests.common import Form
from odoo.tests.common import SavepointCase


@common.post_install(True)
class TestAccountChangeByType(SavepointCase):

    @classmethod
    def setUpClass(self):
        super(TestAccountChangeByType, self).setUpClass()
        self.account_change_by_type_model = self.env['account.change.by.type']
        self.res_users = self.env['res.users']
        self.account_invoice_line_model = self.env['account.invoice.line']
        self.currency_id_usd = self.env['res.currency'].search([('name', '=', 'USD')])

        self.sale_account_id = self.env['account.account'].create({
            'code': '089000-T',
            'name': 'Test sale  Account',
            'user_type_id': self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.sale_account_id2 = self.env['account.account'].create({
            'code': '014200-T',
            'name': 'Test sale 2 Account',
            'user_type_id': self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.purchase_account_id = self.env['account.account'].create({
            'code': '957000-T',
            'name': 'Test purchase Account',
            'user_type_id': self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.product_uom = self.env['uom.uom'].create({
            'name': '3 units',
            'category_id': self.uom_unit.category_id.id,
            'factor_inv': 3,
            'rounding': 1,
            'uom_type': 'bigger',
        })
        self.currency_id_pen = self.env['res.currency'].create({
            'name': 'SOL',
            'symbol': 'S/.'
        })
        self.pricelist_id = self.env['product.pricelist'].create({
            'name': 'Priceslist - prueba',
            'currency_id': self.currency_id_pen.id,
        })
        self.partner_id = self.env['res.partner'].create({
            'name': "Pedro",
            'property_product_pricelist': self.pricelist_id.id,
        })

        self.company_id = self.env['res.company'].search([], limit=1)
        self.supplier_id = self.env['res.partner'].create({
            'name': "Empresa - TEC",
            'supplier': True,
            'customer': False
        })
        self.product_id = self.env['product.product'].create({
            'name': "Laptop hp",
            'lst_price': 124,
            'uom_id': self.product_uom.id
        })
        self.journal_id_pen = self.env['account.journal'].create({
            'name': 'Diario Venta SOL- Prueba',
            'type': 'sale',
            'code': 'TestS',
            'sequence_number_next': 50,
            'update_posted': True,
            'currency_id': self.currency_id_pen.id
        })
        self.journal_id_usd = self.env['account.journal'].create({
            'name': 'Diario Venta USD- Prueba',
            'type': 'sale',
            'code': 'TestD',
            'sequence_number_next': 50,
            'update_posted': True,
            'currency_id': self.currency_id_usd.id
        })

    def create_account_change_by_type(self, journal_id, currency_id, sale_account_id, purchase_account_id, company_id):
        account = self.account_change_by_type_model.create({
            'journal_id': journal_id,
            'currency_id': currency_id,
            'sale_account_id': sale_account_id,
            'purchase_account_id': purchase_account_id,
            'company_id': company_id
        })
        return account

    def create_invoice_from_wizard_sale(self, sale_order, type_wizard):
        sale_order.action_confirm()
        wizard = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': type_wizard
        })
        if type_wizard == 'percentage':
            wizard.amount = 10.0
        context = {
            "active_model": 'sale.order',
            "active_ids": [sale_order.id],
            "active_id": sale_order.id
        }
        # create invoice from sale order
        wizard.with_context(context).create_invoices()
        return sale_order.invoice_ids

    def test_01_create_account_change_by_type(self):
        account = self.create_account_change_by_type(
            journal_id=self.journal_id_pen.id, currency_id=self.currency_id_pen.id, company_id=self.company_id.id,
            sale_account_id=self.sale_account_id.id, purchase_account_id=self.purchase_account_id.id
        )
        self.assertTrue(account)
        print('------------TEST OK - YAROS ------------')

    def test_02_onchange_journal_id_sale_purchase(self):
        # create a record
        account_change = self.create_account_change_by_type(
            journal_id=self.journal_id_pen.id, currency_id=self.currency_id_pen.id, company_id=self.company_id.id,
            sale_account_id=self.sale_account_id.id, purchase_account_id=self.purchase_account_id.id
        )

        # set up invoice - sale
        invoice_form_sale = Form(self.env['account.invoice'], view='account.invoice_form')
        invoice_form_sale.journal_id = self.journal_id_pen
        invoice_form_sale.currency_id = self.currency_id_pen
        self.assertEqual(account_change.sale_account_id, invoice_form_sale.account_id)
        print('------------TEST OK - YAROS ------------')

        # set up invoice - purchase
        invoice_form_purchase = Form(self.env['account.invoice'], view='account.invoice_supplier_form')
        invoice_form_purchase.type = 'in_invoice'
        invoice_form_purchase.journal_id = self.journal_id_pen
        invoice_form_purchase.currency_id = self.currency_id_pen
        self.assertEqual(account_change.purchase_account_id, invoice_form_purchase.account_id)
        print('------------TEST OK - YAROS ------------')

    def test_03_update_onchange_account_id_before_validate(self):
        # create a record
        account_change = self.create_account_change_by_type(
            journal_id=self.journal_id_pen.id, currency_id=self.currency_id_pen.id, company_id=self.company_id.id,
            sale_account_id=self.sale_account_id.id, purchase_account_id=self.purchase_account_id.id
        )
        # set up invoice - sale
        invoice_form_sale = Form(self.env['account.invoice'], view='account.invoice_form')
        invoice_form_sale.journal_id = self.journal_id_pen
        invoice_form_sale.currency_id = self.currency_id_pen
        invoice_form_sale.partner_id = self.partner_id

        self.assertEqual(account_change.sale_account_id, invoice_form_sale.account_id)
        invoice = invoice_form_sale.save()
        self.account_invoice_line_model.create({
            'product_id': self.product_id.id,
            'quantity': 3,
            'price_unit': 1000,
            'invoice_id': invoice.id,
            'name': 'product that cost ' + str(1000),
            'account_id': self.env['account.account'].search([
                ('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)], limit=1).id,
        })

        account_change.sale_account_id = self.sale_account_id2.id
        invoice.action_invoice_open()
        self.assertEqual(account_change.sale_account_id, invoice.account_id)
        print('------------TEST OK - YAROS -------------')

    def test_04_validate_onchange_from_sale_order(self):
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        account_change = self.create_account_change_by_type(
            journal_id=journal_id, currency_id=self.currency_id_pen.id, company_id=self.company_id.id,
            sale_account_id=self.sale_account_id.id, purchase_account_id=self.purchase_account_id.id
        )

        self.order_id = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })
        self.order_line_id = self.env['sale.order.line'].create({
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_uom_qty': 1200.0,
            'order_id': self.order_id.id,
        })

        self.order_id.action_confirm()
        # get invoices
        invoice = self.create_invoice_from_wizard_sale(self.order_id, 'delivered')
        self.assertEqual(account_change.sale_account_id, invoice.account_id)
        print('------------TEST OK - YAROS - ONCHANGE FROM SALE ORDER ------------')

    def test_05_validate_onchange_from_purchase_order(self):

        self.order_id = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id_pen.id
        })
        self.order_line_id = self.env['purchase.order.line'].create({
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_uom_qty': 2400.0,
            'order_id': self.order_id.id,
            'product_qty': 2,
            'product_uom': self.product_id.uom_id.id,
            'price_unit': 1200.0,
            'date_planned': fields.Date().today()
        })

        self.order_id.button_confirm()
        view = self.order_id.action_view_invoice()
        journal_id = self.env['account.invoice'].with_context(view['context']).default_get(['journal_id'])['journal_id']
        account_change = self.create_account_change_by_type(
            journal_id=journal_id, currency_id=self.currency_id_pen.id, company_id=self.company_id.id,
            sale_account_id=self.sale_account_id.id, purchase_account_id=self.purchase_account_id.id
        )
        invoice_form_sale = Form(self.env['account.invoice'].with_context(view['context']),
                                 view='account.invoice_supplier_form')
        invoice = invoice_form_sale.save()
        print('currency account: %s   || currency invoice: %s' % (account_change.currency_id, invoice.currency_id))
        print('journal account:  %s   || currency invoice: %s' % (account_change.journal_id, invoice.journal_id))
        print('account account:  %s   || account invoice:  %s' % (account_change.purchase_account_id, invoice.account_id))
        self.assertEqual(account_change.purchase_account_id, invoice.account_id)
        print('------------TEST OK - YAROS -  ONCHANGE FROM PURCHASE ORDER ------------')
