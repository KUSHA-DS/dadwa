# Boxing Shop API

Sistem i menaxhimit te dyqanit te boksit - API me FastAPI dhe Python.

## Struktura

```
boxing_shop/
├── auth/
│   ├── __init__.py
│   ├── generate_key.py    # Gjenerimi i API key
│   └── security.py        # Autentikimi me API key
├── models/
│   ├── __init__.py
│   ├── product.py         # Modeli i produktit
│   └── sale.py            # Modeli i shitjes
├── routers/
│   ├── __init__.py
│   ├── api_key.py         # Endpoints per API key
│   ├── products.py        # CRUD per produkte
│   └── sales.py           # Endpoints per shitje
├── .env                   # Environment variables
├── app.py                 # FastAPI app instance
├── database.py            # Database connection
├── main.py                # Entry point
├── requirements.txt       # Dependencies
└── shop.db                # SQLite database
```

## Instalimi

```bash
pip install -r requirements.txt
```

## Ekzekutimi

```bash
python main.py
```

Hap: http://localhost:8000/docs per dokumentacionin interaktiv.

## API Endpoints

- `GET /products` - Lista e produkteve
- `POST /products` - Shto produkt (kerkon API key)
- `PUT /products/{id}` - Ndrysho produkt (kerkon API key)
- `DELETE /products/{id}` - Fshi produkt (kerkon API key)
- `GET /sales` - Lista e shitjeve
- `POST /sales` - Krijo shitje (kerkon API key)
- `GET /sales/stats` - Statistikat e shitjeve

## Autentikimi

Perdor header `X-API-Key` per endpoints qe kerkojne autentikim.
