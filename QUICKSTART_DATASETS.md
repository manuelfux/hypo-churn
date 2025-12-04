# Quick Start: Datasets für Mortgage Churn Prediction

Dieses Dokument bietet eine schnelle Anleitung zum Einstieg mit öffentlichen Datasets für Ihr Mortgage Churn Prediction Projekt.

## TL;DR - Sofort starten (5 Minuten)

```bash
# 1. Kaggle API installieren
pip install kaggle

# 2. Kaggle Token konfigurieren (einmalig)
# - Gehe zu: https://www.kaggle.com/settings/account
# - Klicke "Create New API Token"
# - Speichere kaggle.json in ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 3. Empfohlenes Dataset herunterladen
python scripts/download_datasets.py --banking

# 4. Daten explorieren
jupyter notebook notebooks/
```

## Empfohlenes Starter-Dataset

### Bank Customer Churn Dataset
**Warum dieses Dataset?**
- ✓ 10,000 Datensätze (ausreichend für Training)
- ✓ Gut strukturiert und sauber
- ✓ Enthält relevante Features (CreditScore, Balance, Tenure, etc.)
- ✓ Realistische Churn-Rate (~16%)
- ✓ CC0 Public Domain Lizenz
- ✓ Kann für Mortgage Churn adaptiert werden

**Download:**
```bash
python scripts/download_datasets.py --banking
```

**Daten-Location:**
```
data/raw/banking_churn/
└── Churn_Modelling.csv  (oder ähnlicher Name)
```

## Features im Banking Dataset

| Feature | Beschreibung | Mortgage Equivalent |
|---------|--------------|---------------------|
| CreditScore | Kreditwürdigkeit (300-850) | Credit Score (direkt übertragbar) |
| Geography | Land (France/Spain/Germany) | Property Location |
| Gender | Geschlecht | Customer Gender |
| Age | Alter in Jahren | Customer Age |
| Tenure | Jahre als Kunde (0-10) | Loan Age (Jahre seit Vergabe) |
| Balance | Kontostand | Outstanding Loan Balance |
| NumOfProducts | Anzahl Produkte (1-4) | Cross-Sell Products |
| HasCrCard | Kreditkarte (0/1) | Credit Card Ownership |
| IsActiveMember | Aktiv (0/1) | Online Banking Active |
| EstimatedSalary | Geschätztes Gehalt | Annual Income |
| **Exited** | **Churn (0/1)** | **Target Variable** |

## Erste Schritte mit den Daten

### 1. Daten laden und inspizieren

```python
import pandas as pd
import numpy as np

# Daten laden
df = pd.read_csv('data/raw/banking_churn/Churn_Modelling.csv')

# Erste Inspektion
print(f"Dataset Shape: {df.shape}")
print(f"\nFeatures:\n{df.columns.tolist()}")
print(f"\nChurn Rate: {df['Exited'].mean():.2%}")
print(f"\nMissing Values:\n{df.isnull().sum()}")

# Statistiken
print(df.describe())
```

### 2. Features für Mortgage Churn adaptieren

```python
def adapt_banking_to_mortgage(df):
    """Adaptiert Banking Churn für Mortgage Churn Kontext"""

    # Feature Renaming
    mortgage_df = df.rename(columns={
        'Balance': 'outstanding_loan_balance',
        'Tenure': 'loan_age_years',
        'CreditScore': 'credit_score',
        'EstimatedSalary': 'annual_income',
        'NumOfProducts': 'num_bank_products',
        'IsActiveMember': 'online_banking_active',
        'HasCrCard': 'has_credit_card',
        'Exited': 'churned'
    })

    # Feature Engineering für Mortgage-Kontext
    mortgage_df['monthly_income'] = mortgage_df['annual_income'] / 12

    # LTV Ratio Approximation (Balance / geschätzter Property Value)
    # Annahme: Property Value = 3.5x Annual Income
    mortgage_df['estimated_property_value'] = mortgage_df['annual_income'] * 3.5
    mortgage_df['ltv_ratio'] = (
        mortgage_df['outstanding_loan_balance'] /
        mortgage_df['estimated_property_value']
    ).clip(0, 1.5)  # Cap bei 150% LTV

    # Payment-to-Income Ratio
    # Annahme: 5% Zinssatz, 30-Jahre Amortisation
    monthly_payment = mortgage_df['outstanding_loan_balance'] * 0.05 / 12
    mortgage_df['payment_to_income_ratio'] = (
        monthly_payment / mortgage_df['monthly_income']
    )

    # Risk Score (kombiniert mehrere Faktoren)
    mortgage_df['risk_score'] = (
        (850 - mortgage_df['credit_score']) / 550 * 0.4 +  # Credit Risk
        mortgage_df['ltv_ratio'] * 0.3 +                    # LTV Risk
        mortgage_df['payment_to_income_ratio'] * 0.3        # Payment Risk
    )

    return mortgage_df

# Anwenden
mortgage_df = adapt_banking_to_mortgage(df)
print(f"\nNeue Features:\n{mortgage_df.columns.tolist()}")
```

### 3. Baseline-Modell trainieren

