# Pasar de local a internet

La configuración es por entorno y la lógica está separada de las plantillas. Esto facilita la migración, pero no equivale a un despliegue ya realizado.

1. Elegir servidor Python y PostgreSQL 14+ persistente. Usar un usuario de base con permisos mínimos, claves nuevas y conexión TLS según el proveedor (`DB_SSLMODE=require` o la verificación de certificado que indique).
2. Instalar `requirements.txt`. Configurar variables sin subir `.env` a Git.
3. `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS=tu-dominio`, `CSRF_TRUSTED_ORIGINS=https://tu-dominio`.
4. Ejecutar `migrate`, `seed_initial` si la base es nueva y `collectstatic --noinput`. Para conservar datos locales, realizar respaldo y restauración PostgreSQL en lugar de inventar una migración de archivos.
5. Servir con un servidor WSGI real. Incluimos Waitress, compatible con Windows: `waitress-serve --listen=127.0.0.1:8000 config.wsgi:application`. Colocarlo detrás de HTTPS gestionado por un proxy/plataforma. No exponer `runserver` a internet.
6. Si el proxy termina HTTPS, configurar `SECURE_PROXY_SSL_HEADER` solo después de verificar que EL PROXY elimina y reescribe el encabezado confiable. No confiar en encabezados enviados directamente por clientes. Sin esa configuración un proxy mal integrado puede provocar bucles de redirección.
7. Al desactivar DEBUG se activan cookies seguras, redirección HTTPS y HSTS. Antes de habilitar un dominio comprueba que HTTPS esté correctamente configurado.
8. Ejecutar `python manage.py check --deploy`. Atender los avisos en el contexto del alojamiento.
9. Configurar respaldos, registros de errores, recuperación de cuentas y límites de solicitudes/intentos de login en la plataforma. Django básico no proporciona limitación de intentos de contraseña; añadirla antes de abrir el servicio al público.
10. Ensayar los roles con usuarios ficticios, la sincronización entre dispositivos y un respaldo/restauración antes de registrar alumnos reales.

Se incluye recuperación de contraseña por correo mediante Django. No se incluye un proveedor de correo contratado, hosting ni dominio. Antes de publicarlo configura EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS y DEFAULT_FROM_EMAIL según tu proveedor y prueba la recepción real. Con DEBUG=True se imprime el correo en la terminal; eso no envía un mensaje. Las cuentas sin correo guardado requieren ayuda del administrador. No hay verificación de titularidad de correo en esta versión. La primera versión no tiene organizaciones/escuelas aisladas como producto SaaS: tiene profesores propietarios y un administrador global.

PWA o app nativa: reutilizar servicios y modelos. Para nativa, diseñar API versionada, autenticación apropiada y permisos equivalentes; para PWA, definir primero el alcance sin conexión. No se prometen conversiones automáticas.

## Correo de recuperación

Las variables están documentadas en `.env.example`. El remitente debe estar autorizado por el proveedor. Esta configuración usa STARTTLS (habitualmente puerto 587); adapta el transporte si tu proveedor exige otro método. Nunca publiques la contraseña SMTP. Comprueba un restablecimiento completo antes de ofrecer esta función al público; las pruebas automatizadas usan un buzón en memoria, no entregas reales.

Los alumnos pueden compartir el correo de su tutor y tener nombres de usuario distintos. Django envía un enlace individual por cuenta coincidente. El correo no almacena ni identifica de forma única el progreso. Para migrar desde local restaura la base PostgreSQL con sus identidades y verifica un respaldo antes de cambiar el servicio.
