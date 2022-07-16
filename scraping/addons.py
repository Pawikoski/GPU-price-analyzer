BRANDS = {"asus", "gigabyte", "inno3d", "palit", "gainward", "aorus", "pny", "zotac", "kfa2", "msi", "biostar", "afox",
          "asrock", "evga", "sapphire technology", "sapphire", "xfx", "powercolor"}


def brand_detector(name: str) -> str | bool:
    name = name.lower()
    for brand in BRANDS:
        if brand in name:
            return brand.title()

    return False
