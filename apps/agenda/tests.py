from datetime import date
from django.test import TestCase
from apps.agenda.models import Bidul, Evenement, Lieu
from apps.agenda.forms import EvenementForm
from apps.agenda.models.snippets import GoogleSheetMensuel


class BidulModelTest(TestCase):
    def setUp(self):
        self.bidul = Bidul.objects.create(numero=1, mois=2, annee=1997, date_publication=date(1997, 2, 1), nb_evenements=42)

    def test_creation(self):
        self.assertEqual(self.bidul.numero, 1)
        self.assertEqual(self.bidul.annee, 1997)

    def test_str(self):
        self.assertIn(str(self.bidul.numero), str(self.bidul))

    def test_date_publication(self):
        self.assertEqual(self.bidul.date_publication, date(1997, 2, 1))


class LieuModelTest(TestCase):
    def setUp(self):
        self.lieu = Lieu.objects.create(nom='L Oasis', slug='l-oasis', ville='Le Mans', code_postal='72000', actif=True)

    def test_creation(self):
        self.assertEqual(self.lieu.nom, 'L Oasis')
        self.assertEqual(self.lieu.ville, 'Le Mans')

    def test_str(self):
        self.assertIn('Oasis', str(self.lieu))

    def test_slug(self):
        self.assertEqual(self.lieu.slug, 'l-oasis')


class EvenementModelTest(TestCase):
    def setUp(self):
        self.lieu = Lieu.objects.create(nom='Theatre', slug='theatre', ville='Le Mans', code_postal='72000')
        self.evt = Evenement.objects.create(titre='Concert de jazz', slug='concert-jazz', date_debut=date(2026, 6, 15), lieu=self.lieu)

    def test_creation(self):
        self.assertEqual(self.evt.titre, 'Concert de jazz')

    def test_lieu_associe(self):
        self.assertEqual(self.evt.lieu.nom, 'Theatre')

    def test_str(self):
        self.assertIn('Concert', str(self.evt))


class EvenementFormTest(TestCase):
    """Tests du formulaire /annoncer/ - regression sur le bug 'titre requis'."""

    def setUp(self):
        self.lieu = Lieu.objects.create(nom='ENSIM', slug='ensim', ville='Le Mans', code_postal='72000', actif=True)
        self.valid_data = {
            'email_contact': 'test@test.com',
            'date_debut': '2026-10-19',
            'heure_text': '20h30',
            'lieu': self.lieu.id,
            'ville': 'Le Mans',
            'tarif': '8 EUR',
            'url': '',
            'festival_nom': 'Festival Test',
            'festival_style': 'rock',
            'genre_1': 'c',
            'artiste_1': 'Le Groupe',
            'style_1': 'rock',
            'genre_2': '', 'artiste_2': '', 'style_2': '',
            'genre_3': '', 'artiste_3': '', 'style_3': '',
            'genre_4': '', 'artiste_4': '', 'style_4': '',
        }

    def test_formulaire_valide_sans_titre(self):
        """Le formulaire doit être valide même sans champ 'titre' fourni (bug corrige)."""
        form = EvenementForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_titre_genere_depuis_artiste(self):
        """save() doit generer le titre depuis artiste_1 si absent."""
        form = EvenementForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        evt = form.save()
        self.assertEqual(evt.titre, 'Le Groupe')

    def test_titre_genere_depuis_festival_si_pas_artiste(self):
        """Si pas d'artiste, le titre doit venir du festival."""
        data = self.valid_data.copy()
        data['artiste_1'] = ''
        form = EvenementForm(data=data)
        self.assertTrue(form.is_valid())
        evt = form.save()
        self.assertEqual(evt.titre, 'Festival Test')

    def test_statut_en_attente_par_defaut(self):
        """Un evenement soumis via le formulaire doit etre en_attente, pas publie."""
        form = EvenementForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        evt = form.save()
        self.assertEqual(evt.statut, 'en_attente')

    def test_champs_obligatoires_manquants(self):
        """Le formulaire doit etre invalide si email_contact est absent."""
        data = self.valid_data.copy()
        data['email_contact'] = ''
        form = EvenementForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email_contact', form.errors)


class GoogleSheetMensuelTest(TestCase):
    """Tests du modele de configuration des Google Sheets par mois."""

    def test_creation(self):
        sheet = GoogleSheetMensuel.objects.create(
            annee=2026, mois=9, url='https://docs.google.com/spreadsheets/d/test123'
        )
        self.assertEqual(sheet.annee, 2026)
        self.assertEqual(sheet.mois, 9)

    def test_str(self):
        sheet = GoogleSheetMensuel.objects.create(
            annee=2026, mois=9, url='https://docs.google.com/spreadsheets/d/test123'
        )
        self.assertIn('2026', str(sheet))
        self.assertIn('09', str(sheet))

    def test_unicite_annee_mois(self):
        """Un seul sheet par couple (annee, mois)."""
        GoogleSheetMensuel.objects.create(annee=2026, mois=10, url='https://example.com/sheet1')
        with self.assertRaises(Exception):
            GoogleSheetMensuel.objects.create(annee=2026, mois=10, url='https://example.com/sheet2')

    def test_recherche_par_mois(self):
        GoogleSheetMensuel.objects.create(annee=2026, mois=6, url='https://example.com/juin')
        result = GoogleSheetMensuel.objects.filter(annee=2026, mois=6).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.url, 'https://example.com/juin')
