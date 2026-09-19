const registerForm = document.getElementById("register-form");
const registerMessage = document.getElementById("register-message");

document.querySelectorAll(".password-toggle").forEach((toggle) => {
	toggle.addEventListener("click", () => {
		const passwordInput = document.getElementById(toggle.dataset.target);
		const isPassword = passwordInput.type === "password";
		passwordInput.type = isPassword ? "text" : "password";
		toggle.querySelector("span").textContent = isPassword ? "visibility_off" : "visibility";
	});
});

function showRegisterMessage(message, isError = true) {
	registerMessage.textContent = message;
	registerMessage.classList.toggle("text-error", isError);
	registerMessage.classList.toggle("text-secondary", !isError);
}

registerForm?.addEventListener("submit", async (event) => {
	event.preventDefault();

	const submitButton = registerForm.querySelector("button[type='submit']");
	const nombre = document.getElementById("register-name").value.trim();
	const email = document.getElementById("register-email").value.trim();
	const password = document.getElementById("password-input").value;
	const confirmPassword = document.getElementById("confirm-password-input").value;

	if (password !== confirmPassword) {
		showRegisterMessage("Las contraseñas no coinciden.");
		return;
	}

	submitButton.disabled = true;
	showRegisterMessage("Creando cuenta...", false);

	try {
		const response = await fetch("/api/v1/register", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ nombre, email, password }),
		});

		const data = await response.json().catch(() => ({}));

		if (!response.ok) {
			throw new Error(data.detail || "No se pudo crear la cuenta.");
		}

		localStorage.setItem("access_token", data.access_token);
		localStorage.setItem("user", JSON.stringify(data.user));
		showRegisterMessage("Cuenta creada.", false);
		window.location.href = "/perfil";
	} catch (error) {
		showRegisterMessage(error.message || "No se pudo crear la cuenta.");
	} finally {
		submitButton.disabled = false;
	}
});
