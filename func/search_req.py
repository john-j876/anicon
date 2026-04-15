from jikanpy import AioJikan
import json
import aiohttp
import asyncio
from pathlib import Path
from widgets.firstpage import resource_path
import logging
import os

# -------------------------------
# Cache directories (fixed)
# -------------------------------

cache_dir = Path(os.environ["LOCALAPPDATA"]) / "Anicon"

img_cache = cache_dir / "images"
data_cache = cache_dir / "data"

cache_dir.mkdir(parents=True,exist_ok=True)
img_cache.mkdir(parents=True, exist_ok=True)
data_cache.mkdir(parents=True, exist_ok=True)

top_anime_cache = data_cache / "top_anime.json"
searched_anime_cache = data_cache / "searches.json"
page_anime_cache = data_cache / "pages.json"
anim_info_cache = data_cache / "anime_info.json"
anim_episode_cache = data_cache / "episode_info.json"

# -------------------------------
# LOG FILE SETUP
# -------------------------------

log_file = cache_dir / "errors.log"

logging.basicConfig(
    filename=str(log_file),
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# -------------------------------
# GLOBAL SESSION
# -------------------------------

session = None


async def get_session():
    global session

    if session is None or session.closed:
        timeout = aiohttp.ClientTimeout(total=20)
        session = aiohttp.ClientSession(timeout=timeout)

    return session


# -------------------------------
# IMAGE CACHE
# -------------------------------

async def cache_image(url, filename):

    path = img_cache / filename

    if path.exists():
        return str(path)

    try:
        session = await get_session()

        async with session.get(url) as resp:

            if resp.status == 200:
                data = await resp.read()
                path.write_bytes(data)
                return str(path)

    except Exception as e:
        logging.error(f"image cache failed: {e}", exc_info=True)

    return url


# -------------------------------
# PROCESS API DATA
# -------------------------------

async def load_api_data(entry):

    data_e = []

    entries = entry.get("data", [])

    if isinstance(entries, dict):
        entries = [entries]

    tasks = []

    for data in entries:

        anime_id = data.get("mal_id")

        title = (
            data.get("title_english")
            or data.get("title")
            or data.get("title_japanese")
            or "no title"
        )

        image_url = (
            data.get("images", {})
            .get("jpg", {})
            .get("large_image_url")
        )

        story = data.get("synopsis", "")

        filename = f"{anime_id}.jpg"

        if image_url:
            tasks.append(cache_image(image_url, filename))
        else:
            tasks.append(asyncio.sleep(0))

        data_e.append({
            "id": anime_id,
            "title": title,
            "image": filename,
            "story": story,

            "title_japanese": data.get("title_japanese"),
            "type": data.get("type"),
            "episodes": data.get("episodes"),
            "status": data.get("status"),
            "duration": data.get("duration"),
            "score": data.get("score"),
            "rank": data.get("rank"),
            "popularity": data.get("popularity"),
            "year": data.get("year"),
            "season": data.get("season"),
            "rating": data.get("rating"),

            "genres": [g.get("name") for g in data.get("genres", [])],
            "studios": [s.get("name") for s in data.get("studios", [])],
            "themes": [t.get("name") for t in data.get("themes", [])],
        })

    images = await asyncio.gather(*tasks)

    for i, img in enumerate(images):
        data_e[i]["image"] = img

    return data_e


# -------------------------------
# EPISODE INFO
# -------------------------------

async def anime_episode_info(id=None, ep_id=None):

    if not ep_id:
        return []

    async with AioJikan() as jikan:
        try:
            result = await jikan.anime_episode_by_id(
                anime_id=id,
                episode_id=ep_id
            )

            fin = await load_api_data(result)

            with anim_episode_cache.open("w", encoding="utf-8") as f:
                json.dump(fin[:20], f, ensure_ascii=False, indent=2)

            return fin

        except Exception as e:
            logging.error(f"episode fallback: {e}", exc_info=True)

            if anim_episode_cache.exists() and anim_episode_cache.stat().st_size > 0:
                try:
                    with anim_episode_cache.open("r", encoding="utf-8") as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    pass

            return []


# -------------------------------
# SEARCH
# -------------------------------

async def anime_search(query=None):

    if not query:
        return []

    async with AioJikan() as jikan:

        try:
            result = await jikan.search("anime", query)

            fin = await load_api_data(result)

            with searched_anime_cache.open("w", encoding="utf-8") as f:
                json.dump(fin[:20], f, ensure_ascii=False, indent=2)

            return fin

        except Exception as e:
            logging.error(f"search fallback: {e}", exc_info=True)

            if searched_anime_cache.exists():
                with searched_anime_cache.open("r", encoding="utf-8") as f:
                    return json.load(f)

            return []


# -------------------------------
# TOP ANIME
# -------------------------------

async def top_anime():

    async with AioJikan() as jikan:

        try:
            result = await jikan.top("anime")

            fin = await load_api_data(result)

            with top_anime_cache.open("w", encoding="utf-8") as f:
                json.dump(fin, f, ensure_ascii=False, indent=2)

            return fin

        except Exception as e:
            logging.error(f"top anime fallback: {e}", exc_info=True)

            if top_anime_cache.exists():
                with top_anime_cache.open("r", encoding="utf-8") as f:
                    return json.load(f)

            return []


# -------------------------------
# ANIME INFO
# -------------------------------
async def anime_info(query=None):

    if not query:
        return []

    # Load existing cache
    cache = {}
    if anim_info_cache.exists():
        try:
            with anim_info_cache.open("r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    # If already cached return immediately
    if str(query) in cache:
        return cache[str(query)]

    try:
        async with AioJikan() as jikan:
            result = await jikan.anime(id=query, extension="episodes")

        fin = await load_api_data(result)

        # Save using anime id as key
        cache[str(query)] = fin

        with anim_info_cache.open("w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

        return fin

    except Exception as e:
        logging.error(f"anime info fallback: {e}", exc_info=True)

        # fallback to cache if available
        return cache.get(str(query), [])
# -------------------------------
# PAGED ANIME
# -------------------------------

async def anime_page(page):

    async with AioJikan() as jikan:

        try:
            result = await jikan.top("anime", page=page)

            fin = await load_api_data(result)

            with page_anime_cache.open("w", encoding="utf-8") as f:
                json.dump(fin, f, ensure_ascii=False, indent=2)

            return fin

        except Exception as e:
            logging.error(f"page fallback: {e}", exc_info=True)

            if page_anime_cache.exists():
                with page_anime_cache.open("r", encoding="utf-8") as f:
                    return json.load(f)

            return []