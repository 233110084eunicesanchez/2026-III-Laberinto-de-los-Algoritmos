"""Identidad visual y narrativa; no modifica reglas ni puntuaciones."""

THEMES = {
    "ALFA": dict(
        code="alfa",
        name="Laboratorio del Código",
        role="Explorador del código",
        intro="¡Tú tienes el control! Guía a tu robot hasta la meta y ayúdalo a encender el laboratorio.",
        win="¡Laboratorio activado!",
        win_detail="Tus instrucciones abrieron el camino.",
        loss="¡Un virus nos detuvo!",
        loss_detail="Tus aciertos siguen contando. ¿Probamos otra vez?",
        quiz_loss="El laboratorio aún necesita energía.",
        goal="Estación de activación",
    ),
    "BETA": dict(
        code="beta",
        name="Ciudad Conectada",
        role="Agente de ciberdefensa",
        intro="Los virus apagaron las conexiones. Guía a tu compañero y vuelve a encender la ciudad.",
        win="¡Ciudad conectada!",
        win_detail="Tu ingenio protegió la red.",
        loss="¡Conexión interceptada!",
        loss_detail="Tus aciertos se conservan. Preparemos otro intento.",
        quiz_loss="Quedaron conexiones por reparar.",
        goal="Torre de comunicaciones",
    ),
    "OMEGA": dict(
        code="omega",
        name="Zona Virus",
        role="Superhacker de sombrero blanco",
        intro="Encontraste el núcleo de la infección. Los virus dominan esta zona y solo queda una ruta segura. ¡Llega al núcleo y activa el antivirus!",
        win="¡Infección neutralizada!",
        win_detail="Tu ingenio salvó el sistema.",
        loss="¡Los virus interceptaron tu avance!",
        loss_detail="Tus aciertos se conservan. ¿Otra incursión?",
        quiz_loss="La infección resistió el antivirus.",
        goal="Terminal del antivirus",
    ),
}


def theme_for(code):
    return THEMES.get(code, THEMES["ALFA"]).copy()


def outcome(attempt):
    t = theme_for(attempt.category.code)
    if attempt.state == "won":
        return t["win"], t["win_detail"]
    if attempt.state == "abandoned":
        return (
            "Misión interrumpida",
            "Tus aciertos se conservan. Vuelve cuando quieras.",
        )
    return (
        t["quiz_loss"]
        if attempt.state == "lost" and attempt.mode != "solo"
        else t["loss"]
    ), t["loss_detail"]
