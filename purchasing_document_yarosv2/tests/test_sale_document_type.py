# coding: utf-8

from odoo.exceptions import AccessError
from odoo.tests import common
from odoo.tests.common import Form
from odoo.tests.common import SavepointCase


@common.post_install(True)
class TestSaleDocumentType(SavepointCase):

    @classmethod
    def setUpClass(self):
        super(TestSaleDocumentType, self).setUpClass()
        self.sale_document_type_model = self.env['sale.document.type']
        self.res_users = self.env['res.users']
        self.currency_id_pen = self.env['res.currency'].search([('name', '=', 'PEN')])
        self.currency_id_usd = self.env['res.currency'].search([('name', '=', 'USD')])

        self.sale_account_id = self.env['account.account'].search([('code', '=', '121100')])
        self.purchase_account_id = self.env['account.account'].search([('code', '=', '421100')])
        self.product_uom = self.env['uom.uom'].search([('name', '=', 'Dozen(s)')])

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
        self.document_attrs = {
            'code': '12',
            'name': 'DNI',
            'is_active': True,
            'is_sale': True,
            'is_purchase': False,
        }
        self.document_attrs_purchase = {
            'code': '1232',
            'name': 'RUC',
            'is_active': True,
            'is_sale': True,
            'is_purchase': True,
            'journal_purchase_id': self.journal_id_usd.id,
            'prefix_long': 4,
            'prefix_validation': 'numbers',
            'correlative_long': 5,
            'correlative_validation': 'letters'
        }
        self.supplier_id = self.env['res.partner'].create({
            'name': "Empresa - TEC",
            'supplier': True,
            'customer': False
        })
        self.product_id = self.env['product.product'].create({
            'name': "Laptop hp",
            'lst_price': 1124
        })

    def create_sale_document_type(self, **kwargs):
        sale_document = self.sale_document_type_model.create({
            'code': kwargs.get('code'),
            'name': kwargs.get('name'),
            'is_active': kwargs.get('is_active'),
            'is_sale': kwargs.get('is_sale'),
            'is_purchase': kwargs.get('is_purchase'),
        })
        if kwargs.get('is_purchase'):
            sale_document.update({
                'prefix_long': kwargs.get('prefix_long'),
                'prefix_validation': kwargs.get('prefix_validation'),
                'correlative_long': kwargs.get('correlative_long'),
                'correlative_validation': kwargs.get('correlative_validation'),
                'journal_purchase_id': kwargs.get('journal_purchase_id'),
                'company_id': kwargs.get('company_id')
            })
        return sale_document

    def create_res_users_by_group(self, groups, nro):
        user = self.res_users.create({
            'login': 'test_user%d' % nro,
            'name': 'Usuario%d - T' % nro,
            'email': 'usert%d@example.com' % nro,
            'notification_type': 'email',
            'groups_id': [(6, 0, groups)]
        })
        return user

    def test_01_create_sale_document_type(self):
        document1 = self.create_sale_document_type(**self.document_attrs)
        self.assertTrue(document1)

        print('------------TEST OK - CREATE------------')

    def test_02_sale_document_type_permissions(self):
        document = self.create_sale_document_type(**self.document_attrs)
        group_account_manager = self.env.ref('account.group_account_manager')

        # set a different user(account role) to prove permissions
        user_account = self.create_res_users_by_group([group_account_manager.id], 1)

        # should do
        document.sudo(user_account).read()
        document.sudo(user_account).write({'name': 'prueba - account'})
        document.sudo(user_account).unlink()

        print('------------TEST OK - USER ACCOUNT------------')

        # set a different user to prove permissions
        user = self.create_res_users_by_group([], 2)

        # shouldn't do
        self.assertRaises(AccessError, document.sudo(user).write, {'name': 'prueba - normal'})
        self.assertRaises(AccessError, document.sudo(user).unlink)

        # should do
        document.sudo(user).read()

        print('------------TEST OK - NORMAL USER------------')

    def test_03_onchange_invoice_purchase_document_type_validate_reference(self):
        invoice_form_purchase = Form(self.env['account.invoice'].with_context(type='in_invoice'),
                                     view='account.invoice_supplier_form')
        document = self.create_sale_document_type(**self.document_attrs_purchase)
        invoice_form_purchase.type_document_id = document
        self.assertEqual(invoice_form_purchase.journal_id, document.journal_purchase_id)

        print('------------TEST OK - ONCHANGE DOCUMENT INVOICE ------------')

        invoice_form_purchase.prefix_val = '1234'
        invoice_form_purchase.suffix_val = 'TST01'
        invoice = invoice_form_purchase.save()
        self.assertEqual(invoice.reference, invoice.prefix_val + invoice.suffix_val)

        print('------------TEST OK - REFERENCE FIELD-INVOICE PURCHASE------------')
