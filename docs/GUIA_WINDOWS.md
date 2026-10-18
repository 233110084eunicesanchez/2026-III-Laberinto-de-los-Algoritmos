# Vamos a levantar tu proyecto en Windows · versión 2.0

**Si ya funciona tu instalación en D:\laberinto, sigue ACTUALIZAR.txt. No recrees la base ni las cuentas.**

## 1. Extraer y abrir la carpeta

Extrae el ZIP completo, por ejemplo en `Documentos\laberinto`. No ejecutes los archivos dentro del ZIP. Abre la carpeta que contiene `manage.py`, `requirements.txt` y `preparar.py`. Haz clic en la barra de dirección del Explorador, escribe `powershell` y pulsa Enter. Los comandos siguientes se ejecutan en esa carpeta.

## 2. Comprobar Python

```powershell
py --list
```

Recomendado: Python 3.12 o 3.13. Los comandos de esta guía usan Python 3.13. Django 5.2 admite Python 3.10–3.14. No hace falta reinstalar si ya tienes una versión compatible.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe preparar.py
```

No necesitas activar el entorno ni modificar las políticas de PowerShell. La primera instalación sí necesita internet.

## 3. Crear una base nueva con pgAdmin 4

PostgreSQL es el servidor de datos; pgAdmin es su administrador visual. La contraseña maestra de pgAdmin y la contraseña del usuario de PostgreSQL pueden ser diferentes. Necesitas PostgreSQL 14 o posterior.

1. Abre pgAdmin y conéctate a tu servidor PostgreSQL.
2. En **Login/Group Roles**, clic derecho → **Create → Login/Group Role**.
3. En General, nombre: `laberinto_app`.
4. En Definition, escribe una contraseña nueva y guárdala de forma privada.
5. En Privileges, activa **Can login?**. Deja superuser y creación de roles desactivados. Guarda.
6. En **Databases**, clic derecho → **Create → Database**.
7. Nombre: `laberinto`. Owner: `laberinto_app`. Guarda.

No reutilices la base desordenada del proyecto anterior. Si alguno de estos nombres ya existe, utiliza otro y escríbelo en `.env`.

## 4. Conectar Django con PostgreSQL

Abre el archivo `.env` creado por `preparar.py`, desde VS Code o Bloc de notas. Cambia estos valores:

```text
DB_NAME=laberinto
DB_USER=laberinto_app
DB_PASSWORD="tu contraseña de PostgreSQL"
DB_HOST=localhost
DB_PORT=5432
```

Usa comillas dobles si la contraseña contiene espacios o `#`. Si contiene comillas dobles, escápalas según el formato dotenv o usa comillas simples si no contiene apóstrofes. No envíes `.env` por chat ni lo publiques. Conserva la clave aleatoria `DJANGO_SECRET_KEY` que generó el script. Deja `DJANGO_DEBUG=True` para la instalación local.

## 5. Crear tablas y cargar el contenido

```powershell
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_initial
.\.venv\Scripts\python.exe manage.py createsuperuser
```

`migrate` crea las tablas; no tienes que diseñarlas manualmente en pgAdmin. `seed_initial` carga categorías, roles y 360 preguntas. Puedes repetirlo sin duplicar preguntas ni sobrescribir cambios.

`createsuperuser` crea TU cuenta de administrador. El correo puede dejarse vacío. Al escribir la contraseña en la terminal no se muestran caracteres: es normal.

No necesitas crear profesores por PowerShell. Después de encender el proyecto, en la pantalla de acceso pulsa **Crea tu cuenta** y selecciona **Profesor** o **Alumno**. El usuario administrador que acabas de crear conserva su acceso habitual.

## 6. Encender

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

En el navegador abre http://127.0.0.1:8000/ . Conserva abierta la terminal mientras juegas. Para detener el programa pulsa Ctrl+C. Después de esta primera instalación puedes usar `iniciar_windows.bat` con doble clic.

PostgreSQL debe estar iniciado como servicio de Windows. pgAdmin puede estar cerrado mientras juegas.

## 7. Tu primera partida

