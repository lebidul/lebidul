import os, re
from io import BytesIO
from pathlib import Path
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from wagtail.images.models import Image as WagtailImage
from apps.agenda.models import Bidul
from apps.content.models.pages import BidulPage

DIR_COUV  = Path(r"C:\Users\compteadmin\stage\img\couv")
DIR_OTHER = Path(r"C:\Users\compteadmin\stage\img\other img")

RE_DIMS = re.compile(r"-\d+x\d+\.", re.I)

def is_double_page(path):
    try:
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            w, h = im.size
            return w > h  # paysage = double page
    except:
        return False

def score(name):
    n = name.lower()
    if re.search(r"-\d+x\d+\.", n): return -1
    if "rotated" in n: return -1
    if "150x150" in n: return -1
    if n.endswith(".pdf"): return -1
    if n.endswith(".webp"): return -1
    if re.search(r"7\d\dx1024", n): return 1
    if re.search(r"2\d\dx300", n): return 2
    return 3

def extract_numero(name):
    # Pattern: 202501_298.jpg
    m = re.search(r"\d{6}_(\d+)", name)
    if m: return int(m.group(1))
    # Pattern: 1997-02-Couv-Bidul-001.jpg
    m = re.search(r"[Bb]idul[-_.](\d+)", name)
    if m: return int(m.group(1))
    # Pattern: bidul.4.15.1.jpg -> numéro inconnu, skip
    return None

def find_best(numero):
    best, best_score = None, 999
    for year in DIR_OTHER.iterdir():
        if not year.is_dir(): continue
        for month in year.iterdir():
            if not month.is_dir(): continue
            for f in month.iterdir():
                if not f.is_file(): continue
                n = extract_numero(f.name)
                if n != numero: continue
                s = score(f.name)
                if s == -1: continue
                if s < best_score:
                    best_score, best = s, f
    return best

def find_couv(numero):
    for ext in (".jpg", ".jpeg", ".png"):
        for stem in (f"{numero:03d}", str(numero)):
            p = DIR_COUV / f"{stem}{ext}"
            if p.exists(): return p
    return None

def make_image(path, title):
    ex = WagtailImage.objects.filter(title=title).first()
    if ex: return ex, False
    with open(path, "rb") as f:
        data = f.read()
    img = WagtailImage(title=title)
    img.file = ImageFile(BytesIO(data), name=path.name)
    img.save()
    return img, True

class Command(BaseCommand):
    help = "Reimporte toutes les couvertures Bidul"

    def add_arguments(self, parser):
        parser.add_argument("--confirm", action="store_true")
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--numero", type=int, default=0)

    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stdout.write("Ajoute --confirm pour lancer.")
            return

        biduls = Bidul.objects.order_by("numero")
        if options["numero"]:
            biduls = biduls.filter(numero=options["numero"])

        ok = skip = missing = err = 0

        for bidul in biduls:
            n = bidul.numero
            self.stdout.write(f"\n#{n:03d} {bidul.mois} {bidul.annee}")

            try: page = bidul.page
            except: page = None

            if page and page.couverture and not options["force"]:
                self.stdout.write("  skip (deja present)")
                skip += 1
                continue

            path = find_best(n) or find_couv(n)

            if not path:
                self.stdout.write("  MANQUANT")
                missing += 1
                continue

            if is_double_page(path):
                self.stdout.write(f"  double page detectee: {path.name}, fallback couv/")
                path = find_couv(n) or path

            self.stdout.write(f"  -> {path.name}")

            try:
                img, created = make_image(path, f"Couverture Bidul #{n:03d}")
                if page:
                    page.couverture = img
                    page.save_revision().publish()
                    self.stdout.write("  OK")
                ok += 1
            except Exception as e:
                self.stdout.write(f"  ERREUR: {e}")
                err += 1

        self.stdout.write(f"\nOK:{ok} SKIP:{skip} MANQUANT:{missing} ERREUR:{err}")
