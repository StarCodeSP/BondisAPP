const getAuthStorage = () => {
    return localStorage.getItem("access_token") ? localStorage : sessionStorage;
};

const clearSession = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("user");
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

const refreshAccessToken = async (storage) => {
    try {
        const response = await fetch("/api/v1/refresh", {
            method: "POST",
            credentials: "include",
        });

        if (!response.ok) return false;

        const data = await response.json();
        storage.setItem("access_token", data.access_token);
        return true;
    } catch (error) {
        console.error("No se pudo refrescar el token:", error);
        return false;
    }
};

const sendReport = (token, payload) => {
    return fetch("/api/v1/reportar_experiencia", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
    });
};

async function reportarExperiencia(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const ratingGeneral = Number(form.querySelector("#generalRatingValue").value);
    const ratingLimpieza = Number(form.querySelector("#cleanRatingValue").value);
    const ocupacion = form.querySelector('input[name="occupancy"]:checked');
    const numCoche = Number(form.querySelector("#busNumber").value);
    const storage = getAuthStorage();
    let token = storage.getItem("access_token");
    const user = JSON.parse(storage.getItem("user") || "null");
    const usuarioId = user?.id;

    if (!token || !usuarioId) {
        window.location.href = "/login";
        return;
    }

    const payload = {
        usuario_id: usuarioId,
        comentario: form.querySelector("#comments").value.trim() || null,
        calificacion_general: ratingGeneral,
        calificacion_limpieza: ratingLimpieza,
        calificacion_lleno: ocupacion ? ocupacion.value : "",
        num_coche: numCoche,
    };

    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
        let response = await sendReport(token, payload);

        if (response.status === 401) {
            const refreshed = await refreshAccessToken(storage);

            if (!refreshed) {
                await logoutAndRedirect();
                return;
            }

            token = storage.getItem("access_token");
            response = await sendReport(token, payload);
        }

        if (response.status === 401) {
            await logoutAndRedirect();
            return;
        }

        if (response.status === 403) {
            await logoutAndRedirect();
            return;
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || "Error al enviar el reporte");
        }

        alert("Reporte enviado con éxito");
        form.reset();
    } catch (error) {
        console.error("Error:", error);
        alert(error.message || "Error al enviar el reporte");
    } finally {
        submitButton.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reportForm');
    form.addEventListener('submit', reportarExperiencia);
});
