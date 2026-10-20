from pathlib import Path
import secrets
p = Path(__file__).resolve().parent
if (p/'.env').exists():
    print('Tu .env ya existe; no se ha modificado.')
else:
    (p/'.env').write_text((p/'.env.example').read_text().replace('REEMPLAZAR_CON_PREPARAR_PY', secrets.token_urlsafe(50)),encoding='utf-8')
    print('Se creó .env. Ahora configura DB_PASSWORD y los datos de PostgreSQL.')
