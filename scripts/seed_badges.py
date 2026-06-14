"""
Run once after initial setup to seed badges and collections:
    python -m scripts.seed_badges
"""
import asyncio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.models import BEANIE_DOCUMENT_MODELS
from app.models.badge import Badge, BadgeRequirement, UserBadge
from app.models.collection import Collection
from app.core.constants import BadgeLevel


async def seed():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["waygo"]
    await init_beanie(database=db, document_models=BEANIE_DOCUMENT_MODELS)

    # -- Fetch place IDs by slug --
    from app.models.place import Place

    def pid(slug: str) -> str | None:
        return None  # resolved below after async fetch

    place_slugs = [
        "ventana-al-mundo",
        "gran-malecon-del-rio",
        "museo-del-caribe",
        "castillo-de-salgar",
    ]
    places_by_slug: dict[str, str] = {}
    for slug in place_slugs:
        p = await Place.find_one(Place.slug == slug)
        if p:
            places_by_slug[slug] = str(p.id)
            print(f"  Found: {slug} -> {p.id}")
        else:
            print(f"  WARNING: place '{slug}' not found — run mongo-init.js first")

    # -- Badges --
    badge_conocedor_1 = Badge(
        name="Conocedor Barranquilla Nivel 1",
        slug="conocedor-barranquilla-1",
        description="Visita 4 lugares emblemáticos de Barranquilla",
        points=100,
        city="Barranquilla",
        country="Colombia",
        level=BadgeLevel.LEVEL_1,
    )
    await badge_conocedor_1.save()
    print(f"Badge created: {badge_conocedor_1.name}")

    badge_conocedor_2 = Badge(
        name="Conocedor Barranquilla Nivel 2",
        slug="conocedor-barranquilla-2",
        description="Explorador avanzado de Barranquilla (requiere Nivel 1 + más lugares)",
        points=200,
        city="Barranquilla",
        country="Colombia",
        level=BadgeLevel.LEVEL_2,
    )
    await badge_conocedor_2.save()

    badge_explorer_colombia = Badge(
        name="Explorador Colombia",
        slug="explorador-colombia",
        description="Visita lugares en al menos 3 ciudades de Colombia",
        points=300,
        country="Colombia",
        level=BadgeLevel.EXPLORER,
    )
    await badge_explorer_colombia.save()

    # -- Badge Requirements --
    req_1_places = [v for k, v in places_by_slug.items()]
    if req_1_places:
        req = BadgeRequirement(badge_id=str(badge_conocedor_1.id), place_ids=req_1_places)
        await req.save()
        print(f"Requirement set for {badge_conocedor_1.name}: {len(req_1_places)} places")

    # -- Collections --
    col_barranquilla = Collection(
        name="Imperdibles de Barranquilla",
        slug="imperdibles-barranquilla",
        description="Los 4 lugares que no puedes perderte en la Arenosa",
        points=50,
        place_ids=req_1_places,
    )
    await col_barranquilla.save()
    print(f"Collection created: {col_barranquilla.name}")

    col_caribe = Collection(
        name="Ruta Caribe",
        slug="ruta-caribe",
        description="Explora la costa caribe colombiana",
        points=100,
        place_ids=req_1_places[:2],
    )
    await col_caribe.save()

    print("\n✓ Seed complete.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
