from sqlalchemy.dialects.postgresql import insert

from backend.database import get_db
from backend.models.paradas import Parada as ParadaModel
from backend.stmAPI import STMAPIError, stm_client

## Script para actualizar la base de datos con las paradas del STM
def update_db_paradas():
    try:
        paradas_data = stm_client.get_busstops()
    except STMAPIError as e:
        print(f"Error al obtener las paradas del STM: {e}")
        return

    rows_by_id = {}
    for parada in paradas_data:
        calle_principal = parada.get("street1") or parada.get("calle_principal")
        esquina = parada.get("street2") or parada.get("esquina")
        calles = (calle_principal, esquina)
        if any("CALLE FICTICIA" in calle.upper() for calle in calles if calle):
            continue
        if not calle_principal or not esquina:
            continue

        location = parada.get("location") or {}
        coordinates = location.get("coordinates") or []
        if len(coordinates) < 2:
            latitud = parada.get("latitude", parada.get("latitud"))
            longitud = parada.get("longitude", parada.get("longitud"))
        else:
            longitud, latitud = coordinates[:2]

        if latitud is None or longitud is None:
            continue

        parada_id = parada.get("busstopId", parada.get("stop_id", parada.get("id")))
        if parada_id is None:
            continue

        rows_by_id[parada_id] = {
            "id": parada_id,
            "calle_principal": calle_principal,
            "esquina": esquina,
            "latitud": latitud,
            "longitud": longitud,
        }

    rows = list(rows_by_id.values())
    if not rows:
        print("No hay paradas válidas para actualizar.")
        return

    db = next(get_db())
    table = ParadaModel.__table__
    statement = insert(table).values(rows)
    statement = statement.on_conflict_do_update(
        index_elements=[table.c.id],
        set_={
            "calle_principal": statement.excluded.calle_principal,
            "esquina": statement.excluded.esquina,
            "latitud": statement.excluded.latitud,
            "longitud": statement.excluded.longitud,
        },
    )
    db.execute(statement)
    db.commit()
    print(f"Se actualizaron {len(rows)} paradas en la base de datos.")


if __name__ == "__main__":
    update_db_paradas()