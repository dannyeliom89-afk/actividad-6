"""
Management command para:
1. Eliminar todos los usuarios existentes.
2. Crear director + docentes del listado oficial.
   - Username: nombre_seccion  (ej: hulmer_1a)
   - Contraseña: PrimerApellido123  (ej: Loayza123)
   - Sin cuentas de TRABAJADOR D
Uso: python manage.py cargar_docentes
"""
import sys
import unicodedata
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


def normalizar(texto):
    """Quita tildes, convierte a minúsculas y elimina espacios."""
    nfkd = unicodedata.normalize('NFKD', texto)
    sin_tilde = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return sin_tilde.lower().replace(' ', '_').replace('/', '').replace('.', '')


# ---------------------------------------------------------------------------
# Datos: (seccion, condicion, ci, apellido1, apellido2, nombre)
# - username  = normalizar(nombre) + "_" + normalizar(seccion)
# - contraseña = apellido1.capitalize() + "123"
# - NO se incluyen los 5 TRABAJADOR D
# ---------------------------------------------------------------------------
DOCENTES = [
    ("1A",          "NOMBRADO",    "02410380", "LOAYZA",     "JUANITO",    "HULMER RAMIRO"),
    ("1B",          "NOMBRADO",    "41739925", "MAMANI",     "PARISUANA",  "EMILIO"),
    ("1C",          "NOMBRADO",    "02435038", "QUISOCALA",  "LOPE",       "DINA"),
    ("1D",          "NOMBRADO",    "01556203", "SANCHEZ",    "QUISPE",     "IRMA"),
    ("1E",          "NOMBRADO",    "01983254", "VARGAS",     "PAMPA",      "FREDY"),
    ("1F",          "NOMBRADO",    "02410319", "LANZA",      "GALLEGOS",   "NURY SABINA"),
    ("1G",          "NOMBRADO",    "01488595", "LOPEZ",      "TAVERA",     "CARMEN ROSA"),
    ("1H",          "NOMBRADO",    "02440823", "QUISPE",     "QUISPE",     "JUSTO JAVIER"),
    ("2A",          "NOMBRADO",    "44488698", "RAMOS",      "CONDORI",    "KARLA YANIRA"),
    ("2B",          "NOMBRADO",    "02423471", "RAMIREZ",    "PAREDES",    "JAFET JOSE"),
    ("2C",          "NOMBRADO",    "02369419", "QUISPE",     "FERNANDEZ",  "SEVERIANO"),
    ("2D",          "NOMBRADO",    "02413994", "CALIZAYA",   "MALDONADO",  "ROGER"),
    ("2E",          "NOMBRADO",    "42783818", "PACORI",     "QUECARA",    "YGOR"),
    ("2F",          "NOMBRADO",    "02164109", "SALAZAR",    "CANAZA",     "SEMPRONIANA"),
    ("2G",          "NOMBRADO",    "02161759", "BUSTINZA",   "TICONA",     "LIDIA MARINA"),
    ("2H",          "DESTAQUE",    "42538013", "GERPA",      "JOVE",       "SONIA MERCEDES"),
    ("3A",          "NOMBRADO",    "02403033", "GUTIERREZ",  "MENDOZA",    "NERY SUSANA"),
    ("3B",          "NOMBRADO",    "02429163", "APAZA",      "MUNOZ",      "DELIA ROSA"),
    ("3C",          "NOMBRADO",    "46889637", "PUMA",       "VILCA",      "RUTH YANETH"),
    ("3D",          "NOMBRADO",    "02366909", "MAMANI",     "MONZON",     "INES"),
    ("3E",          "REASIGNADO",  "02407431", "ARIAS",      "ZARAVIA",    "JUSTO WILLY"),
    ("3F",          "NOMBRADO",    "01311793", "COAPAZA",    "QUISPE",     "NORMA JUSTINA"),
    ("3G",          "NOMBRADO",    "01287792", "TICONA",     "MAQUERA",    "JUAN"),
    ("3H",          "CONTRATO",    "44842579", "CALIZAYA",   "CASTRO",     "ZAIDA VERONICA"),
    ("4A",          "NOMBRADO",    "02444805", "SUCASACA",   "TOLEDO",     "ANA MARIA"),
    ("4B",          "CONTRATADO",  "43631908", "BARRANTES",  "VILCA",      "EDGAR"),
    ("4C",          "NOMBRADO",    "02145541", "GUTIERREZ",  "CHATA",      "MARTHA ANELY"),
    ("4D",          "NOMBRADO",    "01991131", "CONDORI",    "MAMANI",     "JORGE"),
    ("4E",          "NOMBRADO",    "02292149", "AYQUI",      "SUCA",       "LUCRECIA"),
    ("4F",          "CONTRATADO",  "40570576", "MIRANDA",    "YUCRA",      "MARINA DIONICIA"),
    ("4G",          "NOMBRADO",    "02298546", "CAHUANA",    "CCALLO",     "DAVID"),
    ("4H",          "NOMBRADO",    "02383657", "ESCOBEDO",   "ENRIQUEZ",   "ELIZABETH ROSAURA"),
    ("5A",          "NOMBRADO",    "42989168", "VELASQUEZ",  "CHAMBI",     "CLORINDA"),
    ("5B",          "NOMBRADO",    "01287328", "COILA",      "VELASQUEZ",  "CONSTANTINO"),
    ("5C",          "NOMBRADO",    "02444317", "PAREDES",    "CALVO",      "AMALIA"),
    ("5D",          "DESTAQUE",    "45522867", "MAMANI",     "MAMANI",     "NELLY MARITZA"),
    ("5E",          "NOMBRADO",    "02011582", "MAMANI",     "CHAMBI",     "FABIANA"),
    ("5F",          "REASIGNADO",  "02445905", "MASCO",      "MAYTA",      "GINA GLORIA"),
    ("5G",          "RESIGNADO",   "43744049", "CANAZA",     "MAMANI",     "LUZ MIRIAN"),
    ("5H",          "NOMBRADO",    "01683781", "RAMOS",      "CACERES",    "WALKER ANIBAL"),
    ("6A",          "CONTRATADO",  "44657495", "ACERO",      "TICONA",     "GENOVEVA"),
    ("6B",          "NOMBRADO",    "01491866", "AMANQUI",    "MAMANI",     "MAURO ERMITANO"),
    ("6C",          "NOMBRADO",    "41404641", "MAMANI",     "REYES",      "GERARDO VICTORINO"),
    ("6D",          "NOMBRADO",    "02520668", "ROSSEL",     "CESPEDES",   "LOURDES"),
    ("6E",          "NOMBRADO",    "01540397", "ZAMATA",     "TICONA",     "CLETO MARCELINO"),
    ("6F",          "NOMBRADO",    "02429461", "AQUICE",     "QUISPE",     "RUTH ELIZABETH"),
    ("6G",          "NOMBRADO",    "01334018", "MOLLINEDO",  "CLAVERIAS",  "MARIA MAGDALENA"),
    ("6H",          "NOMBRADO",    "02415186", "PINO",       "YANQUI",     "JULIO RONALTH"),
    ("ED.FISICA",   "NOMBRADO",    "02145684", "TICONA",     "MENDEZ",     "EDDY LEORADIA"),
    ("ED.FISICA",   "CONTRATADO",  "80023144", "PARI",       "HUMPIRI",    "PAUL AQUILES"),
    ("ED.FISICA",   "NOMBRADO",    "02152553", "GUTIERREZ",  "VIZA",       "JUAN BONIFACIO"),
    ("ED.FISICA",   "NOMBRADO",    "02390259", "ARAPA",      "MAMANI",     "FRANCISCO ALFREDO"),
    ("ED.FISICA",   "NOMBRADO",    "40267197", "QUISPE",     "TAPIA",      "EDITH"),
    ("PIP",         "NOMBRADO",    "02436532", "VILCAPAZA",  "CCUNO",      "ADRIAN"),
    ("PIP",         "NOMBRADO",    "02430838", "PARICAHUA",  "CONDORI",    "HECTOR FREDY"),
    ("PSICOLOGIA",  "CONTRATO",    "47436846", "ZAVALA",     "TTITO",      "ROSANEL YURBY"),
    ("SECRETARIA",  "CONTRATADO",  "45387482", "HUAYNACHO",  "QUISPE",     "NIEVES PILAR"),
    ("AUXILIAR",    "NOMBRADO",    "01284808", "MIRANDA",    "FLORES",     "LIDIA MARINA"),
]


