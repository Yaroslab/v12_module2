# coding: utf-8

from odoo import api, fields, models
from odoo.exceptions import ValidationError


type_validation = [
    ('numbers', u'Numérico'),
    ('letters', u'Alfanumérico'),
    ('no_validation', u'Sin validación')
]


length_validation = [
    ('equal', u'Igual'),
    ('max', u'Hasta'),
    ('no_validation', u'Sin validación')
]


def _validate_long(word, length, validation_type, field_name):
    if word and validation_type:
        if validation_type == 'equal':
            if len(word) != length:
                return "- La cantidad de caracteres para el campo '%s' debe ser: %d \n" % \
                       (field_name, length)
        elif validation_type == 'max':
            if len(word) > length:
                return "- La cantidad de caracteres para el campo '%s' debe ser como máximo: %d \n" % \
                       (field_name, length)
    return ''


def _validate_word_structure(word, validation_type, field_name):

    special_characters = u'-°%&=~\\+?*^$()[]{}|@%#"/¡¿!:.,;'
    if word:
        if validation_type == 'numbers':
            if not word.isdigit():
                return "- El campo '%s' solo debe contener números.\n" % field_name
            else:
                total = 0
                for d in str(word):
                    total += int(d)
                if total == 0:
                    return "- El campo '%s' no puede contener solo ceros.\n" % field_name
        special = ''
        for letter in word:
            if letter in special_characters:
                special += letter
        if special != '':
            return "- El campo '%s' contiene caracteres no permitidos:  %s \n" % (field_name, special)
    return ''


class SaleDocumentType(models.Model):

    _name = 'sale.document.type'
    _description = "Tipo de documento de venta"

    name = fields.Char(
        string='Nombre',
        required=True
    )
    code = fields.Char(
        string=u'Código'
    )
    is_active = fields.Boolean(
        string='Activo',
        default=True
    )
    is_sale = fields.Boolean(
        string='Venta'
    )
    is_purchase = fields.Boolean(
        string='Compra'
    )
    prefix_long = fields.Integer(
        string='Longitud Serie'
    )
    prefix_length_validation = fields.Selection(
        selection=length_validation,
        string=u'Validacion Longitud Serie',
        default='no_validation'
    )
    prefix_validation = fields.Selection(
        selection=type_validation,
        string=u'Validación Serie',
        default='no_validation'
    )
    correlative_long = fields.Integer(
        string='Longitud Correlativo'
    )
    correlative_length_validation = fields.Selection(
        selection=length_validation,
        string=u'Validación Longitud Correlativo',
        default='no_validation'
    )
    correlative_validation = fields.Selection(
        selection=type_validation,
        string=u'Validación Correlativo',
        default='no_validation'
    )
    journal_purchase_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string=u'Compañía'
    )


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    sale_document_type_id = fields.Many2one(
        comodel_name='sale.document.type',
        string='Tipo de documento de venta'
    )

    @api.onchange('type')
    def _onchange_type(self):
        self.sale_document_type_id = False


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    type_document_id = fields.Many2one(
        comodel_name='sale.document.type',
        string='Tipo de documento'
    )
    error_dialog = fields.Text(
        compute="_compute_error_dialog",
        store=True,
        help='Campo usado para mostrar mensaje de alerta en el mismo formulario'
    )
    prefix_val = fields.Char(
        string='Serie'
    )
    suffix_val = fields.Char(
        string='Correlativo'
    )

    @api.onchange('type_document_id')
    def _onchange_type_document_id(self):
        if self.type_document_id and self.type_document_id.journal_purchase_id:
            self.journal_id = self.type_document_id.journal_purchase_id

    @api.multi
    @api.depends('type_document_id', 'prefix_val', 'suffix_val', 'type')
    def _compute_error_dialog(self):
        for rec in self:
            if rec.type in ['in_invoice', 'in_refund']:
                msg = ''
                if rec.type_document_id:
                    type_document_serie = rec.type_document_id.prefix_length_validation
                    type_document_correlative = rec.type_document_id.correlative_length_validation
                    msg += _validate_long(rec.prefix_val, rec.type_document_id.prefix_long, type_document_serie,
                                          'Serie')
                    msg += _validate_long(rec.suffix_val, rec.type_document_id.correlative_long,
                                          type_document_correlative, 'Correlativo')

                    msg += _validate_word_structure(rec.prefix_val, rec.type_document_id.prefix_validation, 'Serie')
                    msg += _validate_word_structure(rec.suffix_val, rec.type_document_id.correlative_validation,
                                                    'Correlativo')
                rec.error_dialog = msg

    @api.constrains('error_dialog', 'type')
    def _constrains_error_dialog(self):
        for rec in self:
            if rec.type in ['in_invoice', 'in_refund'] and rec.error_dialog:
                raise ValidationError('Debe resolver las siguientes requerimientos antes de guardar: \n %s' %
                                      rec.error_dialog)

    @api.model
    def create(self, values):
        if values.get('type') and values.get('type') in ['in_invoice', 'in_refund'] and values.get('prefix_val') and \
                values.get('suffix_val'):
            values['reference'] = values['prefix_val'] + values['suffix_val']
        return super(AccountInvoice, self).create(values)

    @api.multi
    def write(self, values):
        for rec in self:
            if rec.type in ['in_invoice', 'in_refund']:
                if values.get('prefix_val') and values.get('suffix_val'):
                    values['reference'] = values.get('prefix_val') + values.get('suffix_val')
                elif values.get('prefix_val') and not values.get('suffix_val'):
                    values['reference'] = values.get('prefix_val') + rec.suffix_val
                elif not values.get('prefix_val') and values.get('suffix_val'):
                    values['reference'] = rec.prefix_val + values.get('suffix_val')
        return super(AccountInvoice, self).write(values)

    @api.onchange('partner_id')
    def _onchange_partner_id_type_document_id(self):
        if self.partner_id and self.partner_id.type_document_id:
            self.type_document_id = self.partner_id.type_document_id