```python
from hypo_churn.data_preprocessing import split_features_target, clean_data
from hypo_churn.models import ChurnPredictor
from hypo_churn.evaluation import evaluate_model
from sklearn.model_selection import train_test_split

# Data Preprocessing
mortgage_clean = clean_data(mortgage_df)

# Feature Selection
feature_cols = [
    'credit_score',
    'Age',
    'loan_age_years',
    'outstanding_loan_balance',
    'num_bank_products',
    'online_banking_active',
    'annual_income',
    'ltv_ratio',
    'payment_to_income_ratio',
    'risk_score'
]

X = mortgage_clean[feature_cols]
y = mortgage_clean['churned']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Model Training
model = ChurnPredictor(model_type='random_forest')
model.train(X_train, y_train)

# Evaluation
metrics = evaluate_model(model, X_test, y_test)
print(f"\nModel Performance:\n{metrics}")
```

## Weitere Datasets (Optional)

### Credit Card Churn Dataset
**Für zusätzliche Features und größeres Trainingsset**

```bash
python scripts/download_datasets.py --credit-card
```

Features:
- 10,000 Kunden
- ~18 Features inkl. Credit Limit, Marital Status
- 16.07% Churn Rate
- Ergänzt Banking Dataset gut

### Telco Churn Dataset
**Für Cross-Domain Vergleich und Contract-Type Features**

```bash
python scripts/download_datasets.py --telco
```

Features:
- 7,043 Kunden
- Contract Type (Month-to-Month, One/Two Year)
- Payment Method, Tenure, Charges
- Nützlich für Contract-Duration Patterns

## Typische Data Pipeline

```
1. Download Dataset
   └─> scripts/download_datasets.py

2. Exploratory Data Analysis
   └─> notebooks/01_eda.ipynb

3. Feature Engineering
   └─> src/hypo_churn/data_preprocessing.py
   └─> Adapt Banking → Mortgage Features

4. Model Training
   └─> src/hypo_churn/models.py
   └─> Baseline: Random Forest

5. Evaluation
   └─> src/hypo_churn/evaluation.py
   └─> Metrics: Accuracy, Precision, Recall, F1, ROC-AUC

6. Iteration
   └─> Feature Selection
   └─> Hyperparameter Tuning
   └─> Cross-Validation
```

## Erwartete Performance (Basierend auf Banking Dataset)

**Baseline Random Forest:**
- Accuracy: ~85-87%
- Precision: ~75-80%
- Recall: ~50-60%
- F1-Score: ~60-68%
- ROC-AUC: ~85-87%

**Herausforderungen:**
- Class Imbalance (~16% Churn)
- Feature Engineering für Mortgage-Spezifika
- Fehlende temporal patterns (keine Zeitreihen)

**Lösungsansätze:**
- SMOTE für Class Balancing
- Feature Engineering (siehe oben)
- Ensemble Methods
- Threshold Tuning für Precision-Recall Tradeoff

## Nächste Schritte

### Woche 1: Setup & Baseline
- [x] Kaggle API Setup
- [ ] Dataset Download (--banking)
- [ ] EDA Notebook erstellen
- [ ] Baseline-Modell trainieren

### Woche 2: Feature Engineering
- [ ] Mortgage-spezifische Features entwickeln
- [ ] LTV, Payment-to-Income, Risk Scores
- [ ] Feature Importance Analyse
- [ ] Feature Selection

### Woche 3: Model Optimization
- [ ] Hyperparameter Tuning
- [ ] Cross-Validation
- [ ] Multiple Models vergleichen
- [ ] Ensemble Methods

### Woche 4: Erweiterung
- [ ] Credit Card Dataset integrieren
- [ ] Synthetische Daten generieren (SDV)
- [ ] External Data (FRED, Zillow)
- [ ] Production Pipeline

## Zusätzliche Ressourcen

**Vollständige Recherche:**
- Siehe: `data/DATASET_RESEARCH.md`

**Kaggle Notebooks (Inspiration):**
- https://www.kaggle.com/datasets/mathchi/churn-for-bank-customers/code
- Über 100+ Community Notebooks mit verschiedenen Ansätzen

**Synthetische Daten:**
- SDV (Synthetic Data Vault): https://docs.sdv.dev/sdv
- Tutorial: `pip install sdv`

**External Data APIs:**
- FRED (Economic Data): https://fred.stlouisfed.org/
- Zillow (Housing): https://www.zillow.com/research/data/

## Hilfe & Support

**Probleme beim Download?**
- Prüfen: `~/.kaggle/kaggle.json` existiert
- Permissions: `chmod 600 ~/.kaggle/kaggle.json`
- Siehe: `scripts/README.md`

**Fragen zu Features?**
- Siehe: Feature Mapping in `data/DATASET_RESEARCH.md`
- Banking → Mortgage Adaptation Guide

**Model Performance Issues?**
- Class Imbalance: Verwenden Sie SMOTE
- Feature Engineering: Siehe oben
- Hyperparameter Tuning: Grid/Random Search

---

**Viel Erfolg mit Ihrem Mortgage Churn Prediction Projekt!**

Bei weiteren Fragen konsultieren Sie bitte `data/DATASET_RESEARCH.md` für detaillierte Informationen zu allen verfügbaren Datasets und Strategien.
