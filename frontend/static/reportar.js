function reportarExperiencia(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const ratingGeneral = Number(form.querySelector('#generalRatingValue').value);
    const ratingLimpieza = Number(form.querySelector('#cleanRatingValue').value);
    const ocupacion = form.querySelector('input[name="occupancy"]:checked');
    const numCoche = Number(form.querySelector('#busNumber').value);
    const storage = localStorage.getItem("access_token")
    ? localStorage
    : sessionStorage;

    const token = storage.getItem("access_token");
    const user = JSON.parse(storage.getItem("user") || "null");
    const usuarioId = user?.id;

    if (!token || !usuarioId) {
    window.location.href = "/login";
    return;
    }

    const payload = {
        usuario_id: usuarioId,
        comentario: form.querySelector('#comments').value.trim() || null,
        calificacion_general: ratingGeneral,
        calificacion_limpieza: ratingLimpieza,
        calificacion_lleno: ocupacion ? ocupacion.value : '',
        num_coche: numCoche
    };

    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    fetch('/api/v1/reportar_experiencia', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
})
.then(response => {
    if (!response.ok) {
        return response.json().then(error => {
            throw new Error(error.detail || 'Error al enviar el reporte');
        });
    }
    return response.json();
})
.then(() => {
    alert('Reporte enviado con éxito');
    form.reset();
})
.catch(error => {
    console.error('Error:', error);
    alert(error.message);
})
.finally(() => {
    submitButton.disabled = false;
});
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reportForm');
    form.addEventListener('submit', reportarExperiencia);
});
