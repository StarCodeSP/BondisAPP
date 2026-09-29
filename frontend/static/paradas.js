document.addEventListener("DOMContentLoaded", () => {
  const nearbyStopsEl = document.getElementById("nearby-stops");
  const stopCountEl = document.getElementById("stop-count");
  const arrivalsContainerEl = document.getElementById("arrivals-container");
  const refreshBtn = document.getElementById("refresh-btn");
  const selectedStopNameEl = document.getElementById("selected-stop-name");
  const selectedStopSubtitleEl = document.getElementById("selected-stop-subtitle");
  const distanceBadgeEl = document.getElementById("distance-badge");
  const zoomMessageEl = document.getElementById("map-zoom-message");

  const fallbackLocation = { lat: -34.90328, lon: -56.18816 };
  const MAP_ZOOM_THRESHOLD = 13.5;
  const INITIAL_MAP_ZOOM = 18;
  let userLocation = fallbackLocation;
  let activeMap = null;
  let nearbyStops = [];
  let stopLayer = null;
  let userLocationMarker = null;
  let lastNearbyFetchKey = "";
  let isLoadingNearbyStops = false;
  let hasLoadedUserLocation = false;

  const getMapRadiusMeters = () => {
    if (!activeMap) return 800;

    const center = activeMap.getCenter();
    const corner = activeMap.getBounds().getNorthEast();
    const diagonalMeters = haversineDistance(center.lat, center.lng, corner.lat, corner.lng);
    return Math.max(800, diagonalMeters * 1.2);
  };

  const shouldLoadMoreStops = () => {
    if (!activeMap || nearbyStops.length === 0) return true;

    const bounds = activeMap.getBounds();
    const visibleStops = nearbyStops.filter((stop) => {
      if (!stop || stop.latitud == null || stop.longitud == null) return false;
      return bounds.contains(L.latLng(stop.latitud, stop.longitud));
    });

    if (activeMap.getZoom() >= MAP_ZOOM_THRESHOLD) {
      return visibleStops.length === 0;
    }

    return visibleStops.length < Math.min(nearbyStops.length, 6);
  };

  const syncZoomMessage = () => {
    if (!activeMap || !zoomMessageEl) return;
    const visible = activeMap.getZoom() < MAP_ZOOM_THRESHOLD;
    zoomMessageEl.style.display = visible ? "flex" : "none";
  };

  const updateUserLocationMarker = (lat, lon) => {
    if (!activeMap) return;

    const location = L.latLng(lat, lon);
    if (!userLocationMarker) {
      userLocationMarker = L.marker(location, {
        icon: L.divIcon({
          className: "current-location-marker",
          html: '<span class="material-symbols-outlined">my_location</span>',
          iconSize: [42, 42],
          iconAnchor: [21, 21],
        }),
        interactive: false,
        zIndexOffset: 1000,
      }).addTo(activeMap);
      return;
    }

    userLocationMarker.setLatLng(location);
  };

  const addLocateControl = () => {
    const LocateControl = L.Control.extend({
      options: { position: "topright" },

      onAdd: () => {
        const button = L.DomUtil.create("button", "leaflet-locate-control");
        button.type = "button";
        button.title = "Centrar en mi ubicación";
        button.setAttribute("aria-label", "Centrar en mi ubicación");
        button.innerHTML = '<span class="material-symbols-outlined">my_location</span>';

        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, "click", async () => {
          button.classList.add("is-loading");
          const location = await getUserLocation();
          userLocation = location;
          hasLoadedUserLocation = true;
          updateUserLocationMarker(location.lat, location.lon);
          activeMap.setView([location.lat, location.lon], Math.max(activeMap.getZoom(), MAP_ZOOM_THRESHOLD));
          button.classList.remove("is-loading");
        });

        return button;
      },
    });

    activeMap.addControl(new LocateControl());
  };

  const initMap = (lat, lon) => {
    const mapContainer = document.getElementById("leaflet-map");
    if (!mapContainer || typeof L === "undefined") return;

    if (activeMap) {
      activeMap.remove();
    }

    activeMap = L.map("leaflet-map", {
      zoomControl: true,
      scrollWheelZoom: true,
      attributionControl: true,
    }).setView([lat, lon], INITIAL_MAP_ZOOM);

    updateUserLocationMarker(lat, lon);
    addLocateControl();

L.tileLayer(
  "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=2e16eeef-17ff-41c8-851c-6ae7d6dbc501",
  {
    maxZoom: 20,
    attribution:
      '&copy; <a href="https://stadiamaps.com">Stadia Maps</a> &copy; OpenMapTiles &copy; OpenStreetMap contributors',
  }
).addTo(activeMap);

    stopLayer = L.layerGroup().addTo(activeMap);
    activeMap.on("zoomend moveend", () => {
      syncZoomMessage();

      if (shouldLoadMoreStops()) {
        loadNearbyStops({ isViewportRefresh: true });
      }
    });
    syncZoomMessage();
  };

  const haversineDistance = (lat1, lon1, lat2, lon2) => {
    const toRad = (value) => (value * Math.PI) / 180;
    const earthRadius = 6371000;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) *
        Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    return 2 * earthRadius * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  };

  const formatDistance = (meters) => {
    if (!Number.isFinite(meters)) return "Distancia";
    return meters < 1000 ? `${Math.round(meters)} m` : `${(meters / 1000).toFixed(1)} km`;
  };

  const formatStopName = (stop) => {
    const street = stop.calle_principal || stop.calle || stop.street || "Calle";
    const corner = stop.esquina || stop.esquina_1 || stop.corner || "esquina";
    return `${street} y ${corner}`;
  };

  const formatLine = (value) => {
    const raw = value ?? "";
    return String(raw).replace(/[^0-9A-Za-z]/g, "").toUpperCase() || "LÍNEA";
  };

  const normalizeArrival = (item) => {
    const line =
      item.linea ||
      item.line ||
      item.linha ||
      item.route_code ||
      item.route ||
      item.codigo ||
      item.bus ||
      "";

    const minutes =
      item.minutos ??
      item.minutes ??
      item.tiempo ??
      item.estimatedTime ??
      item.estimated_time ??
      item.arrival_time ??
      item.time ??
      null;

    const destination =
      item.destino ||
      item.destination ||
      item.trip_headsign ||
      item.ruta ||
      item.route_name ||
      "Ruta";

    const busId = item.idBus ?? item.id_bus ?? item.bus_id ?? item.num_coche ?? null;

    return {
      line: formatLine(line),
      busId,
      minutes: Number(minutes) ?? 0,
      destination: String(destination || "Ruta"),
      color: line && Number(String(line).replace(/\D/g, "")) % 2 === 0 ? "secondary" : "primary",
    };
  };

  const updateSelectedStop = (stop, distanceMeters) => {
    if (selectedStopNameEl) {
      selectedStopNameEl.textContent = stop ? formatStopName(stop) : "Buscando parada…";
    }

    if (selectedStopSubtitleEl) {
      selectedStopSubtitleEl.innerHTML = `
        <span class="material-symbols-outlined text-[14px]">directions_bus</span>
        ${stop ? "Estación principal" : "Esperando datos"}
      `;
    }

    if (distanceBadgeEl) {
      distanceBadgeEl.textContent = stop ? formatDistance(distanceMeters) : "Buscando...";
    }
  };

  const renderMapStops = () => {
    if (!activeMap || !stopLayer || !Array.isArray(nearbyStops)) return;
    stopLayer.clearLayers();

    if (activeMap.getZoom() < MAP_ZOOM_THRESHOLD) {
      syncZoomMessage();
      return;
    }

    nearbyStops.forEach((stop) => {
      const marker = L.circleMarker([stop.latitud, stop.longitud], {
        radius: 8,
        color: "#43e2d2",
        fillColor: "#43e2d2",
        fillOpacity: 0.9,
        weight: 2,
      }).addTo(stopLayer);

      marker.bindPopup(formatStopName(stop));
      marker.on("click", () => {
        const distance = haversineDistance(userLocation.lat, userLocation.lon, stop.latitud, stop.longitud);
        updateSelectedStop(stop, distance);
        loadArrivals(stop.id, stop);
      });
    });
  };

  const renderStops = (stops, lat, lon) => {
    if (!nearbyStopsEl) return;

    nearbyStops = Array.isArray(stops) ? stops : [];
    nearbyStopsEl.innerHTML = "";

    if (!stops || stops.length === 0) {
      stopCountEl.textContent = "Sin paradas cercanas";
      nearbyStopsEl.innerHTML = `
        <div class="w-full rounded-xl bg-surface-container p-4 text-on-surface-variant text-sm">
          No se encontraron paradas cercanas en este radio.
        </div>
      `;
      return;
    }

    stopCountEl.textContent = `${stops.length} encontradas`;

    stops.slice(0, 5).forEach((stop, index) => {
      const distance = haversineDistance(lat, lon, stop.latitud, stop.longitud);
      const button = document.createElement("button");
      button.type = "button";
      button.className = `flex items-center gap-2 px-3 py-2 rounded-xl ${
        index === 0 ? "bg-secondary/15 border border-secondary text-secondary" : "bg-surface-container hover:bg-surface-container-high text-on-surface"
      } shrink-0 transition-colors`;
      button.dataset.stopId = stop.id;
      button.innerHTML = `
        <span class="material-symbols-outlined text-[18px]">${
          index === 0 ? "location_on" : "pin_drop"
        }</span>
        <div class="flex flex-col items-start">
          <span class="font-body-sm font-semibold text-[14px] text-inherit leading-tight">
            ${formatStopName(stop)}
          </span>
          <span class="font-label-caps text-[10px] ${
            index === 0 ? "text-secondary" : "text-on-surface-variant"
          }">${index === 0 ? "Actual" : ""} ${formatDistance(distance)}</span>
        </div>
      `;

      button.addEventListener("click", () => {
        document.querySelectorAll("#nearby-stops button").forEach((node) => {
          node.className = "flex items-center gap-2 px-3 py-2 rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface shrink-0 transition-colors";
        });
        button.className = "flex items-center gap-2 px-3 py-2 rounded-xl bg-secondary/15 border border-secondary text-secondary shrink-0 transition-colors";

        const distance = haversineDistance(lat, lon, stop.latitud, stop.longitud);
        updateSelectedStop(stop, distance);
        loadArrivals(stop.id, stop);
      });

      if (activeMap && activeMap.getZoom() >= MAP_ZOOM_THRESHOLD) {
        renderMapStops();
      }

      nearbyStopsEl.appendChild(button);
    });
  };

  const getBusRatings = async (busId) => {
    if (busId == null || busId === "") return null;

    try {
      const response = await fetch(`/api/v1/experiencias/${encodeURIComponent(busId)}`);
      if (response.status === 404) return null;
      if (!response.ok) throw new Error(`Error ${response.status}`);

      const payload = await response.json();
      const experiences = Array.isArray(payload) ? payload : payload ? [payload] : [];
      const getAverage = (field) => {
        const values = experiences
          .map((experience) => Number(experience[field]))
          .filter((rating) => Number.isFinite(rating) && rating >= 1 && rating <= 5);

        if (values.length === 0) return null;
        return values.reduce((sum, value) => sum + value, 0) / values.length;
      };

      const latestExperience = experiences
        .filter((experience) => experience.calificacion_lleno)
        .sort((first, second) => {
          return new Date(second.fecha_reporte || 0) - new Date(first.fecha_reporte || 0);
        })[0];

      const general = getAverage("calificacion_general");
      const cleaning = getAverage("calificacion_limpieza");
      const occupancy = latestExperience?.calificacion_lleno || null;

      if (general === null && cleaning === null && occupancy === null) return null;

      return { general, cleaning, occupancy };
    } catch (error) {
      console.error(`Error cargando ratings del coche ${busId}:`, error);
      return null;
    }
  };

  const formatOccupancy = (value) => {
    const labels = {
      empty: "Vacío",
      moderate: "Moderado",
      full: "Lleno",
      very_full: "Muy lleno",
    };

    return labels[value] || value || "Sin datos";
  };

  const renderArrivals = async (items, selectedStop) => {
    if (!arrivalsContainerEl) return;

    arrivalsContainerEl.innerHTML = "";

    if (!items || items.length === 0) {
      arrivalsContainerEl.innerHTML = `
        <div class="w-full rounded-xl bg-surface-container p-4 text-on-surface-variant text-sm">
          No hay arribos disponibles para ${selectedStop ? formatStopName(selectedStop) : "esta parada"}.
        </div>
      `;
      return;
    }

    const normalized = items
      .map(normalizeArrival)
      .filter((item) => item.line || item.minutes !== null)
      .slice(0, 5);

    if (normalized.length === 0) {
      arrivalsContainerEl.innerHTML = `
        <div class="w-full rounded-xl bg-surface-container p-4 text-on-surface-variant text-sm">
          No hay datos de arribos para esta parada por el momento.
        </div>
      `;
      return;
    }

    const ratings = await Promise.all(normalized.map((item) => getBusRatings(item.busId)));

    normalized.forEach((item, index) => {
      const card = document.createElement("div");
      const accent = item.color === "secondary" ? "bg-secondary" : "bg-primary";
      const textColor = item.color === "secondary" ? "text-secondary" : "text-primary";
      const rating = ratings[index];
      const ratingDetails = rating
        ? `
          <span class="flex items-center gap-1">
            <span class="material-symbols-outlined text-primary text-[15px]">star</span>
            ${rating.general === null ? "Sin datos" : rating.general.toFixed(1)}
          </span>
          <span class="flex items-center gap-1">
            <span class="material-symbols-outlined text-primary text-[15px]">cleaning_services</span>
            ${rating.cleaning === null ? "Sin datos" : rating.cleaning.toFixed(1)}
          </span>
          <span class="flex items-center gap-1">
            <span class="material-symbols-outlined text-secondary text-[15px]">groups</span>
            ${formatOccupancy(rating.occupancy)}
          </span>
        `
        : "Sin datos";

      card.className = "w-full bg-surface-container rounded-xl p-4 flex flex-row items-center relative overflow-hidden shadow-md shadow-black/30";
      card.innerHTML = `
        <div class="absolute left-0 top-0 bottom-0 w-1 ${accent}"></div>
        <div class="flex flex-col justify-center items-center bg-surface-container-high rounded-lg p-2 min-w-[60px]">
          <span class="font-headline-lg-mobile text-headline-lg-mobile ${textColor}">${item.line || "-"}</span>
          <span class="font-label-caps text-label-caps text-on-surface-variant">LÍNEA</span>
        </div>
        <div class="flex flex-col ml-4 flex-1">
          <div class="flex items-center">
            <span class="font-title-md text-title-md text-on-surface">${item.destination}</span>
          </div>
          <div class="flex flex-wrap items-center gap-2 mt-2">
            <div class="flex items-center gap-1 bg-surface-container-high px-2 py-0.5 rounded-full">
              <span class="font-label-caps text-[10px] text-on-surface-variant">${item.minutes ?? "-"} min</span>
            </div>
            <span class="font-label-caps text-[10px] text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded-full">
              COCHE ${item.busId ?? "Sin dato"}
            </span>
            <div class="flex flex-wrap items-center gap-2 font-label-caps text-[10px] text-on-surface-variant">
              ${ratingDetails}
            </div>
          </div>
        </div>
        <div class="flex flex-col items-end ml-2">
          <span class="font-headline-lg text-headline-lg ${textColor}">${item.minutes ?? "-"}</span>
          <span class="font-label-caps text-label-caps text-on-surface-variant">MIN</span>
        </div>
      `;

      arrivalsContainerEl.appendChild(card);
    });
  };

  const getUserLocation = () => {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve(fallbackLocation);
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          });
        },
        () => resolve(fallbackLocation),
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });
  };

  const loadNearbyStops = async ({ isViewportRefresh = false } = {}) => {
    const location = hasLoadedUserLocation ? userLocation : await getUserLocation();
    const { lat, lon } = location;
    userLocation = { lat, lon };
    hasLoadedUserLocation = true;

    if (!activeMap) {
      initMap(lat, lon);
    }

    const centerLat = activeMap ? activeMap.getCenter().lat : lat;
    const centerLon = activeMap ? activeMap.getCenter().lng : lon;
    const radius = getMapRadiusMeters();
    const fetchKey = `${centerLat.toFixed(5)}:${centerLon.toFixed(5)}:${Math.round(radius)}`;

    if (!isViewportRefresh && fetchKey === lastNearbyFetchKey) {
      return;
    }

    if (isLoadingNearbyStops) {
      return;
    }

    isLoadingNearbyStops = true;
    lastNearbyFetchKey = fetchKey;

    try {
      const response = await fetch(
        `/api/v1/paradas/cercanas?lat=${centerLat}&lon=${centerLon}&radius=${radius}`
      );
      if (!response.ok) {
        throw new Error(`Error ${response.status}`);
      }

      const stops = await response.json();
      renderStops(stops, centerLat, centerLon);
      renderMapStops();

      if (stops && stops.length > 0) {
        const firstStop = stops[0];
        const firstDistance = haversineDistance(centerLat, centerLon, firstStop.latitud, firstStop.longitud);
        updateSelectedStop(firstStop, firstDistance);
        loadArrivals(firstStop.id, firstStop);
      }
    } catch (error) {
      console.error("Error cargando paradas cercanas:", error);
      if (nearbyStopsEl) {
        nearbyStopsEl.innerHTML = `
          <div class="w-full rounded-xl bg-surface-container p-4 text-on-surface-variant text-sm">
            No se pudieron cargar las paradas cercanas.
          </div>
        `;
      }
      if (stopCountEl) {
        stopCountEl.textContent = "Error";
      }
    } finally {
      isLoadingNearbyStops = false;
    }
  };

  const loadArrivals = async (stopId, selectedStop) => {
    if (!stopId) return;

    try {
      const response = await fetch(`/api/v1/transport/montevideo/arribos/${stopId}`);
      if (!response.ok) {
        throw new Error(`Error ${response.status}`);
      }

      const payload = await response.json();
      const arrivals = Array.isArray(payload) ? payload : payload?.arribos ?? payload?.data ?? [];
      renderArrivals(arrivals, selectedStop);
    } catch (error) {
      console.error("Error cargando arribos:", error);
      if (arrivalsContainerEl) {
        arrivalsContainerEl.innerHTML = `
          <div class="w-full rounded-xl bg-surface-container p-4 text-on-surface-variant text-sm">
            No se pudieron cargar los arribos de esta parada.
          </div>
        `;
      }
    }
  };

  if (refreshBtn) {
    refreshBtn.addEventListener("click", async () => {
      const icon = refreshBtn.querySelector("span");
      if (icon) {
        icon.classList.add("animate-spin");
      }
      await loadNearbyStops();
      if (icon) {
        setTimeout(() => icon.classList.remove("animate-spin"), 600);
      }
    });
  }

  loadNearbyStops();
});
