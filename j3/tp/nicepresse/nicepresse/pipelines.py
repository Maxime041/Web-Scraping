from itemadapter import ItemAdapter


class CleanPipeline:
    """Nettoie les textes et ne garde que la date, sans l'heure."""

    def process_item(self, item, spider):
        a = ItemAdapter(item)

        for champ in ["titre", "url"]:
            a[champ] = (a.get(champ) or "").strip()

        # Le site donne "2026-06-26T19:03:01+02:00", on ne garde que 2026-06-26
        a["date"] = (a.get("date") or "")[:10]

        return item
