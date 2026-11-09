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

const sendReport = (token, payload, reportType) => {
    const endpoint = reportType === "stop"
        ? "/api/v1/reportar_parada_experiencia"
        : "/api/v1/reportar_experiencia";

    return fetch(endpoint, {
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
    const reportType = form.dataset.reportType || "bus";
    const ratingGeneral = Number(form.querySelector("#generalRatingValue").value);
    const ocupacion = form.querySelector('input[name="occupancy"]:checked');
    const storage = getAuthStorage();
    let token = storage.getItem("access_token");
    const user = JSON.parse(storage.getItem("user") || "null");
    const usuarioId = user?.id;

    if (!token || !usuarioId) {
        window.location.href = "/login";
        return;
    }

    if (reportType === "stop" && !form.querySelector("#stopId").value) {
        alert("Seleccioná una parada de la lista de sugerencias");
        return;
    }

    const payload = {
        usuario_id: usuarioId,
        comentario: form.querySelector("#comments").value.trim() || null,
        calificacion_general: ratingGeneral,
        calificacion_lleno: ocupacion ? ocupacion.value : "",
    };

    if (reportType === "stop") {
        payload.calificacion_seguridad = Number(form.querySelector("#safetyRatingValue").value);
        payload.id_parada = Number(form.querySelector("#stopId").value);
    } else {
        payload.calificacion_limpieza = Number(form.querySelector("#cleanRatingValue").value);
        payload.num_coche = Number(form.querySelector("#busNumber").value);
    }

    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
        let response = await sendReport(token, payload, reportType);

        if (response.status === 401) {
            const refreshed = await refreshAccessToken(storage);

            if (!refreshed) {
                await logoutAndRedirect();
                return;
            }

            token = storage.getItem("access_token");
            response = await sendReport(token, payload, reportType);
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
    const reportTypeButtons = form.querySelectorAll('.report-type-btn');
    const busFields = document.getElementById('busReportFields');
    const stopFields = document.getElementById('stopReportFields');
    const safetySection = document.getElementById('safetyRatingSection');
    const cleanSection = document.getElementById('cleanRatingSection');
    const busNumber = document.getElementById('busNumber');
    const stopSearch = document.getElementById('stopSearch');
    const stopId = document.getElementById('stopId');
    const stopOptions = document.getElementById('stopOptions');
    const cleanRating = document.getElementById('cleanRatingValue');
    const safetyRating = document.getElementById('safetyRatingValue');

    const setReportType = (reportType) => {
        const isStop = reportType === 'stop';
        form.dataset.reportType = reportType;
        busFields.classList.toggle('hidden', isStop);
        busFields.classList.toggle('flex', !isStop);
        stopFields.classList.toggle('hidden', !isStop);
        stopFields.classList.toggle('flex', isStop);
        safetySection.classList.toggle('hidden', !isStop);
        safetySection.classList.toggle('flex', isStop);
        cleanSection.classList.toggle('hidden', isStop);
        cleanSection.classList.toggle('flex', !isStop);
        busNumber.required = !isStop;
        stopSearch.required = isStop;
        cleanRating.required = !isStop;
        safetyRating.required = isStop;

        reportTypeButtons.forEach((button) => {
            const active = button.dataset.reportType === reportType;
            button.classList.toggle('bg-primary', active);
            button.classList.toggle('text-on-primary', active);
            button.classList.toggle('text-on-surface-variant', !active);
        });
    };

    reportTypeButtons.forEach((button) => {
        button.addEventListener('click', () => setReportType(button.dataset.reportType));
    });

    fetch('/api/v1/paradas')
        .then((response) => {
            if (!response.ok) throw new Error('No se pudieron cargar las paradas');
            return response.json();
        })
        .then((stops) => {
            stopOptions.replaceChildren();
            stops
                .filter((stop) => stop.activa)
                .sort((first, second) => first.calle_principal.localeCompare(second.calle_principal))
                .forEach((stop) => {
                    const label = `#${stop.id} - ${stop.calle_principal} y ${stop.esquina}`;
                    stopOptions.appendChild(new Option(label));
                });
        })
        .catch((error) => {
            console.error('Error al cargar las paradas:', error);
            stopOptions.replaceChildren(new Option('No se pudieron cargar las paradas'));
        });

    stopSearch.addEventListener('input', () => {
        const selectedOption = Array.from(stopOptions.options).find(
            (option) => option.value === stopSearch.value,
        );
        stopId.value = selectedOption ? stopSearch.value.match(/^#(\d+)/)[1] : '';
    });

    setReportType('bus');
    form.addEventListener('submit', reportarExperiencia);
});
