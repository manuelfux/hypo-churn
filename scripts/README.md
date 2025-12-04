# Scripts Verzeichnis

Dieses Verzeichnis enthält Hilfsskripte für das hypo-churn Projekt.

## Verfügbare Scripts

### download_datasets.py

Automatisiert den Download der empfohlenen öffentlichen Churn Datasets von Kaggle.

#### Setup

1. **Kaggle API installieren:**
   ```bash
   pip install kaggle
   ```

2. **Kaggle API Token konfigurieren:**
   - Gehe zu: https://www.kaggle.com/settings/account
   - Scrolle zu "API" Sektion
   - Klicke "Create New API Token"
   - Speichere die heruntergeladene `kaggle.json` Datei in `~/.kaggle/`
   - Setze Permissions:
     ```bash
     mkdir -p ~/.kaggle
     mv ~/Downloads/kaggle.json ~/.kaggle/
     chmod 600 ~/.kaggle/kaggle.json
     ```

#### Usage

**Download aller empfohlenen Datasets:**
```bash
python scripts/download_datasets.py --all
```

**Download spezifischer Datasets:**
```bash
# Nur Banking Churn (EMPFOHLEN für Start)
python scripts/download_datasets.py --banking

# Banking Churn (alternative Version)
python scripts/download_datasets.py --banking-alt

# Credit Card Churn
python scripts/download_datasets.py --credit-card

# Telco Churn (für Vergleich)
python scripts/download_datasets.py --telco
```

**Kombinationen:**
```bash
# Banking und Credit Card
python scripts/download_datasets.py --banking --credit-card

# Alles außer Telco
python scripts/download_datasets.py --banking --banking-alt --credit-card
```

**Benutzerdefiniertes Zielverzeichnis:**
```bash
python scripts/download_datasets.py --all --data-dir data/external
```

#### Heruntergeladene Datasets

Die Datasets werden in folgende Unterverzeichnisse gespeichert:

```
data/raw/
├── banking_churn/          # Bank Customer Churn (Primary, empfohlen)
├── banking_churn_alt/      # Bank Customer Churn (Alternative Version)
├── credit_card_churn/      # Credit Card Customers
└── telco_churn/            # Telco Customer Churn (IBM)
```

#### Troubleshooting

**Fehler: "kaggle: command not found"**
- Lösung: Installieren Sie Kaggle API: `pip install kaggle`

**Fehler: "Unauthorized: please ensure your API credentials are correct"**
- Lösung: Prüfen Sie ob `~/.kaggle/kaggle.json` existiert und korrekt ist
- Erstellen Sie einen neuen Token auf https://www.kaggle.com/settings/account

**Fehler: "403 - Forbidden"**
- Lösung: Akzeptieren Sie die Dataset-Regeln auf der Kaggle-Website
- Besuchen Sie das Dataset auf Kaggle und klicken Sie "Download"

**Fehler: "Permission denied"**
- Lösung: Setzen Sie korrekte Permissions: `chmod 600 ~/.kaggle/kaggle.json`

## Weitere Scripts (zukünftig)

Weitere Scripts werden hier hinzugefügt, z.B.:
- `prepare_synthetic_data.py` - Synthetische Datengenerierung mit SDV
- `merge_datasets.py` - Kombination mehrerer Churn Datasets
- `validate_data.py` - Datenqualitätsprüfung
