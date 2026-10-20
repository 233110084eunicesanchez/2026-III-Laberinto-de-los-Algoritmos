# Guía para explicar el proyecto · 3.0

## Explicación breve

“El proyecto está organizado en apps por responsabilidad: cuentas, inicio, escuela, preguntas, juego y progreso. Cada una tiene sus propias URLs y vistas basadas en clases. Reutilizamos formularios, mixins y servicios para que las reglas no estén copiadas en varias pantallas. Django verifica quién inició sesión, qué acción puede realizar y si el registro solicitado le pertenece.”

## Dónde demostrar cada requisito

| Requisito | Archivo que pueden abrir | Qué mostrar |
|---|---|---|
| Apps separadas | `config/settings.py` y las seis carpetas | Apps instaladas y responsabilidades distintas |
| Vistas basadas en clases | `escuela/views.py`, `cuentas/views.py`, `juego/views.py` | CRUD genérico, FormView y View con GET/POST |
| URLs por módulo | `config/urls.py` y `escuela/urls.py` | include(), app_name y as_view() |
| Permisos nativos | `core/management/commands/seed_initial.py` | Group y Permission; profesor/alumno |
| Autorización en servidor | `core/mixins.py` | SchoolPermission y AttemptAccessMixin |
| Acceso a registros propios | `core/access.py` | Consultas filtradas por profesor o alumno |
| Reutilización | `core/mixins.py`, `juego/services/game.py` | Mismos controles en varias vistas y una función para iniciar/reintentar |
| Conservar datos al separar modelos | `escuela/models.py`, `core/migrations/0006_domain_apps.py` | Nuevo app_label, misma tabla y mismos IDs de permisos |
| Pruebas de acceso roto | `core/test_modular.py` | Intentos de acceso ajeno, escalamiento, CSRF y métodos prohibidos |

## Una demostración sencilla con tres cuentas de prueba

1. Un profesor A crea un grupo y un alumno de prueba.
2. Un profesor B abre la dirección del alumno de A: recibe 404, sin sus datos.
3. Un alumno intenta abrir un CRUD reservado a profesores: recibe 403.
4. El alumno juega y el profesor A observa su resultado, dentro de su alcance.
5. El administrador puede consultar registros de ambos profesores y publicar preguntas.

No prueben con datos reales de niños. Un 403 significa “acción prohibida”; un 404 en un recurso ajeno evita revelar que existe; un 405 significa “esa dirección no acepta ese método HTTP”.

## Preguntas que podrían hacerles

**¿Control de acceso roto es una función?** No: es una vulnerabilidad. Se previene comprobando los permisos en el servidor y limitando los registros accesibles, incluso si alguien escribe la URL a mano.

**¿Ocultar un botón es suficiente?** No. Ocultarlo mejora la interfaz; el servidor debe rechazar también la petición no autorizada.

**¿Por qué login y registro están juntos?** Ambos pertenecen a la gestión de cuentas. Separar apps por responsabilidad permite compartir validación y autenticación.

**¿Por qué algunas tablas aún se llaman core_*?** Conservamos sus nombres para actualizar sin reconstruir la base. Los modelos pertenecen a sus nuevas apps; `db_table` permite usar las tablas existentes.

**¿Por qué User sigue en core?** Es la identidad histórica de las cuentas. Las pantallas de autenticación están separadas en cuentas, pero cambiar AUTH_USER_MODEL en una base con datos sería un trabajo adicional innecesario para esta reorganización.

**¿Qué significa sin código repetido?** Una regla compartida tiene una implementación central: permisos en mixins/consultas, progreso en su servicio, rutas del laberinto en otro. Cada vista puede declarar su permiso o plantilla sin duplicar la lógica que los aplica.

## Ejecutar la comprobación

En PowerShell, dentro de D:\laberinto:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test core
```

La segunda instrucción necesita un usuario PostgreSQL autorizado a crear una base temporal de pruebas. No elimina la base normal. Para comprobar solo la lógica con SQLite temporal, sigan `docs/VERIFICACION.md`.
