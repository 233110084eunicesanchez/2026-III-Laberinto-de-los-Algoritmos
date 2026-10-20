# Verificación · versión 3.0

Entorno de desarrollo: Linux, Python 3.12 y Django 5.2.18. La configuración predeterminada del proyecto sigue usando PostgreSQL; SQLite solo se activa explícitamente para pruebas.

## Verificación modular 3.0

- 79 pruebas automatizadas: 65 regresiones existentes y 14 pruebas de organización, autorización y migración.
- Todas las rutas de las seis apps están asociadas a clases y poseen namespace. Las direcciones públicas anteriores se conservan.
- Acceso de otro profesor a alumnos, grupos, preguntas y partidas rechazado; alumno sin permisos no puede administrar ni publicar; un profesor puede observar pero no controlar una partida operada por el alumno.
- Campos manipulados de autor, profesor y estado no escalan permisos. Revocar permisos de lectura corta el acceso a las partidas.
- Acciones mediante GET rechazadas; CSRF requerido; cuerpos JSON inválidos devuelven 400 sin cambiar estado. Proyección solo lectura, sin nombre/rutas físicas y con caducidad.
- Migración desde 2.1 probada con cuentas, contraseñas, grupos escolares, membresías, grupos de permisos y permisos directos; IDs de content types y permisos conservados.
- Actualización adicional sobre la base local de pruebas de 2.1: misma cantidad de filas en todas las tablas core_*, 360 preguntas conservadas, roles intactos e inicio HTTP 200 tras migrar.
- `check`, `makemigrations --check --dry-run` y `collectstatic --noinput` completados. No hay cambios de modelos pendientes.

Estas comprobaciones se realizaron en Linux/Python 3.12 con SQLite. La nueva migración debe comprobarse todavía en la instalación Windows/PostgreSQL de la usuaria con respaldo previo. No se afirma una auditoría de seguridad integral ni se han realizado pruebas nuevas de carga o despliegue público. La revisión visual en Chromium descrita abajo corresponde a 2.1; en 3.0 se conserva el arte y se prueba el renderizado de las páginas mediante el cliente de Django.

## Revisión del rediseño 2.1

- 65 pruebas automatizadas ejecutadas de nuevo: todas pasan, incluyendo preservación de datos con la nueva migración 0005.
- Chromium: victorias individuales en los tres mundos, las tres celebraciones aparecen y finalizan; fallo individual, preferencia de movimiento reducido persistente, primer error dinámico continúa y proyección sin controles. Sin errores JavaScript.
- Revisión visual de inicio, preparación, preguntas y victorias a 1440 px; juego, derrota e inicio a 390 px, sin desbordamiento horizontal.
- Validación de lectura completa de los cuatro PNG, comprobación de sintaxis JavaScript y recopilación de estáticos con recursos locales.
- `check` sin incidencias, `makemigrations --check --dry-run` sin cambios pendientes.
- No se ha instalado esta versión visual en la computadora de la usuaria. La migración 0005 se probó aquí con SQLite; falta su comprobación local en PostgreSQL.

## Comprobaciones de lógica conservadas

- **65 pruebas automatizadas** pasan con SQLite temporal. Incluyen registro, CRUD, permisos, aislamiento entre profesores, CSRF y acceso a mundos comprobado en servidor.
- 300 tableros físicos verificados: número exacto de rutas, pasos ortogonales, longitud mínima y variedad de metas. Otros 30 tableros individuales comprueban trayectorias al virus desde todas sus casillas seguras.
- Banco de 360 preguntas distintas: 120 por categoría, 40 por dificultad, cuatro opciones diferentes y carga idempotente.
- Individual: total de preguntas igual a movimientos, victoria al terminar la ruta, derrota al primer error, timeout y conservación de aciertos.
- Alfa sin fecha límite en ambos modos; Beta 35 s y Omega 30 s. Recargas, respuestas duplicadas y posiciones antiguas no cambian la puntuación indebidamente.
- Dinámico: cinco preguntas seguidas sin pausa, todos los resultados de 0 a 5, victoria desde tres aciertos y alumno con controles sobre su propio intento.
- Progreso: 95/120 no desbloquea; 96/120 sí; aciertos repetidos no duplican; partidas fallidas cuentan; desbloqueos persistentes y acceso a dificultades posteriores.
- Alta de alumnos en lote sin crear cuentas; grupo en el mismo paso; errores de validación no dejan perfiles/grupos parciales; rechazo de grupos de otro profesor.
- Vinculación de perfil escolar a cuenta, unión de historial/aciertos, código de un solo uso y rechazo de transferencias entre profesores.
- Correo requerido para nuevos profesores y opcional para alumnos. Recuperación probada con buzón de memoria: generación de enlace, validación y cambio efectivo de contraseña. No se enviaron correos reales.
- Prueba de migración desde 0002 con cuentas y partidas históricas: conserva contraseñas, resultados y preguntas; recupera nombre, acredita una sola vez aciertos repetidos y calcula desbloqueos. Las migraciones 0003 y 0004 también se aplicaron sobre la base local de comprobación de v1.1.
- Chromium: login, mundo Alfa, individual con acierto/error/animación/reintento, dinámico completo con tres aciertos, pegado de alumnos por lote y guardado sin cuentas. Sin errores JavaScript observados.
- Revisión visual a 1440 y 390 px. Diseño móvil apilado sin desbordamiento horizontal de página; tablas y navegación usan sus propios contenedores desplazables. Robot SVG local para no depender de fuentes emoji.
- `manage.py check`, `makemigrations --check --dry-run` y `collectstatic --noinput` completados.

## Límites

Las nuevas migraciones y los bloqueos concurrentes **no se probaron en PostgreSQL real** en este entorno. La usuaria confirmó la instalación y las migraciones 0003/0004 de v2.0 en Windows/PostgreSQL; esta actualización debe aplicarse y comprobarse allí con respaldo previo. No se ha accedido remotamente a su computadora.

No se realizaron pruebas de carga, publicación en hosting, entrega SMTP real ni pruebas en una red escolar. El backend de correo local imprime el enlace en la terminal. Antes de internet se necesita configurar y probar SMTP/HTTPS, respaldos y límites de intentos de acceso.

El banco usa familias de ejercicios con variantes numéricas. Su adecuación pedagógica y los tiempos de Beta/Omega requieren evaluación en una clase piloto. Las pruebas de código no sustituyen esa revisión.

## Ejecutar pruebas

Con PostgreSQL de desarrollo y un usuario autorizado a crear la base temporal de pruebas:

```powershell
.\.venv\Scripts\python.exe manage.py test core
```

Para comprobar la lógica sin PostgreSQL, en una terminal de pruebas:

```powershell
$env:LAB_TEST_SQLITE="1"
.\.venv\Scripts\python.exe manage.py test core
Remove-Item Env:LAB_TEST_SQLITE
```

Django crea y elimina su base temporal. El ZIP no contiene bases de prueba, alumnos ficticios, credenciales ni capturas de la revisión.
