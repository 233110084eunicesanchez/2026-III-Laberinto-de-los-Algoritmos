"""360 ejercicios reproducibles: 10 familias × 4 variantes × 3 dificultades × 3 categorías.
Las variantes cambian cantidades; no se presentan como 360 tipos pedagógicos diferentes.
"""

import random


def bank():
    for code in ["ALFA", "BETA", "OMEGA"]:
        for d in [1, 2, 3]:
            for k in range(1, 5):
                a = k + 4 * (d - 1) + 2
                b = k + 4 * (d - 1) + 1
                n = 2 * d + 2
                if code == "ALFA":
                    rows = [
                        (
                            "Sumas",
                            f"Tienes {a} estrellas y ganas {b} más. ¿Cuántas tienes?",
                            a + b,
                            f"Suma {a} + {b} = {a + b}.",
                        ),
                        (
                            "Restas",
                            f"Hay {a + b} robots y {b} se van. ¿Cuántos quedan?",
                            a,
                            f"Resta {a + b} − {b} = {a}.",
                        ),
                        (
                            "Patrones",
                            f"¿Qué número sigue? {a}, {a + 2}, {a + 4}, …",
                            a + 6,
                            "La secuencia aumenta de dos en dos.",
                        ),
                        (
                            "Comparación",
                            f"¿Cuál es el mayor: {a}, {a + 3}, {a + 1} o {a + 2}?",
                            a + 3,
                            f"{a + 3} es el número más grande.",
                        ),
                        (
                            "Conteo",
                            f"Cuenta hacia atrás: {a + 5}, {a + 4}, {a + 3}, … ¿Qué sigue?",
                            a + 2,
                            "Cada número es uno menos que el anterior.",
                        ),
                        (
                            "Dobles",
                            f"Hay {b} fichas en una caja y otras {b} en otra. ¿Cuántas hay en total?",
                            2 * b,
                            f"{b} + {b} = {2 * b}.",
                        ),
                        (
                            "Número faltante",
                            f"Tienes {b} llaves y necesitas {a + b}. ¿Cuántas te faltan?",
                            a,
                            f"{a + b} − {b} = {a}.",
                        ),
                        (
                            "Orden",
                            f"¿Qué número va justo después de {a + 10 * (d - 1)}?",
                            a + 10 * (d - 1) + 1,
                            "Para encontrar el siguiente número sumamos uno.",
                        ),
                        (
                            "Problemas",
                            f"Juntas {a} monedas, ganas 2 y gastas 1. ¿Cuántas te quedan?",
                            a + 1,
                            f"{a} + 2 − 1 = {a + 1}.",
                        ),
                        (
                            "Mitades",
                            f"Reparte {2 * b} botones en dos grupos iguales. ¿Cuántos hay en cada grupo?",
                            b,
                            f"{b} + {b} = {2 * b}.",
                        ),
                    ]
                elif code == "BETA":
                    rows = [
                        (
                            "Multiplicación",
                            f"Hay {a} bolsas con {b} canicas cada una. ¿Cuántas canicas hay?",
                            a * b,
                            f"Multiplica {a} × {b} = {a * b}.",
                        ),
                        (
                            "División",
                            f"Reparte {a * b} fichas entre {b} personas por igual. ¿Cuántas recibe cada una?",
                            a,
                            f"{a * b} ÷ {b} = {a}.",
                        ),
                        (
                            "Fracciones",
                            f"¿Cuánto es la cuarta parte de {4 * a}?",
                            a,
                            f"Divide {4 * a} entre 4.",
                        ),
                        (
                            "Patrones",
                            f"¿Qué sigue en {a}, {a + n}, {a + 2 * n}, …?",
                            a + 3 * n,
                            f"Suma {n} cada vez.",
                        ),
                        (
                            "Dinero",
                            f"Pagas con {10 * a} pesos un objeto de {10 * a - b * 2} pesos. ¿Cuánto cambio recibes?",
                            b * 2,
                            f"{10 * a} − {10 * a - b * 2} = {b * 2}.",
                        ),
                        (
                            "Tiempo",
                            f"Una actividad dura {a * 5} minutos y otra {b * 5}. ¿Cuántos minutos duran juntas?",
                            (a + b) * 5,
                            f"Suma {a * 5} + {b * 5}.",
                        ),
                        (
                            "Geometría",
                            f"Un cuadrado tiene lados de {a} cm. ¿Cuántos cm mide su perímetro?",
                            4 * a,
                            f"Suma sus cuatro lados: 4 × {a}.",
                        ),
                        (
                            "Complementos",
                            f"¿Cuánto le falta a {100 - a * 3} para llegar a 100?",
                            a * 3,
                            f"100 − {100 - a * 3} = {a * 3}.",
                        ),
                        (
                            "Problemas",
                            f"Hay {b} cajas con {a} lápices cada una. Se usan {b} lápices. ¿Cuántos quedan?",
                            a * b - b,
                            f"{b} × {a} − {b} = {a * b - b}.",
                        ),
                        (
                            "Comparación",
                            f"Un equipo tiene {a * 3} puntos y otro {b * 2}. ¿Por cuántos puntos gana el primero?",
                            a * 3 - b * 2,
                            f"Resta {a * 3} − {b * 2}.",
                        ),
                    ]
                else:
                    rows = [
                        (
                            "Lógica de patrones",
                            f"¿Qué sigue en la secuencia {a}, {a * 2}, {a * 4}, …?",
                            a * 8,
                            "Cada término es el doble del anterior.",
                        ),
                        (
                            "Deducción",
                            f"Ana tiene {a} fichas. Leo tiene {b} más que Ana y Sol tiene 2 menos que Leo. ¿Cuántas tiene Sol?",
                            a + b - 2,
                            f"Primero {a} + {b}; después resta 2.",
                        ),
                        (
                            "Proporcionalidad",
                            f"{b} entradas cuestan {b * 10} pesos. Al mismo precio, ¿cuánto cuestan {a} entradas?",
                            a * 10,
                            "Cada entrada cuesta 10 pesos.",
                        ),
                        (
                            "Porcentajes",
                            f"Un artículo cuesta {a * 10} pesos. Tiene un descuento del 10 %. ¿Cuántos pesos descuentan?",
                            a,
                            f"El 10 % de {a * 10} es {a * 10} ÷ 10.",
                        ),
                        (
                            "Organización",
                            f"Hay {a * b + 1} personas. En cada mesa caben {b}. ¿Cuántas mesas se necesitan como mínimo?",
                            a + 1,
                            f"{a} mesas admiten {a * b} personas; hace falta otra para la restante.",
                        ),
                        (
                            "Lógica temporal",
                            f"Un robot emite una señal cada {b} minutos. Acaba de emitir una. ¿Cuántos minutos pasarán hasta la cuarta señal siguiente?",
                            b * 4,
                            f"Hay cuatro intervalos de {b} minutos.",
                        ),
                        (
                            "Ciclos",
                            f"Las luces siguen el ciclo rojo, azul, verde. La primera es roja. ¿Qué color ocupa el lugar {3 * a + 2}?",
                            "azul",
                            "Cada bloque tiene tres luces. Después de los bloques completos, la segunda es azul.",
                        ),
                        (
                            "Promedio",
                            f"Tres rondas dan {a * 2}, {a * 2 + 2} y {a * 2 + 4} puntos. ¿Cuál es el promedio?",
                            a * 2 + 2,
                            "Las cantidades están igualmente separadas: el promedio es la del centro.",
                        ),
                        (
                            "Conteo lógico",
                            f"Para unir {a} estaciones en una sola fila, se pone un cable entre cada par de estaciones vecinas. ¿Cuántos cables se necesitan?",
                            a - 1,
                            "En una fila hay un espacio entre cada dos vecinos: uno menos que estaciones.",
                        ),
                        (
                            "Razonamiento",
                            f"Una máquina entrega {b} fichas por turno. Ya tienes {a}. ¿Cuántas tendrás después de 3 turnos?",
                            a + 3 * b,
                            f"A las {a} iniciales añade 3 × {b}.",
                        ),
                    ]
                for t, (topic, text, answer, explanation) in enumerate(rows):
                    rng = random.Random(f"{code}-{d}-{k}-{t}")
                    if isinstance(answer, int):
                        candidates = [
                            answer - 2,
                            answer - 1,
                            answer + 1,
                            answer + 2,
                            answer + 3,
                            answer + 5,
                        ]
                        candidates = list(
                            dict.fromkeys(
                                x for x in candidates if x >= 0 and x != answer
                            )
                        )
                        rng.shuffle(candidates)
                        options = [str(answer)] + [str(x) for x in candidates[:3]]
                    else:
                        options = ["azul", "rojo", "verde", "amarillo"]
                    rng.shuffle(options)
                    yield {
                        "seed_key": f"{code}-{d}-{k}-{t}",
                        "category_code": code,
                        "difficulty": d,
                        "topic": topic,
                        "text": text,
                        "options": options,
                        "correct": options.index(str(answer)),
                        "explanation": explanation,
                    }
