document.addEventListener("DOMContentLoaded", async () => {
	const logoutButton = document.getElementById("logout-button");
	const comingSoonMessage = document.getElementById("coming-soon-message");

	const clearSession = () => {
		localStorage.removeItem("access_token");
		localStorage.removeItem("user");
		sessionStorage.removeItem("access_token");
		sessionStorage.removeItem("user");
	};

	const getAccessToken = () => {
		return localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
	};

	const getTokenStorage = () => {
		return localStorage.getItem("access_token") ? localStorage : sessionStorage;
	};

	const logoutAndRedirect = async () => {
		try {
			await fetch("/api/v1/logout", {
				method: "POST",
				credentials: "include",
			});
		} catch (error) {
			console.error("No se pudo invalidar la sesión:", error);
		} finally {
			clearSession();
			window.location.href = "/login";
		}
	};

	const refreshAccessToken = async () => {
		const response = await fetch("/api/v1/refresh", {
			method: "POST",
			credentials: "include",
		});

		if (!response.ok) {
			return false;
		}

		const data = await response.json();
		getTokenStorage().setItem("access_token", data.access_token);
		return true;
	};

	const fetchCurrentUser = (accessToken) => {
		return fetch("/api/v1/users/me", {
			headers: {
				Authorization: `Bearer ${accessToken}`,
			},
		});
	};

	if (!getAccessToken()) {
		window.location.href = "/login";
		return;
	}

	document.querySelectorAll("[data-coming-soon]").forEach((button) => {
		button.addEventListener("click", () => {
			if (!comingSoonMessage) return;
			comingSoonMessage.classList.remove("hidden");
			window.clearTimeout(comingSoonMessage.hideTimeout);
			comingSoonMessage.hideTimeout = window.setTimeout(() => {
				comingSoonMessage.classList.add("hidden");
			}, 2500);
		});
	});

	logoutButton?.addEventListener("click", async () => {
		logoutButton.disabled = true;
		await logoutAndRedirect();
	});

	try {
		let response = await fetchCurrentUser(getAccessToken());

		if (response.status === 401) {
			const refreshed = await refreshAccessToken();

			if (!refreshed) {
				await logoutAndRedirect();
				return;
			}

			response = await fetchCurrentUser(getAccessToken());
		}

		if (response.status === 401) {
			await logoutAndRedirect();
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
