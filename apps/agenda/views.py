import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from .forms import EvenementForm

def soumettre_evenement(request):
    initial = {}
    for field in ['email_contact','ville','tarif']:
        val = request.COOKIES.get('evt_' + field)
        if val:
            initial[field] = val
    lieu_cookie = request.COOKIES.get('evt_lieu')
    if lieu_cookie:
        try:
            initial['lieu'] = int(lieu_cookie)
        except (ValueError, TypeError):
            pass

    try:
        from .wagtail_hooks import FormulaireSettings
        form_settings = FormulaireSettings.for_request(request)
    except Exception:
        form_settings = None

    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            evt = form.save()
            email = form.cleaned_data.get('email_contact', '')
            lieu_nom = evt.lieu.nom if evt.lieu else ''
            ville = form.cleaned_data.get('ville', '')
            heure = form.cleaned_data.get('heure_text', '')
            tarif = form.cleaned_data.get('tarif', '')
            festival = form.cleaned_data.get('festival_nom', '')
            festival_style = form.cleaned_data.get('festival_style', '')

            # Construire recap artistes
            artistes_txt = ''
            artistes_data = []
            for i in range(1, 5):
                g = form.cleaned_data.get(f'genre_{i}', '')
                a = form.cleaned_data.get(f'artiste_{i}', '')
                s = form.cleaned_data.get(f'style_{i}', '')
                if a or g:
                    genre_label = 'Concert' if g == 'c' else 'Spectacle vivant' if g == 'sv' else ''
                    artistes_txt += f'  {genre_label}: {a} ({s})\n'
                    artistes_data.append({'genre': g, 'artiste': a, 'style': s})

            recap = (
                'Bonjour,\n\nVotre evenement a bien ete enregistre :\n\n'
                'Date : ' + str(evt.date_debut) + '\n'
                'Heure : ' + heure + '\n'
                'Lieu : ' + lieu_nom + '\n'
                'Ville : ' + ville + '\n'
                'Tarif : ' + tarif + '\n'
                'URL : ' + (evt.url or '') + '\n'
            )
            if festival:
                recap += 'Festival/Asso : ' + festival + '\n'
            if artistes_txt:
                recap += 'Artistes/Spectacles :\n' + artistes_txt
            recap += '\nIl sera examine par notre equipe.\n\nMerci,\nL equipe du Bidul'

            # Email 1: recap a l utilisateur
            if email:
                try:
                    send_mail(subject='Votre evenement a ete soumis - Le Bidul', message=recap,
                        from_email='formulaire@lebidul.com', recipient_list=[email], fail_silently=True)
                except Exception:
                    pass
                # Email 2: notification a lebidul
                try:
                    send_mail(subject='Nouvel evenement soumis : ' + (festival or lieu_nom or 'evenement'),
                        message=recap, from_email=email, recipient_list=['lebidul@live.fr'], fail_silently=True)
                except Exception:
                    pass

            # Google Sheets
            creds = getattr(settings, 'GOOGLE_CREDENTIALS_PATH', '')
            folder = getattr(settings, 'GOOGLE_SHEETS_FOLDER_ID', '')
            if creds and folder:
                try:
                    from .google_sheets import ajouter_evenement
                    sheet_data = {
                        'email': email,
                        'date_tapage': datetime.datetime.now().isoformat(),
                        'titre': festival or evt.titre or lieu_nom,
                        'style_festival': festival_style,
                        'date_debut': evt.date_debut,
                        'heure': heure,
                        'lieu': lieu_nom,
                        'ville': ville,
                        'prix': tarif,
                    }
                    for i, ad in enumerate(artistes_data):
                        sheet_data[f'genre_{i+1}'] = ad['genre']
                        sheet_data[f'artiste_{i+1}'] = ad['artiste']
                        sheet_data[f'style_{i+1}'] = ad['style']
                    ajouter_evenement(creds, folder, sheet_data)
                except Exception:
                    pass

            messages.success(request, 'Merci ! Votre evenement a ete soumis.')
            response = redirect('agenda:soumettre_evenement')
            max_age = 60 * 60 * 24 * 365
            if email:
                response.set_cookie('evt_email_contact', email, max_age=max_age)
            if evt.lieu_id:
                response.set_cookie('evt_lieu', str(evt.lieu_id), max_age=max_age)
            if ville:
                response.set_cookie('evt_ville', ville, max_age=max_age)
            if tarif:
                response.set_cookie('evt_tarif', tarif, max_age=max_age)
            return response
    else:
        form = EvenementForm(initial=initial)
    return render(request, 'agenda/soumettre_evenement.html', {'form': form, 'settings': form_settings})
