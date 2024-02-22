# Uvoz funkcije za kreiranje aplikacije iz modula 'website'
from website import create_app

# Kreiranje instance aplikacije pomoću funkcije 'create_app()'
app = create_app()

# Provjera da li je skripta pokrenuta izravno (ne uvezena kao modul)
if __name__ == "__main__":
    # Pokretanje aplikacije na adresi '0.0.0.0' na portu 5000
    app.run(host='localhost', port=5000, debug=False)
