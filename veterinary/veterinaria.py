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

from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class species (models.Model):

    _name = 'veterinaria.specie'

    name = fields.Char('Name', size=128)
    scientific_name = fields.Char('Scientific Name', size=128, help='The scientific name of the ...')
    breed_ids = fields.One2many('veterinaria.breed', 'specie_id' , string='Breed')

class breed (models.Model):
    
    _name = 'veterinaria.breed'
    _order = 'size asc'
    _rec_name = 'breed_name'

    breed_name = fields.Char('Name', size=128, required=True, help='The scientific name of the ...')
    scientific_name = fields.Char('Scientific Name', size=128)
    size = fields.Float('Size', digits=(16, 3))
    specie_id = fields.Many2one('veterinaria.specie', string='Specie', required=True)

class patient(models.Model):
    _name = 'veterinaria.patient'
    _order = 'name asc'

    @api.one
    @api.depends("birth_date")
    def _compute_age(self):
        age = 0.0
        if self.birth_date:
            date = datetime.strptime(self.birth_date, '%Y-%m-%d')
            delta = datetime.now() - date
            age = delta.days / 365.00
        self.age = age
        
    name = fields.Char('Name', size=128, required=True)
    birth_date = fields.Date('Birth Date', required=True)
    age = fields.Float('Age', compute='_compute_age', digits=(16, 2))
    purebred = fields.Boolean('Pure Breed')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', default='male')
    state = fields.Selection([('healthy', 'Healthy'), ('sick', 'Sick')], string='State', default='healthy')
    pedigree = fields.Char('Pedigree', size=64)
    food = fields.Text('Food')
    castreted = fields.Boolean('Castreted')
    specie_id = fields.Many2one('veterinaria.specie', string='Specie', ondelete='cascade', required=True)
    breed_id = fields.Many2one('veterinaria.breed', string='Breed')
    weight = fields.Float('Weight' , digits=(16, 2))
    product_uom_id = fields.Many2one('product.uom', string='Weight in units', required=True)
    family_id = fields.Many2one('veterinaria.family', string='Owner', required=True)
    medical_history = fields.Text('Medical History')
    partner_id = fields.Many2one ('res.partner', string='Family', required=True)
    


    @api.multi
    def patient_healthy(self):
        self.write({'state': 'healthy'})

    @api.multi
    def patient_sick(self):
        self.write({'state': 'sick'})
    @api.onchange('purebred')
    def onchange_pure_breed(self):
        self.pedigree = ''

    @api.constrains('specie_id','breed_id')
    def check_breed_id(self):
        if self.breed_id not in self.specie_id.breed_ids:
            raise Warning (_('Breed does not belong to species'))
        return True

    @api.constrains('medical_history')
    def check_medical_history(self):
        if not self.medical_history:
            raise Warning (_('The camp Medical History does not empty'))
        return True

class res_partner_family(models.Model):
        _name = 'veterinaria.family'
        
        name = fields.Char('Name')
        owner_ids = fields.Many2many('res.partner', string='Family')


class laboratory_test(models.Model):
    _name = 'veterinaria.laboratory'
    
    name = fields.Char('Name of test', size=128)
    date = fields.Datetime('Date Test', required=True)
    date_provided = fields.Datetime('Date of Result')
    patient_id = fields.Many2one('veterinaria.patient' , string='Patient', required=True)
    sumary = fields.Text('Sumary test', required=True)
