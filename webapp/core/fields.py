#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : OKF - Spending Stories
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU General Public License
# -----------------------------------------------------------------------------
# Creation : 08-Aug-2013
# Last mod : 08-Aug-2013
# -----------------------------------------------------------------------------
# This file is part of Spending Stories.
# 
#     Spending Stories is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     Spending Stories is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with Spending Stories.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models

# -----------------------------------------------------------------------------
#
#    CountryField
#
# -----------------------------------------------------------------------------
# - Took from http://djangosnippets.org/snippets/1281/
# - filtered for countries that are actually referenced into CPI dataset

COUNTRIES = (
    ('000', 'España (Gobierno de)'),
    ('001', 'Ciudades'),
    ('C01', 'Andalucía'),
    ('C02', 'Aragón'),
    ('C03', 'Asturias, Principado de'),
    ('C04', 'Baleares, Islas'),
    ('C05', 'Canarias'),
    ('C06', 'Cantabria'),
    ('C07', 'Castilla y León'),
    ('C08', 'Castilla-La Mancha'),
    ('C09', 'Cataluña'),
    ('C10', 'Comunidad Valenciana'),
    ('C11', 'Extremadura'),
    ('C12', 'Galicia'),
    ('C13', 'Madrid, Comunidad de'),
    ('C14', 'Murcia, Región de'),
    ('C15', 'Navarra, Comunidad Foral de'),
    ('C16', 'País Vasco'),
    ('C17', 'Rioja, La'),
    ('C18', 'Ceuta'),
    ('C19', 'Melilla'),
    ('P02', 'Albacete'),
    ('P03', 'Alicante/Alacant'),
    ('P04', 'Almería'),
    ('P01', 'Araba/Álava'),
    ('P33', 'Asturias'),
    ('P05', 'Ávila'),
    ('P06', 'Badajoz'),
    ('P07', 'Balears, Illes'),
    ('P08', 'Barcelona'),
    ('P48', 'Bizkaia'),
    ('P09', 'Burgos'),
    ('P10', 'Cáceres'),
    ('P11', 'Cádiz'),
    ('P39', 'Cantabria'),
    ('P12', 'Castellón/Castelló'),
    ('P13', 'Ciudad Real'),
    ('P14', 'Córdoba'),
    ('P15', 'Coruña, A'),
    ('P16', 'Cuenca'),
    ('P20', 'Gipuzkoa'),
    ('P17', 'Girona'),
    ('P18', 'Granada'),
    ('P19', 'Guadalajara'),
    ('P21', 'Huelva'),
    ('P22', 'Huesca'),
    ('P23', 'Jaén'),
    ('P24', 'León'),
    ('P25', 'Lleida'),
    ('P27', 'Lugo'),
    ('P28', 'Madrid'),
    ('P29', 'Málaga'),
    ('P30', 'Murcia'),
    ('P31', 'Navarra/Nafarroa'),
    ('P32', 'Ourense'),
    ('P34', 'Palencia'),
    ('P35', 'Palmas, Las'),
    ('P36', 'Pontevedra'),
    ('P26', 'Rioja, La'),
    ('P37', 'Salamanca'),
    ('P38', 'Santa Cruz de Tenerife'),
    ('P40', 'Segovia'),
    ('P41', 'Sevilla'),
    ('P42', 'Soria'),
    ('P43', 'Tarragona'),
    ('P44', 'Teruel'),
    ('P45', 'Toledo'),
    ('P46', 'Valencia/‘València'),
    ('P47', 'Valladolid'),
    ('P49', 'Zamora'),
    ('P50', 'Zaragoza'),
    ('P51', 'Ceuta'),
    ('P52', 'Melilla')
)

class CountryField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 3)
        kwargs.setdefault('choices', COUNTRIES)

        super(CountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^webapp\.core\.fields\.CountryField"])

# EOF
