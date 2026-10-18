# Arquitectura modular · versión 3.0

La versión 3.0 reorganiza el proyecto existente. Conserva el diseño 2.1 y las reglas; no es una segunda aplicación ni requiere otra base de datos.

## Apps y responsabilidades

| App | Vistas / responsabilidades | Modelos propios |
|---|---|---|
| cuentas | Registro, login, logout, perfil, recuperación y cambio de contraseña | Usa `core.User` para conservar la identidad histórica |
| inicio | Panel principal, selección de participante y mundos | Consulta otros dominios; no necesita tablas propias |
| escuela | CRUD de grupos/alumnos, alta por lote, invitaciones y vinculación | Classroom, Student |
| preguntas | CRUD de preguntas y publicación | Subject, Category, Question |
| juego | Modalidades, partidas, API de estado/acciones y proyección | Attempt, AttemptQuestion |
| progreso | Historial, resultados, aciertos y desbloqueos | Mastery, WorldUnlock |
| core | Usuario estable, políticas de acceso, mixins, compatibilidad y pruebas de integración | User |

Una app representa una responsabilidad, no cada pantalla. Login y registro pertenecen a cuentas. No todas las apps necesitan un modelo o una migración propia.

## Flujo de una petición

`config/urls.py` incluye el `urls.py` de cada app. El módulo resuelve la dirección a una clase mediante `as_view()`. La clase comprueba identidad, permiso y alcance; valida el formulario; llama al servicio cuando corresponde; utiliza modelos y devuelve una plantilla o JSON.

Todas las rutas de las seis apps usan vistas basadas en clases, incluidas las de autenticación nativas de Django. El panel `/admin/` es el subsistema nativo de Django y conserva su implementación interna.

- CRUD: ListView, DetailView, CreateView, UpdateView y DeleteView.
- Formularios: FormView en registro, perfil, vinculación y alta individual.
- Acciones/API: View con `get()` o `post()` explícitos. Los cambios de estado no aceptan GET.
- Alta por lote: View con formulario de grupo más formset de alumnos; guardado atómico.

Las plantillas específicas viven en `app/templates/app/`. `templates/base.html` y `templates/shared/` contienen la estructura y los componentes compartidos. `static/` conserva los recursos comunes y los escenarios.

## URLs y namespaces

Cada módulo declara `app_name`. Ejemplos: `cuentas:login`, `escuela:students`, `juego:play`, `progreso:history`. Enlaces y redirecciones usan nombres, no rutas copiadas.

Las direcciones visibles anteriores se conservan: `/cuenta/login/`, `/alumnos/`, `/mision/<uuid>/`, etc. Por eso `config/urls.py` incluye los módulos con prefijo vacío: el prefijo concreto lo define cada módulo. Esto mantiene los marcadores existentes sin duplicar rutas.

## Reutilización

- `core/access.py`: consultas limitadas por propietario y permisos efectivos.
- `core/mixins.py`: SchoolPermission, ScopedQuerysetMixin, OperatorFormMixin, AttemptAccessMixin y DisplayAccessMixin.
- `juego/selectors.py`: selección autorizada del participante y comprobación de quién controla una partida.
- `juego/services/game.py`: reglas, reloj, respuestas y `resume_or_create()` compartido por inicio/reintento.
- `juego/services/maze.py`: generación, validación de rutas y recorrido al virus.
- `progreso/services/progress.py`: una única implementación del 80 %, dificultades y desbloqueos.
- `escuela/services/accounts.py`: inscripción y combinación de perfiles.
- `preguntas/services/question_bank.py`: banco inicial.

Los adaptadores `core/forms.py`, `core/models.py`, `core/themes.py` y `core/services/` reexportan definiciones para imports anteriores. No contienen copias de la implementación. `core/views.py` ya no atiende rutas. Las nuevas funcionalidades se desarrollan en las apps de dominio.

## Modelos, tablas y migraciones

El modelo de usuario mantiene `AUTH_USER_MODEL='core.User'`. Cambiarlo en una instalación con datos exige una migración adicional que no aporta valor a estos requisitos.

Los otros nueve modelos pertenecen realmente a sus nuevas apps. Por ejemplo, `Student._meta.app_label` es `escuela`, aunque su tabla conserva el nombre `core_student` gracias a `Meta.db_table`. La tabla intermedia de alumnos/grupos también conserva su nombre. Así no se copian, renombran ni eliminan tablas durante esta reorganización.

Las cuatro migraciones `0001_domain_state` trasladan el estado de Django usando SeparateDatabaseAndState; `core.0006_domain_apps` retira las definiciones históricas del estado y reasigna sus content types al nuevo módulo. Mantiene sus IDs y, por tanto, los Permission y sus relaciones con grupos, usuarios y registros administrativos.

Las migraciones históricas 0001–0005 permanecen disponibles para una instalación nueva. No deben borrarse, falsificarse con `--fake` ni ejecutarse manualmente fuera de Django. El despliegue debe aplicar `manage.py migrate` completo con el servidor detenido.

## Roles y límites

Profesor y Alumno son Groups nativos; los permisos son Permission nativos. El registro público nunca permite asignar staff/superusuario. Solo los superusuarios activos acceden al panel administrativo personalizado.

Un profesor administra sus propios grupos y perfiles; puede observar una partida de su alumno, pero no controlarla si el operador es el alumno. Un alumno opera sus propias partidas. El guía utiliza los controles del participante en el modo dinámico; no se crea una identidad adicional para el guía.

La proyección pública es una excepción deliberada: token UUID aleatorio, ocho horas, sin nombre ni controles. Es un enlace de acceso por posesión del token: no se debe difundir fuera de la sesión. No sirve para responder preguntas ni modificar la partida.
