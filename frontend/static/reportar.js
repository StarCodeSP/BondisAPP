// Codigo de ejemplo para reportar una parada (Todavia no funcional, no recibe datos del frontend)
let num_coche = 0;
var comentario = "";
let calificacion_limpieza = 0;
let calificacion_general = 0;
var calificación_lleno = 0;
var user_id = "";

function reportarExperiencia() {
fetch('/api/v1/reportar_experiencia', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user_id: user_id,
        comentario: comentario, // Reemplaza con el ID de la parada que deseas reportar
        calificacion_general: calificacion_general,
        calificación_lleno: calificación_lleno,
        calificacion_limpieza: calificacion_limpieza,
        num_coche: num_coche,
    })
})
.then(response => {
    if (response.ok) {
        alert('Reporte enviado con éxito');
    }
    else {
        alert('Error al enviar el reporte');
    }
})
.catch(error => {
    console.error('Error:', error);
    alert('Error al enviar el reporte');
});
};