1. Crea una cuenta Alumno con nombre/alias, usuario, edad y contraseña. El correo es opcional.
2. Haz clic en la tarjeta de un mundo disponible y elige **Individual**.
3. Cada acierto mueve el robot. Alfa no tiene reloj; Beta da 35 s y Omega 30 s. El primer error termina la partida con la animación del virus.
4. En la alerta puedes **Volver a intentar**, salir o ver las explicaciones. Los aciertos únicos se conservan.
5. Para jugar con el tablero físico elige **Dinámico**. El guía controla la misma sesión, confirma llegada/virus y después el participante responde cinco preguntas. Gana con tres aciertos. Preparen el espacio físico con supervisión y sin obstáculos.
6. Como Profesor, registra tu cuenta con correo y abre **Añadir alumnos**: nombres y edades en filas, con grupo existente o nuevo en el mismo paso. No exige contraseñas por alumno.
7. En Inicio elige participante y haz clic en su mundo. Su progreso se guarda aunque todavía no tenga cuenta personal.

`COMO_JUGAR.txt` explica ambos modos, los códigos de vinculación y el 80 % de preguntas diferentes. Una cuenta de alumno puede jugar de forma independiente o vincularse posteriormente a su perfil escolar.

Para proyección, en Dinámico usa **Abrir pantalla**. La vista de lectura no tiene controles. El guía confirma el tablero desde la pantalla principal.

## 8. Usar celular y computadora en la misma red

1. Conecta ambos dispositivos a la misma red Wi-Fi de confianza.
2. Ejecuta `ipconfig` en la computadora. Localiza su dirección IPv4, por ejemplo `192.168.1.50`.
3. En `.env`, añade ESA dirección a `DJANGO_ALLOWED_HOSTS`:

```text
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.50
```

4. Detén el servidor e inicia:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

5. Si Windows pregunta por el firewall, autoriza Python solo en redes privadas. No abras puertos del router.
6. En el celular abre `http://192.168.1.50:8000/` (sustituye la IP). Entra con la cuenta del profesor y abre la misma partida desde el historial.
7. En la computadora usa esa dirección IP también para que el enlace “Abrir pantalla” se pueda copiar a otros dispositivos.

El control responde por consultas periódicas, aproximadamente cada 0.7 s. Una pantalla pública no puede contestar ni cambiar resultados. Si no abre, comprueba IP, firewall y si la Wi-Fi impide comunicación entre dispositivos. HTTP local no cifra credenciales: úsalo solo en una red de confianza; para internet se requiere HTTPS.

## 9. Problemas frecuentes

| Mensaje o situación | Qué revisar |
| --- | --- |
| `py` no se reconoce | Python instalado y su lanzador de Windows. Cierra y vuelve a abrir PowerShell. |
| No se encuentra Python 3.13 | Usa la versión compatible que aparezca en `py --list`. |
| `connection refused` | Servicio PostgreSQL iniciado, host y puerto correctos. |
| `password authentication failed` | Usuario y contraseña de PostgreSQL en `.env`, no la contraseña maestra de pgAdmin. |
| Base de datos inexistente | Nombre de base en pgAdmin y en `.env`. |
| Permiso denegado para crear tablas | La base debe pertenecer a `laberinto_app`. |
| `DisallowedHost` desde el celular | Añade la IP exacta a `DJANGO_ALLOWED_HOSTS` y reinicia. |
| No hay tablas / `relation does not exist` | Ejecuta `migrate` con la misma configuración que utiliza el servidor. |
| Faltan roles o preguntas | Ejecuta `seed_initial` después de `migrate`. |
| Puerto ocupado | Detén el otro proceso o usa `runserver 8001` y abre el puerto 8001. |
| Contraseña olvidada | Usa «Olvidé mi contraseña» si tienes correo guardado; en local el enlace aparece en PowerShell. Como alternativa administrativa, ejecuta `.\.venv\Scripts\python.exe manage.py changepassword nombre_usuario`. |
| No avanza una pregunta | Revisa la conexión; recargar conserva el intento. Si la sesión venció, vuelve a entrar y abre el historial. |

## 10. Respaldo y comprobación final

En pgAdmin, clic derecho sobre `laberinto` → **Backup**, formato Custom, elige un archivo `.backup` y ejecútalo. Guarda también el código y `.env` de forma privada. El ZIP del código no contiene tus alumnos ni sus resultados: esos viven en PostgreSQL.

Prueba con un alumno ficticio: completar misión, pisar virus, agotar tiempo, jugar Individual como alumno, recargar y verificar que otro profesor no vea esos datos. No borres alumnos reales para probar.

Para ejecutar `manage.py test core` contra PostgreSQL, Django crea una base temporal `test_laberinto`. Usa una cuenta de pruebas con permiso CREATEDB en un servidor de desarrollo; no otorgues ese permiso a la cuenta de producción ni ejecutes las pruebas sobre producción.

Cuando nos compartas un error, manda su texto o captura ocultando contraseñas. No hace falta compartir `.env`.
