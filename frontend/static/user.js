document.addEventListener("DOMContentLoaded", async () => {
	const token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");

	if (!token) {
		window.location.href = "/login";
		return;
	}

	try {
		const response = await fetch("/api/v1/users/me", {
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});

		if (response.status === 401) {
			localStorage.removeItem("access_token");
			localStorage.removeItem("user");
			sessionStorage.removeItem("access_token");
			sessionStorage.removeItem("user");
			window.location.href = "/login";
			return;
		}

		if (!response.ok) {
			throw new Error(`Error ${response.status}`);
		}

		const currentUser = await response.json();
		const registeredDate = currentUser.fecha_registro
			? new Date(currentUser.fecha_registro).toLocaleDateString("es-UY")
			: "-";

		document.getElementById("user-name").textContent = currentUser.nombre || "Usuario";
		document.getElementById("user-level").textContent = `Colaborador Nvl. ${currentUser.level ?? 1}`;
		document.getElementById("user-exp").textContent = currentUser.exp ?? 0;
		document.getElementById("user-level-stat").textContent = currentUser.level ?? 1;
		document.getElementById("user-registered").textContent = registeredDate;

		const storage = localStorage.getItem("access_token") ? localStorage : sessionStorage;
		const userForStorage = { ...currentUser };
		delete userForStorage.email;
		storage.setItem("user", JSON.stringify(userForStorage));
	} catch (error) {
		console.error("No se pudieron cargar los datos del usuario:", error);
	}
});
