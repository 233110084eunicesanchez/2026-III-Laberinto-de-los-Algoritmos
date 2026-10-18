# Identidad visual · 2.1

El niño programa la aventura. El robot es su compañero y marcador, no el protagonista de las decisiones. La aplicación comparte navegación azul, tipografía de sistema, tarjetas redondeadas, mundos flotantes y controles reales accesibles sobre ilustraciones.

| Mundo | Rol | Color | Escenario | Victoria |
|---|---|---|---|---|
| Alfa | Explorador del código | Verde, menta y turquesa | Laboratorio del Código | Laboratorio activado; confeti verde, blanco y dorado |
| Beta | Agente de ciberdefensa | Amarillo oro y azul | Ciudad Conectada | Ciudad conectada; chispas doradas y cian |
| Omega | Superhacker de sombrero blanco | Rojo y morado | Zona Virus | Infección neutralizada; red segura azul |

Omega conserva el protagonismo de la infección en el escenario y los virus. Su robot lleva un sombrero blanco. La derrota conserva mensajes de aliento y acceso al reintento; los aciertos siguen contando según las reglas existentes.

## Mantenimiento

- `juego/themes.py`: nombres, roles, textos de preparación y resultados.
- `static/worlds.css`: colores, capas, escenarios, atlas del robot y adaptación móvil. Se carga después de los estilos anteriores.
- `static/game.js`: controles, movimiento y presentación del estado recibido del servidor.
- `static/effects.js`: celebraciones canvas finitas. Sin capturar clics, sin bucles permanentes.
- `static/appearance.js`: preferencia de movimiento reducido persistente en el navegador.
- `static/art/alfa.png`, `beta.png`, `omega.png`: escenarios completos.
- `static/art/robots.png`: atlas transparente de tres variantes del mismo compañero, recortado por CSS.
- `static/art/virus.svg`: icono vectorial del tablero.

Las preguntas, las rutas, los permisos y el progreso se deciden en el servidor. Los fondos no contienen texto, botones ni preguntas. Los mensajes finales distinguen un virus físico/virtual de no alcanzar tres aciertos en el cuestionario dinámico.

No hay sonido automático; la animación reducida respeta la preferencia inicial del sistema y puede cambiarse desde la partida. El movimiento reducido simplifica el recorrido al virus sin alterar el resultado ni los tiempos.

## Procedencia de las ilustraciones

Escenarios y atlas creados con la herramienta integrada de generación de imágenes; no se utilizó la alternativa CLI/API. El atlas conserva transparencia real. Se incluyen como recursos locales para no depender de un proveedor de imágenes al jugar.

Especificaciones de producción de las imágenes:

- Alfa: fondo panorámico de videojuego infantil 3D estilizado; laboratorio jardín flotante, edificios blancos redondeados con detalles verdes, cúpulas menta, pasos holográficos turquesa, estación de activación, jardines y cascadas entre nubes. Luz diurna acogedora. Predomina verde; sin personajes, texto, interfaz, marcos ni marcas de agua. Arte hasta los bordes.
- Beta: ciudad tecnológica flotante, edificios y puentes dorados, conexiones luminosas y torre de comunicaciones, cielo cálido; aventura 3D estilizada, oro y amarillo con cian; panorama sin texto, personajes ni controles dibujados.
- Omega: zona infectada flotante, núcleo viral rojo luminoso, arquitectura tecnológica oscura, virus y energía de infección violeta; aventura 3D estilizada para adolescentes, rojo/morado, índigo y pequeños acentos cian; sin texto ni interfaz.
- Robots: atlas horizontal transparente de tres variantes del mismo robot blanco simpático de rostro negro y ojos cian; Alfa detalles verdes, Beta dorados con visor y herramientas, Omega violeta con escudo azul y sombrero blanco. Figuras completas en tres columnas iguales, sin texto ni fondo.

Las instrucciones anteriores documentan la dirección de arte para futuras variantes; los recursos finales incluidos son la referencia visual de esta versión.
