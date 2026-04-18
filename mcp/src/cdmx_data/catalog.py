from dataclasses import dataclass


@dataclass
class DatasetInfo:
    key: str
    slug: str
    resource_id: str | None
    track: str
    notes: str = ""


CATALOG: dict[str, DatasetInfo] = {
    # ── Movilidad ────────────────────────────────────────────────────────────
    "metro_afluencia_simple": DatasetInfo(
        key="metro_afluencia_simple",
        slug="afluencia-diaria-del-metro-cdmx",
        resource_id="0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb",
        track="movilidad",
        notes="Enero 2010 → presente, por línea y estación",
    ),
    "metro_afluencia_desglosada": DatasetInfo(
        key="metro_afluencia_desglosada",
        slug="afluencia-diaria-del-metro-cdmx",
        resource_id="cce544e1-dc6b-42b4-bc27-0d8e6eb3ed72",
        track="movilidad",
        notes="Desglosada por TMI/boleto/gratuidad",
    ),
    "metrobus_afluencia": DatasetInfo(
        key="metrobus_afluencia",
        slug="afluencia-diaria-de-metrobus-cdmx",
        resource_id="d122639e-a56a-4f26-a8b7-983464d11aaa",
        track="movilidad",
        notes="Desde julio 2005",
    ),
    "rtp_afluencia": DatasetInfo(
        key="rtp_afluencia",
        slug="afluencia-diaria-de-la-red-de-transporte-de-pasajeros",
        resource_id=None,
        track="movilidad",
        notes="Desde enero 2022 — resource_id se resuelve con package_show",
    ),
    "ste_afluencia": DatasetInfo(
        key="ste_afluencia",
        slug="afluencia-diaria-servicio-de-transportes-electricos",
        resource_id=None,
        track="movilidad",
        notes="Cablebús, Tren Ligero y Trolebús",
    ),
    "ecobici_viajes": DatasetInfo(
        key="ecobici_viajes",
        slug="afluencia-diaria-del-sistema-ecobici",
        resource_id=None,
        track="movilidad",
        notes="Viajes procesados de usuarios",
    ),
    "ciclovias": DatasetInfo(
        key="ciclovias",
        slug="infraestructura-vial-ciclista",
        resource_id=None,
        track="movilidad",
        notes="651 tramos (v11, marzo 2025)",
    ),
    "gtfs": DatasetInfo(
        key="gtfs",
        slug="gtfs-estatico-transporte-publico-cdmx",
        resource_id=None,
        track="movilidad",
        notes="Estándar GTFS, ZIP",
    ),
    # ── Seguridad ────────────────────────────────────────────────────────────
    "carpetas_fgj": DatasetInfo(
        key="carpetas_fgj",
        slug="carpetas-de-investigacion-fgj-de-la-ciudad-de-mexico",
        resource_id=None,
        track="seguridad",
        notes="Múltiples recursos por año — se resuelve con package_search",
    ),
    "victimas_fgj": DatasetInfo(
        key="victimas_fgj",
        slug="victimas-en-carpetas-de-investigacion-fgj",
        resource_id="d543a7b1-f8cb-439f-8a5c-e56c5479eeb5",
        track="seguridad",
        notes="Acumulado 2019 → presente",
    ),
    "hechos_transito": DatasetInfo(
        key="hechos_transito",
        slug="hechos-de-transito-reportados-por-ssc-base-ampliada-no-comparativa",
        resource_id=None,
        track="seguridad",
        notes="Desde 2018",
    ),
    "fotocivicas": DatasetInfo(
        key="fotocivicas",
        slug="fotocivicas",
        resource_id=None,
        track="seguridad",
        notes="Cumplimiento reglamento vehicular",
    ),
    "incidentes_c5": DatasetInfo(
        key="incidentes_c5",
        slug="incidentes-viales-c5",
        resource_id=None,
        track="seguridad",
        notes="Reportes ciudadanos C5",
    ),
    # ── Aire ─────────────────────────────────────────────────────────────────
    "calidad_aire": DatasetInfo(
        key="calidad_aire",
        slug="red-automatica-de-monitoreo-atmosferico",
        resource_id=None,
        track="aire",
        notes="PM2.5, O3, NO2, CO por estación SIMAT — resource_ids por contaminante",
    ),
    "estaciones_simat": DatasetInfo(
        key="estaciones_simat",
        slug="estaciones-simat",
        resource_id=None,
        track="aire",
        notes="Georreferenciadas",
    ),
    "meteorologia_simat": DatasetInfo(
        key="meteorologia_simat",
        slug="meteorologia-simat",
        resource_id=None,
        track="aire",
        notes="Temperatura, humedad, viento",
    ),
    # ── Servicios ────────────────────────────────────────────────────────────
    "locatel_0311": DatasetInfo(
        key="locatel_0311",
        slug="0311",
        resource_id=None,
        track="servicios",
        notes="Tiempos de respuesta por alcaldía",
    ),
    # ── Finanzas ─────────────────────────────────────────────────────────────
    "proveedores": DatasetInfo(
        key="proveedores",
        slug="padron-de-proveedores-vigente",
        resource_id=None,
        track="finanzas",
        notes="Personas físicas y morales vigentes",
    ),
    "deuda_publica": DatasetInfo(
        key="deuda_publica",
        slug="deuda-de-la-ciudad",
        resource_id=None,
        track="finanzas",
        notes="Por acreedor, tipo, intereses",
    ),
    "transparencia_presupuestaria": DatasetInfo(
        key="transparencia_presupuestaria",
        slug="presupuesto-de-egresos",
        resource_id=None,
        track="finanzas",
        notes="Gasto público",
    ),
    "ley_ingresos": DatasetInfo(
        key="ley_ingresos",
        slug="ley-de-ingresos",
        resource_id=None,
        track="finanzas",
        notes="Ingresos estimados",
    ),
    # ── Geo ──────────────────────────────────────────────────────────────────
    "colonias": DatasetInfo(
        key="colonias",
        slug="catalogo-de-colonias-datos-abiertos",
        resource_id=None,
        track="geo",
        notes="GeoJSON + Shapefile. Base de cualquier mapa.",
    ),
    "alcaldias": DatasetInfo(
        key="alcaldias",
        slug="alcaldias-cdmx",
        resource_id=None,
        track="geo",
        notes="16 polígonos oficiales",
    ),
    "agebs": DatasetInfo(
        key="agebs",
        slug="agebs-cdmx",
        resource_id=None,
        track="geo",
        notes="Áreas Geoestadísticas Básicas (unidad INEGI)",
    ),
    "cuadrantes_ssc": DatasetInfo(
        key="cuadrantes_ssc",
        slug="cuadrantes-de-seguridad",
        resource_id=None,
        track="geo",
        notes="847 polígonos de SSC",
    ),
    # ── Meta ─────────────────────────────────────────────────────────────────
    "catalogo_completo": DatasetInfo(
        key="catalogo_completo",
        slug="domaindatasets",
        resource_id=None,
        track="meta",
        notes="Lista TODOS los datasets del portal. Ideal para descubrimiento vía MCP.",
    ),
}
