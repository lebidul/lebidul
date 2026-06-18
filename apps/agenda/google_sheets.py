import gspread
from datetime import date
MOIS_FR = {1:'Janvier',2:'Fevrier',3:'Mars',4:'Avril',5:'Mai',6:'Juin',7:'Juillet',8:'Aout',9:'Septembre',10:'Octobre',11:'Novembre',12:'Decembre'}
JOURS_FR = {0:'Lundi',1:'Mardi',2:'Mercredi',3:'Jeudi',4:'Vendredi',5:'Samedi',6:'Dimanche'}
HEADERS = ['INFO TAPEUR','DATE TAPAGE','Date Emission Radio','FESTOCHE EVENEMENT','STYLE FESTOCHE / EVENEMENT',
    'DATE','HEURE','LIEU','VILLE','PRIX',
    'GENRE 1','NOM SPECTACLE 1','COMPAGNIE 1','STYLE SPECTACLE 1',
    'GENRE 2','NOM SPECTACLE 2','COMPAGNIE 2','STYLE SPECTACLE 2',
    'GENRE 3','NOM SPECTACLE 3','COMPAGNIE 3','STYLE SPECTACLE 3',
    'GENRE 4','NOM SPECTACLE 4','COMPAGNIE 4','STYLE SPECTACLE 4']

def get_client(credentials_path):
    return gspread.service_account(filename=credentials_path)

def get_or_create_sheet(client, folder_id, annee, mois, share_with=None):
    # Verifie d'abord si une URL est configuree dans l'admin pour ce mois/annee
    try:
        from .models.snippets import GoogleSheetMensuel
        config = GoogleSheetMensuel.objects.filter(annee=annee, mois=mois).first()
        if config and config.url:
            return client.open_by_url(config.url)
    except Exception:
        pass

    mois_str = MOIS_FR.get(mois, str(mois))
    sheet_name = f'{annee}{mois:02d}_tapage_biduleur_{mois_str}_{annee}'
    try:
        for f in client.list_spreadsheet_files():
            if f['name'] == sheet_name:
                return client.open(sheet_name)
    except Exception:
        pass
    sh = client.create(sheet_name, folder_id=folder_id) if folder_id else client.create(sheet_name)
    if share_with:
        sh.share(share_with, perm_type='user', role='writer')
    sh.sheet1.update('A1', [HEADERS])
    return sh

def ajouter_evenement(credentials_path, folder_id, evt_data, share_with='le.bidul.72.le.mans@gmail.com'):
    client = get_client(credentials_path)
    d = evt_data.get('date_debut')
    if isinstance(d, str):
        d = date.fromisoformat(d)
    sh = get_or_create_sheet(client, folder_id, d.year, d.month, share_with=share_with)
    jour_fr = JOURS_FR.get(d.weekday(), '')
    row = [
        evt_data.get('email',''), evt_data.get('date_tapage',''), '',
        evt_data.get('titre',''), evt_data.get('style_festival',''),
        f'{jour_fr} {d.day}', evt_data.get('heure',''),
        evt_data.get('lieu',''), evt_data.get('ville',''), evt_data.get('prix',''),
    ]
    for i in range(1, 5):
        row.append(evt_data.get(f'genre_{i}', ''))
        row.append(evt_data.get(f'artiste_{i}', ''))
        row.append('')
        row.append(evt_data.get(f'style_{i}', ''))
    sh.sheet1.append_row(row)
    return sh.title
