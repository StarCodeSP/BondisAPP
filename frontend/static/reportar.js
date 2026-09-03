function reportarExperiencia(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const usuarioId = localStorage.getItem('usuario_id');
    const ratingGeneral = Number(form.querySelector('#generalRatingValue').value);
    const ratingLimpieza = Number(form.querySelector('#cleanRatingValue').value);
    const ocupacion = form.querySelector('input[name="occupancy"]:checked');
    const numCoche = Number(form.querySelector('#busNumber').value);

    if (!usuarioId) {
        alert('Debes iniciar sesión antes de enviar un reporte.');
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
        'Content-Type': 'application/json'
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
