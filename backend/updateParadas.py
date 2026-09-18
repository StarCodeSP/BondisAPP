from backend.database import Base, engine, get_db
from backend.models.paradas import Parada as ParadaModel
from backend.schemas.paradas import Parada
from backend.stmAPI import STMAPIError, stm_client

## Script para actualizar la base de datos con las paradas del STM
def update_db_paradas():
    try:
        paradas_data = stm_client.get_busstops()
    except STMAPIError as e:
        print(f"Error al obtener las paradas del STM: {e}")
        return

    db = next(get_db())
    actualizadas = 0
    for parada in paradas_data:
        calle_principal = parada.get("street1", parada.get("calle_principal", ""))
        esquina = parada.get("street2", parada.get("esquina", ""))
        calles = (calle_principal, esquina)
        if any("CALLE FICTICIA" in calle.upper() for calle in calles if calle):
            continue

        location = parada.get("location") or {}
        coordinates = location.get("coordinates") or []
        if len(coordinates) < 2:
            latitud = parada.get("latitude", parada.get("latitud"))
            longitud = parada.get("longitude", parada.get("longitud"))
        else:
            longitud, latitud = coordinates[:2]

        if latitud is None or longitud is None:
            print(f"Se omite parada sin coordenadas: {parada}")
            continue

        parada_obj = ParadaModel(
            id=parada.get("busstopId", parada.get("stop_id", parada.get("id"))),
            calle_principal=calle_principal,
            esquina=esquina,
            latitud=latitud,
            longitud=longitud,
        )
        db.merge(parada_obj)  # merge para actualizar o insertar
        print(f"Se actualizó o insertó la parada: {parada_obj}")
        actualizadas += 1
    db.commit()
    print(f"Se actualizaron {actualizadas} paradas en la base de datos.")


if __name__ == "__main__":
    update_db_paradas()