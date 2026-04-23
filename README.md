# Boxing Store - Sistem Inventari

Sistem per menaxhimin e stokut te nje dyqani boksi, i ndertuar me Python dhe Flask.

## Teknologjite

- **Python 3.12+**
- **Flask** - Web framework
- **SQLite** - Database

## Si te ekzekutosh

1. Instalo dependencies:
```bash
cd v0-boxing-inventory-system-main/backend
pip install flask
```

2. Ekzekuto aplikacionin:
```bash
python main.py
```

3. Hap ne browser: `http://localhost:5000`

## Funksionalitetet

- Shfaq te gjitha produktet
- Shto produkt te ri
- Ndrysho produkt ekzistues
- Fshi produkt
- Shto/Hiq stok
- Kerko dhe filtro produktet
- Statistika (produkte totale, stok, vlera)

## Struktura

```
backend/
  main.py           - Aplikacioni Flask
  boxing_shop.db    - Database SQLite
  templates/
    base.html       - Template baze
    index.html      - Faqja kryesore
    product_form.html - Forma per produkte
```
