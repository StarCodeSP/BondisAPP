// Codigo de ejemplo para reportar una parada (Todavia no funcional, no recibe datos del frontend)
let num_coche = 123;

function reportarExperiencia() {
fetch('/api/v1/reportar_experiencia', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        num_coche: num_coche, // Reemplaza con el ID de la parada que deseas reportar
        descripcion: 'La parada está en mal estado' // Reemplaza con la descripción del problema
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
