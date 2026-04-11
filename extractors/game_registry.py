"""
Game registry: AppIDs for all tracked titles. FINAL CORRECTED VERSION.
Verify AppIDs at: https://store.steampowered.com/app/{appid}/
"""

GAME_REGISTRY = {
    # ── SIE PC Ports ──────────────────────────────────────────────
    "sie": {
        "God of War (2018)":              {"appid": 1593500, "release_pc": "2022-01-14"},
        "God of War Ragnarök":            {"appid": 2322010, "release_pc": "2024-09-19"},
        "Horizon Zero Dawn":              {"appid": 1151640, "release_pc": "2020-08-07"},
        "Horizon Forbidden West":         {"appid": 2420110, "release_pc": "2024-03-21"},
        "Marvel's Spider-Man Remastered": {"appid": 1817070, "release_pc": "2022-08-12"},
        "Marvel's Spider-Man: Miles Morales": {"appid": 1817190, "release_pc": "2022-11-18"},
        "The Last of Us Part I":          {"appid": 1888930, "release_pc": "2023-03-28"},
        "Helldivers 2":                   {"appid": 553850,  "release_pc": "2024-02-08"},
        "Returnal":                       {"appid": 1649240, "release_pc": "2023-02-15"},
        "Ratchet & Clank: Rift Apart":    {"appid": 1895880, "release_pc": "2023-07-26"},
    },

    # ── Bandai Namco ──────────────────────────────────────────────
    "bandai_namco": {
        "Elden Ring":                     {"appid": 1245620, "release_pc": "2022-02-25"},
        "Tekken 8":                       {"appid": 1778820, "release_pc": "2024-01-26"},
        "Dragon Ball FighterZ":           {"appid": 678950,  "release_pc": "2018-01-26"},
        "Dragon Ball: Sparking! Zero":    {"appid": 1790600, "release_pc": "2024-10-11"},
        "Ace Combat 7":                   {"appid": 502500,  "release_pc": "2020-01-01"},
        "Tales of Arise":                 {"appid": 740130, "release_pc": "2021-09-10"},
        "Gundam Breaker 4":               {"appid": 1672500, "release_pc": "2024-08-28"},
        "Little Nightmares II":           {"appid": 860510,  "release_pc": "2021-02-11"},
    },

    # ── Sega / Atlus ──────────────────────────────────────────────
    "sega_atlus": {
        "Like a Dragon: Infinite Wealth": {"appid": 2561580, "release_pc": "2024-01-26"},
        "Yakuza: Like a Dragon":          {"appid": 1235140, "release_pc": "2021-01-13"},
        "Persona 3 Reload":               {"appid": 2161700, "release_pc": "2024-02-02"},
        "Persona 4 Golden":               {"appid": 1113000, "release_pc": "2020-06-13"},
        "Persona 5 Royal":                {"appid": 1687950, "release_pc": "2022-10-21"},
        "Sonic Frontiers":                {"appid": 1237320, "release_pc": "2022-11-08"},
        "Sonic Superstars":               {"appid": 2022670, "release_pc": "2023-10-17"},
        "Two Point Campus":               {"appid": 1649080, "release_pc": "2022-08-09"},
    },

    # ── Square Enix ───────────────────────────────────────────────
    "square_enix": {
        "Final Fantasy VII Remake Intergrade": {"appid": 1462040, "release_pc": "2021-12-16"},
        "Final Fantasy XVI":              {"appid": 2515020, "release_pc": "2024-09-17"},
        "Final Fantasy XIV Online":       {"appid": 39210,   "release_pc": "2013-08-27"},
        "Final Fantasy VII Rebirth":      {"appid": 2909400, "release_pc": "2024-01-23"},  # NOTE: verify this ID
        "Dragon Quest XI S":              {"appid": 1295510, "release_pc": "2020-12-04"},
        "Octopath Traveler":              {"appid": 921570,  "release_pc": "2019-06-07"},
        "Octopath Traveler II":           {"appid": 1971650, "release_pc": "2023-02-24"},
        "NieR: Automata":                 {"appid": 524220,  "release_pc": "2017-03-17"},
        "NieR Replicant":                 {"appid": 1113560, "release_pc": "2021-04-22"},  # NOTE: verify
        "Forspoken":                      {"appid": 1680880, "release_pc": "2023-01-24"},
        "Marvel's Avengers":              {"appid": 997070,  "release_pc": "2020-09-04"},
    },

    # ── Benchmarks ────────────────────────────────────────────────
    "nintendo": {
        "Super Mario Bros. Wonder":       {"appid": None,    "note": "no PC version"},
        "Kirby and the Forgotten Land":   {"appid": None,    "note": "no PC version"},
    },
    "ea": {
        "EA Sports FC 24":                {"appid": 2195250, "release_pc": "2023-09-29"},
        "EA Sports FC 25":                {"appid": 2669320, "release_pc": "2024-09-27"},
        "Apex Legends":                   {"appid": 1172470, "release_pc": "2019-02-04"},
    },
    "take_two": {
        "GTA V":                          {"appid": 271590,  "release_pc": "2015-04-14"},
        "Red Dead Redemption 2":          {"appid": 1174180, "release_pc": "2019-12-05"},
        "Borderlands 3":                  {"appid": 397540,  "release_pc": "2020-03-13"},
    },
    "ubisoft": {
        "Assassin's Creed Mirage":        {"appid": 3035570, "release_pc": "2023-10-05"},
        "Assassin's Creed Shadows":       {"appid": 3159330, "release_pc": "2025-03-20"},
        "Star Wars Outlaws":              {"appid": 2446550, "release_pc": "2024-08-30"},
    },
}

# Flat lookup: appid → metadata
def get_all_titles():
    titles = {}
    for publisher, games in GAME_REGISTRY.items():
        for title, meta in games.items():
            if meta.get("appid"):
                titles[meta["appid"]] = {
                    "title": title,
                    "publisher": publisher,
                    **meta
                }
    return titles

if __name__ == "__main__":
    titles = get_all_titles()
    print(f"Total trackable titles (with Steam AppID): {len(titles)}")
    for appid, info in list(titles.items())[:5]:
        print(f"  {appid}: {info['title']} ({info['publisher']})")
