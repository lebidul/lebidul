from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from django.db import models
from .models.evenement import Evenement, EvenementViewSet

register_snippet(Evenement, viewset=EvenementViewSet)

@register_setting(icon='form')
class FormulaireSettings(BaseSiteSetting):
    class Meta:
        verbose_name = 'Formulaire evenements'
    intro_text = models.TextField(default='Vous etes un groupe, un tourneur, un bar, une salle de concert et souhaitez annoncer un evenement dans le Bidul ? Remplissez ce formulaire.', verbose_name='Texte introduction')
    help_email = models.CharField(max_length=300, blank=True, default='Email a contacter en cas de question.', verbose_name='Aide champ email')
    help_date = models.CharField(max_length=300, blank=True, default='Date de l evenement.', verbose_name='Aide champ date')
    help_heure = models.CharField(max_length=300, blank=True, default='Exemple : 20h30', verbose_name='Aide champ heure')
    help_lieu = models.CharField(max_length=300, blank=True, default='Selectionnez le lieu ou proposez-en un nouveau.', verbose_name='Aide champ lieu')
    help_prix = models.CharField(max_length=300, blank=True, default='Gratuit, prix libre, 10 EUR...', verbose_name='Aide champ prix')
    show_description = models.BooleanField(default=True, verbose_name='Afficher Description')
    show_date_fin = models.BooleanField(default=True, verbose_name='Afficher Date fin')
    show_heure_fin = models.BooleanField(default=True, verbose_name='Afficher Heure fin')
    show_categorie = models.BooleanField(default=True, verbose_name='Afficher Categorie')
    show_url = models.BooleanField(default=True, verbose_name='Afficher Lien web')
    panels = [
        MultiFieldPanel([FieldPanel('intro_text')], heading='Introduction'),
        MultiFieldPanel([FieldPanel('help_email'),FieldPanel('help_date'),FieldPanel('help_heure'),FieldPanel('help_lieu'),FieldPanel('help_prix')], heading='Descriptions'),
        MultiFieldPanel([FieldPanel('show_description'),FieldPanel('show_date_fin'),FieldPanel('show_heure_fin'),FieldPanel('show_categorie'),FieldPanel('show_url')], heading='Champs optionnels'),
    ]
