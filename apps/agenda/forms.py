from django import forms
from .models import Evenement, Lieu

VILLES_SARTHE = [('', 'Choisir une ville...')] + [(v, v) for v in [
    'Aigne','Aillieres-Beauvoir','Allonnes','Amne','Ancinnes','Arnage','Aubigne-Racan',
    'Ballon-Saint Mars','Beaumont-sur-Sarthe','Bonnetable','Bouloire','Brulon',
    'Cerans-Foulletourte','Champagne','Change','Conlie','Connerre','Coulaines',
    'Coulans-sur-Gee','Domfront-en-Champagne','Ecommoy','Ferce-sur-Sarthe','Fille',
    'Fresnay-sur-Sarthe','Guecelard','Jupilles','La Bazoge','La Chapelle-Saint-Aubin',
    'La Ferte-Bernard','La Fleche','La Milesse','La Suze-sur-Sarthe','Le Grand-Luce',
    'Le Lude','Le Mans','Loue','Louplande','Luche-Pringe','Malicorne-sur-Sarthe',
    'Mamers','Marcon','Mayet','Monce-en-Belin','Montfort-le-Gesnois','Montval-sur-Loir',
    'Mulsanne','Noyen-sur-Sarthe','Parigne-l Eveque','Pontvallain','Precigne',
    'Roeze-sur-Sarthe','Rouillon','Ruaudin','Sable-sur-Sarthe','Saint-Calais',
    'Saint-Cosme-en-Vairais','Saint-Saturnin','Sarge-les-le-Mans','Savigne-l Eveque',
    'Sille-le-Guillaume','Solesmes','Teloche','Yvre-l Eveque',
]]

GENRE_CHOICES = [('', '---------'), ('c', 'Concert'), ('sv', 'Spectacle vivant')]

class EvenementForm(forms.ModelForm):
    email_contact = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'stephane.lefoll@lemans.fr'}))
    heure_text = forms.CharField(required=True, max_length=20, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '20h30'}))
    lieu = forms.ModelChoiceField(queryset=Lieu.objects.filter(actif=True).order_by('nom'), required=True, empty_label='Choisir un lieu...', widget=forms.Select(attrs={'class': 'form-select'}))
    ville = forms.ChoiceField(choices=VILLES_SARTHE, required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    tarif = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '8 EUR, prix libre, au chapeau...'}))
    festival_nom = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Festival Bebop, Orga Cortex...'}))
    festival_style = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'festival de theatre de rue'}))
    genre_1 = forms.ChoiceField(choices=GENRE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    artiste_1 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Cie Punto y Trazo, Syl...'}))
    style_1 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'theatre, post-punk...'}))
    genre_2 = forms.ChoiceField(choices=GENRE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    artiste_2 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input'}))
    style_2 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input'}))
    genre_3 = forms.ChoiceField(choices=GENRE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    artiste_3 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input'}))
    style_3 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input'}))
    genre_4 = forms.ChoiceField(choices=GENRE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    artiste_4 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input'}))
    style_4 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input'}))
    nouveau_lieu_nom = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom du nouveau lieu'}))

    class Meta:
        model = Evenement
        fields = ['date_debut', 'lieu', 'url']
        widgets = {
            'date_debut': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
        }

    def save(self, commit=True):
        evt = super().save(commit=False)
        evt.statut = 'en_attente'
        evt.prix = self.cleaned_data.get('tarif', '')
        evt.description = self.cleaned_data.get('festival_nom', '')
        # Générer le titre automatiquement
        if not evt.titre:
            artiste = self.cleaned_data.get('artiste_1', '')
            festival = self.cleaned_data.get('festival_nom', '')
            lieu = self.cleaned_data.get('lieu')
            lieu_nom = lieu.nom if lieu else ''
            evt.titre = artiste or festival or lieu_nom or 'Événement sans titre'
        if commit:
            evt.save()
        return evt