class Command(BaseCommand):
    help = 'Elimina todos los usuarios y crea director + docentes del listado oficial'

    def handle(self, *args, **kwargs):
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')

        # ── 1. Borrar todos los usuarios ────────────────────────────────────
        total_borrados = User.objects.all().count()
        User.objects.all().delete()
        self.stdout.write(self.style.WARNING(
            f'  Eliminados: {total_borrados} usuario(s) previos.'
        ))

        # ── 2. Crear director ───────────────────────────────────────────────
        director = User(
            username='director',
            email='director@ie1122.edu.pe',
            first_name='Director',
            last_name='IE 1122 Maria Auxiliadora',
            role='director',
            is_staff=True,
            is_active=True,
            seccion_asignada='',
        )
        director.set_password('director2025')
        director.save()
        self.stdout.write(self.style.SUCCESS(
            '  [OK] Director  ->  usuario: director | pass: Director2025!'
        ))

        # ── 3. Crear docentes ───────────────────────────────────────────────
        creados = []
        used_usernames = set()

        for seccion, condicion, ci, ap1, ap2, nombre in DOCENTES:
            # Username: primera palabra del nombre + _ + seccion normalizada
            primera_palabra = normalizar(nombre.split()[0])
            sec_norm = normalizar(seccion)
            base_username = f'{primera_palabra}_{sec_norm}'

            # Garantizar unicidad si hay colisiones
            username = base_username
            counter = 2
            while username in used_usernames:
                username = f'{base_username}{counter}'
                counter += 1
            used_usernames.add(username)

            # Contraseña: PrimerApellido + 123
            password = f'{ap1.capitalize()}123'

            first_name = nombre.title()
            last_name = f'{ap1.title()} {ap2.title()}'

            doc = User(
                username=username,
                email=f'{ci}@ie1122.edu.pe',
                first_name=first_name,
                last_name=last_name,
                role='docente',
                is_active=True,
                seccion_asignada=seccion,
            )
            doc.set_password(password)
            doc.save()
            creados.append((username, password, first_name, last_name, seccion))
            self.stdout.write(
                self.style.SUCCESS(
                    f'  [OK] {first_name} {last_name} ({seccion})  ->  {username} | {password}'
                )
            )

        # ── 4. Resumen final ────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 72))
        self.stdout.write(self.style.SUCCESS(
            f'  {len(creados) + 1} cuentas creadas (1 director + {len(creados)} docentes).'
        ))
        self.stdout.write(self.style.SUCCESS('=' * 72))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('  CREDENCIALES COMPLETAS:'))
        self.stdout.write(
            f'  {"ROL":<12} {"USUARIO":<28} {"CONTRASENA":<20} NOMBRE / SECCION'
        )
        self.stdout.write('  ' + '-' * 80)
        self.stdout.write(
            f'  {"DIRECTOR":<12} {"director":<28} {"Director2025!":<20} Director IE 1122'
        )
        for username, password, first_name, last_name, seccion in creados:
            self.stdout.write(
                f'  {"DOCENTE":<12} {username:<28} {password:<20} {first_name} {last_name} ({seccion})'
            )
        self.stdout.write('')
