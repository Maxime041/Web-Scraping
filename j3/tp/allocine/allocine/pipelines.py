from itemadapter import ItemAdapter


class CleanPipeline:
    """Nettoie et caste les donnees."""

    def process_item(self, item, spider):
        a = ItemAdapter(item)
        for field in ["titre", "realisateur"]:
            if a.get(field):
                a[field] = a[field].strip()
        for field in ["note_presse", "note_spectateurs"]:
            try:
                raw = (a.get(field) or "").replace(",", ".")
                a[field] = float(raw)
            except (ValueError, TypeError):
                a[field] = None
        return item
