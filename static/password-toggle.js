document.querySelectorAll('input[type="password"]').forEach((input) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "button light";
    button.textContent = "Mostrar contraseña";
    button.setAttribute("aria-controls", input.id);

    button.addEventListener("click", () => {
        const mostrar = input.type === "password";

        input.type = mostrar ? "text" : "password";
        button.textContent = mostrar
            ? "Ocultar contraseña"
            : "Mostrar contraseña";
    });

    input.insertAdjacentElement("afterend", button);
});