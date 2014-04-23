#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : OKF - Spending Stories
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU General Public License
# -----------------------------------------------------------------------------
# Creation : 05-Aug-2013
# Last mod : 19-Aug-2013
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


from django.utils.translation import ugettext as _
from django.conf import settings
from webapp.currency.models import Currency
from django.template.defaultfilters import slugify
from django.db import models
import fields
import datetime
import inflation

YEAR_CHOICES = []
for r in range(1999, (datetime.datetime.now().year + 1)):
    YEAR_CHOICES.append((r,r))

STORY_TYPES = (('discrete', _('discrete')), ('over_one_year', _('over one year')))

# -----------------------------------------------------------------------------
#
#    THEMES
#
# -----------------------------------------------------------------------------
class ThemeManager(models.Manager):
    """
    Manager for Stories
    """
    def public(self):
        return self.get_query_set().filter(active=True)


class Theme(models.Model):
    title       = models.CharField(max_length=80)
    slug        = models.SlugField(primary_key=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    image       = models.FileField(_("theme's image"), upload_to="themes", max_length=300, null=True, blank=True)
    active      = models.BooleanField(default=True)
    # managers
    objects     = ThemeManager()

    class Meta:
        ordering = ("slug",)

    def __unicode__(self):
        return self.title

    def image_tag(self):
        return u'<img src="%s" />' % self.image.url
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def save(self, *args, **kwargs):
        # Newly created object, so set slug
        if not self.slug:
            self.slug = slugify(self.title)
        # Remove the disabled theme from stories
        if self.active is False:
            for story in self.story_set.all():
                story.themes.remove(self)
        super(Theme, self).save(*args, **kwargs)

# -----------------------------------------------------------------------------
#
#    STORY
#
# -----------------------------------------------------------------------------
class StoryManager(models.Manager):
    """
    Manager for Stories
    """
    def public(self):
        return self.get_query_set().exclude(status__in=('refused', 'pending'))

class Story(models.Model):
    '''
    The model representing a spending
    '''
    value               = models.FloatField(_('The spending value'),help_text=_("Insert round numbers without any space or separator. e.g.222109000.You can also use the scientific notation. e.g.222.109e6")) # The spending amount
    title               = models.CharField(_('Story title'), max_length=240)
    description         = models.TextField(_('Story description'), blank=True, null=True)
    country             = fields.CountryField(_('Country'),help_text=_("Choose the country or zone where the money is spent")) # ISO code of the country 
    source              = models.URLField(_('Story\'s source URL'), max_length=140)
    currency            = models.ForeignKey(Currency)
    type                = models.CharField(_("Story type"), choices=STORY_TYPES, default    ='discrete', help_text  =_("The way you want that we compare this story. If this story's amount concerns a buget or a spending over one specific year, choose \"over one year\" (The amount will be cut into time equivalence)."), max_length =15)
    status              = models.CharField(_("status"), choices=(('pending', _('pending')), ('published', _('published')), ('refused', _('refused'))), default='pending', max_length=9)
    sticky              = models.BooleanField(_('Is a top story'),help_text=_("Check if the story is a tabloid"),default=False)
    year                = models.IntegerField(_('Year'), choices=YEAR_CHOICES, max_length=4, help_text=_("Enter the start year of the spending"))
    themes              = models.ManyToManyField(Theme, limit_choices_to = {'active':True})
    extras              = models.TextField(_("Extra informations in json format"), default="{}")
    # auto computed
    created_at          = models.DateTimeField(auto_now_add=True, editable=False)
    current_value       = models.FloatField(_('The current value with the inflation'), editable=False)
    current_value_usd   = models.FloatField(_('Current value in USD'), editable=False)
    inflation_last_year = models.IntegerField(max_length=4, editable=False)
    lang                = models.CharField(_('Story language'), max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    # managers
    objects             = StoryManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = "stories"

    def set_current_value(self):
        self.country = "ESP"
        inflation_amount, inflation_year = inflation.get_inflation(amount=self.value, year=self.year, country=self.country)
        self.current_value       = inflation_amount
        self.inflation_last_year = inflation_year
        self.current_value_usd   = self.current_value / self.currency.rate

    def save(self, *args, **kwargs):
        '''
        save in database
        '''
        try:
            previous_instance = Story.objects.get(pk=self.pk)
        except:
            previous_instance = None
        # Serialize the value in USD with the closest inflation 
        # if `year`, `value` or `currency` have changed, 
        # we recompute `current_value`, `current_value_usd` and `inflation_last_year`
        if not self.current_value_usd \
        or previous_instance.value    != self.value \
        or previous_instance.currency != self.currency \
        or previous_instance.year     != self.year:
            self.set_current_value()
        super(Story, self).save(*args, **kwargs)

# -----------------------------------------------------------------------------
#
#    PAGE
#
# -----------------------------------------------------------------------------
class Page(models.Model):
    title   = models.CharField(_('Page title'), max_length=240)
    slug    = models.SlugField(_('Page slug'), max_length=240)
    content = models.TextField(_('Page content'))

    def save(self, *args, **kwargs):
        # Newly created object, so set slug
        if not self.slug:
            self.slug = slugify(self.title)
        super(Page, self).save(*args, **kwargs)

# EOF
