const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

function showLoginMessage(message, isError = true) {
	loginMessage.textContent = message;
	loginMessage.classList.toggle("text-error", isError);
	loginMessage.classList.toggle("text-secondary", !isError);
}

loginForm?.addEventListener("submit", async (event) => {
	event.preventDefault();

	const submitButton = loginForm.querySelector("button[type='submit']");
	const email = document.getElementById("login-email").value.trim();
	const password = document.getElementById("password-input").value;
	const keepSession = loginForm.querySelector("input[type='checkbox']").checked;

	submitButton.disabled = true;
	showLoginMessage("Iniciando sesión...", false);

	try {
		const response = await fetch("/api/v1/login", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ email, password }),
		});

		const data = await response.json().catch(() => ({}));

		if (!response.ok) {
			throw new Error(data.detail || "No se pudo iniciar sesión.");
		}

		const storage = keepSession ? localStorage : sessionStorage;
		const otherStorage = keepSession ? sessionStorage : localStorage;
		otherStorage.removeItem("access_token");
		otherStorage.removeItem("user");
		storage.setItem("access_token", data.access_token);
		storage.setItem("user", JSON.stringify(data.user));

		showLoginMessage("Sesión iniciada.", false);
		window.location.href = "/perfil";
	} catch (error) {
		showLoginMessage(error.message || "No se pudo iniciar sesión.");
	} finally {
		submitButton.disabled = false;
	}
});
