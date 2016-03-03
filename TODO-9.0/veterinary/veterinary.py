# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields,api, _
from datetime import datetime
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
from openerp import tools

class specie (models.Model):
    
    _name='veterinary.specie'
    
    name = fields.Char('Name', size=128, required=True)
    scientific_name = fields.Char('Scientific Name', size=128)
    breed_ids = fields.One2many('veterinary.breed','specie_id', string='Breed')
    
            
class breed(models.Model):
    
    _name='veterinary.breed'
    _rec_name='breed_name'
    
    breed_name = fields.Char('Name', size=128, required=True)
    scientific_name = fields.Char('Scientific Name', size=128)
    specie_id = fields.Many2one('veterinary.specie', string='Specie',required=True)

class patient(models.Model):
    
    _name='veterinary.patient'
    _order='patient_name asc'
    _rec_name= 'patient_name'
    
    @api.one
    @api.depends('brith_date')
    def _compute_age (self):
        ageaux = 0.0
        if self.brith_date:
            date = datetime.strptime(self.brith_date,'%Y-%m-%d')
            delta = datetime.now() - date
            ageaux = delta.days / 365.00
        self.age = ageaux
            
    @api.one
    @api.depends('relative_ids')
    def _get_parents(self):
               patient_obj = self.env['veterinary.patient']
               self._cr.execute('SELECT id FROM veterinary_patient where veterinary_patient.id in'\
                                '(select veterinary_patient.parent_id_father from  public.veterinary_patient'\
                                ' where veterinary_patient.id = %s UNION ALL (SELECT id FROM veterinary_patient '\
                                'where veterinary_patient.id in '\
                                '(select veterinary_patient.parent_id_mother from  public.veterinary_patient '\
                                'where veterinary_patient.id = %s )))',(self.id,self.id))
               relaIds = self._cr.fetchall()
               result = patient_obj.search([('id','in',relaIds)])
               self.relative_ids = result

    @api.one
    @api.depends('active')
    def _compute_active_view(self):
        self.active_view = not self.active

    @api.one
    def _compute_responsible(self):
        self.responsible_id =self.env['res.partner']
        if self.partner_id:
            for child in self.partner_id.child_ids:
                if child.responsible:
                    self.responsible_id = child

    patient_name = fields.Char('Patient', size=128, required=True)
    brith_date = fields.Date ('Birth Date')    
    age = fields.Float('Age', compute='_compute_age', digits=(16,1))
    pure_breed = fields.Boolean('Pure Breed')
    gender = fields.Selection([('male','Male'),('female','Female')], 
                              string='Gender', default='male')
    state = fields.Selection([('healthy','Healthy'),('sick','Sick')], 
                             string='State', default='healthy')
    pedrigree = fields.Char('Pedigree',size=64)
    food = fields.Text(' ')
    castreded = fields.Boolean('Castreded')
    weight = fields.Float('Weight')
    specie_id = fields.Many2one('veterinary.specie', string='Specie', required=True)
    breed_id = fields.Many2one('veterinary.breed', string='Breed')    
    product_uom_id = fields.Many2one('product.uom', string=' ')    
    partner_id = fields.Many2one ('res.partner', string='Family', required=True)
    medical_history = fields.Text('Medical History')
    parent_id_father = fields.Many2one('veterinary.patient',string='Father')
    parent_id_mother = fields.Many2one('veterinary.patient',string='Mother')
    relative_ids = fields.One2many('veterinary.patient','parent_id_father', compute='_get_parents')
    height = fields.Float('Height')
    image = fields.Binary('Photo')
    colors_id = fields.Many2one('patient.color', string='Color')
    active_view = fields.Boolean('Deceased', compute='_compute_active_view', inverse='_inverse_active_view')
    active = fields.Boolean('Dead', default=True)
    laboratory_id = fields.Many2one('veterinary.laboratory', string='Test')
    responsible_id = fields.Many2one('res.partner' , compute='_compute_responsible', string='Responsible')


    @api.one
    def _inverse_active_view(self):
        self.active = not self.active_view

    @api.multi
    def patient_healthy (self):
        self.write({'state':'healthy'})
        
    @api.multi
    def patient_sick (self):
        self.write({'state':'sick'})
        
    @api.onchange('pure_breed')
    def onchange_pure_breed(self):
        self.pedrigree=''
        
    @api.constrains('specie_id','breed_id')
    def check_breed_id(self):
        if self.breed_id not in self.specie_id.breed_ids:
            raise Warning('Breed does not belong to Specie')
        return True
    
    @api.constrains('medical_history')
    def check_medical_history(self): # function for verify the field medical history is not empty
        if not self.medical_history:
            raise Warning (_('The camp Medical History does not empty'))
        return True


class laboratory_test(models.Model):
    _name = 'veterinary.laboratory'
    
    name = fields.Char('Name of test', size=128)
    date = fields.Datetime('Date Test', required=True)
    date_provided = fields.Date('Date of Result')
    patient_id = fields.Many2one('veterinary.patient' , string='Patient', required=True)
    sumary = fields.Text('Sumary test', required=True)
    
class patient_color(models.Model):
    
    _name = 'patient.color'
    _rec_name= 'name'
    
    name = fields.Char('Color')
    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    responsible = fields.Boolean('Responsible')
    
    @api.constrains('responsible')
    def _check_something(self):
        count = 0
        if self.parent_id:
            for child in self.parent_id.child_ids:
                if child.responsible:
                    count += 1
            if count > 1:
                raise Warning(_('Only one responsible per family is allowed.'))