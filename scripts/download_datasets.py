#!/usr/bin/env python3
"""
Dataset Download Script für Mortgage Churn Prediction Projekt

Dieses Script automatisiert den Download der empfohlenen öffentlichen Datasets
von Kaggle für das hypo-churn Projekt.

Voraussetzungen:
    1. Kaggle API installiert: pip install kaggle
    2. Kaggle API Token konfiguriert: ~/.kaggle/kaggle.json
       - Token von https://www.kaggle.com/settings/account
       - "Create New API Token" klicken
       - kaggle.json in ~/.kaggle/ speichern
       - Permissions setzen: chmod 600 ~/.kaggle/kaggle.json

Usage:
    python scripts/download_datasets.py --all
    python scripts/download_datasets.py --banking
    python scripts/download_datasets.py --credit-card
    python scripts/download_datasets.py --telco
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
import zipfile
import shutil


class DatasetDownloader:
    """Automatisiert den Download von Kaggle Datasets für Churn Prediction"""

    def __init__(self, data_dir: str = "data/raw"):
        """
        Args:
            data_dir: Zielverzeichnis für heruntergeladene Datasets
        """
        self.project_root = Path(__file__).parent.parent.absolute()
        self.data_dir = self.project_root / data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def check_kaggle_api(self) -> bool:
        """Prüft ob Kaggle API installiert und konfiguriert ist"""
        try:
            result = subprocess.run(
                ["kaggle", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Kaggle API installiert: {result.stdout.strip()}")
            return True
        except FileNotFoundError:
            print("✗ Kaggle API nicht installiert.")
            print("  Installation: pip install kaggle")
            return False
        except subprocess.CalledProcessError:
            print("✗ Kaggle API Fehler.")
            return False

    def check_kaggle_credentials(self) -> bool:
        """Prüft ob Kaggle Credentials konfiguriert sind"""
        kaggle_json = Path.home() / ".kaggle" / "kaggle.json"

        if not kaggle_json.exists():
            print("✗ Kaggle API Token nicht gefunden.")
            print(f"  Erwarteter Pfad: {kaggle_json}")
            print("  1. Gehe zu: https://www.kaggle.com/settings/account")
            print("  2. Klicke 'Create New API Token'")
            print("  3. Speichere kaggle.json in ~/.kaggle/")
            print("  4. Setze Permissions: chmod 600 ~/.kaggle/kaggle.json")
            return False

        print(f"✓ Kaggle API Token gefunden: {kaggle_json}")
        return True

    def download_dataset(
        self,
        dataset_id: str,
        dataset_name: str,
        subfolder: str
    ) -> bool:
        """
        Download eines einzelnen Kaggle Datasets

        Args:
            dataset_id: Kaggle Dataset ID (z.B. 'mathchi/churn-for-bank-customers')
            dataset_name: Beschreibender Name für Logging
            subfolder: Unterordner in data/raw/

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        target_dir = self.data_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*70}")
        print(f"Downloading: {dataset_name}")
        print(f"Dataset ID: {dataset_id}")
        print(f"Zielverzeichnis: {target_dir}")
        print(f"{'='*70}")

        try:
            # Kaggle Dataset Download
            result = subprocess.run(
                [
                    "kaggle",
                    "datasets",
                    "download",
                    "-d",
                    dataset_id,
                    "-p",
                    str(target_dir),
                    "--unzip"
                ],
                capture_output=True,
                text=True,
                check=True
            )

            print(f"✓ Download erfolgreich: {dataset_name}")
            print(f"  Ausgabe: {result.stdout.strip()}")

            # Liste heruntergeladene Dateien
            files = list(target_dir.glob("*"))
            print(f"  Heruntergeladene Dateien ({len(files)}):")
            for f in files:
                size = f.stat().st_size / 1024  # KB
                print(f"    - {f.name} ({size:.1f} KB)")

            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ Download fehlgeschlagen: {dataset_name}")
            print(f"  Fehler: {e.stderr}")
            return False

    def download_banking_churn(self) -> bool:
        """Download Bank Customer Churn Dataset (Empfohlen für Mortgage Churn)"""
        return self.download_dataset(
            dataset_id="mathchi/churn-for-bank-customers",
            dataset_name="Bank Customer Churn Dataset (Mehmet Akturk)",
            subfolder="banking_churn"
        )

    def download_banking_churn_alternative(self) -> bool:
        """Download alternatives Bank Customer Churn Dataset"""
        return self.download_dataset(
            dataset_id="gauravtopre/bank-customer-churn-dataset",
            dataset_name="Bank Customer Churn Dataset (Gaurav Topre)",
            subfolder="banking_churn_alt"
        )

    def download_credit_card_churn(self) -> bool:
        """Download Credit Card Churn Dataset"""
        return self.download_dataset(
            dataset_id="sakshigoyal7/credit-card-customers",
            dataset_name="Credit Card Customers Dataset",
            subfolder="credit_card_churn"
        )

    def download_telco_churn(self) -> bool:
        """Download Telco Customer Churn Dataset (für Vergleich)"""
        return self.download_dataset(
            dataset_id="blastchar/telco-customer-churn",
            dataset_name="Telco Customer Churn (IBM)",
            subfolder="telco_churn"
        )

    def download_all(self) -> dict:
        """
        Download aller empfohlenen Datasets

        Returns:
            Dictionary mit Download-Status für jedes Dataset
        """
        results = {
            "banking_churn": self.download_banking_churn(),
            "banking_churn_alt": self.download_banking_churn_alternative(),
            "credit_card_churn": self.download_credit_card_churn(),
            "telco_churn": self.download_telco_churn()
        }

        return results

    def print_summary(self, results: dict):
        """Druckt Zusammenfassung der Downloads"""
        print(f"\n{'='*70}")
        print("DOWNLOAD ZUSAMMENFASSUNG")
        print(f"{'='*70}")

        total = len(results)
        successful = sum(1 for v in results.values() if v)

        for dataset, status in results.items():
            status_icon = "✓" if status else "✗"
            print(f"{status_icon} {dataset}: {'Erfolgreich' if status else 'Fehlgeschlagen'}")

        print(f"\nErgebnis: {successful}/{total} Datasets erfolgreich heruntergeladen")
        print(f"Speicherort: {self.data_dir}")

        if successful > 0:
            print(f"\nNächste Schritte:")
            print(f"1. Prüfen Sie die Daten in: {self.data_dir}")
            print(f"2. Führen Sie explorative Datenanalyse durch")
            print(f"3. Starten Sie mit Banking Churn Dataset für Baseline-Modell")
            print(f"\nEmpfohlenes Notebook:")
            print(f"  jupyter notebook notebooks/01_exploratory_data_analysis.ipynb")


def main():
    parser = argparse.ArgumentParser(
        description="Download Kaggle Datasets für Mortgage Churn Prediction"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Download alle empfohlenen Datasets"
    )

    parser.add_argument(
        "--banking",
        action="store_true",
        help="Download Bank Customer Churn Dataset (Primary)"
    )

    parser.add_argument(
        "--banking-alt",
        action="store_true",
        help="Download alternatives Bank Customer Churn Dataset"
    )

    parser.add_argument(
        "--credit-card",
        action="store_true",
        help="Download Credit Card Churn Dataset"
    )

    parser.add_argument(
        "--telco",
        action="store_true",
        help="Download Telco Churn Dataset (Vergleich)"
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/raw",
        help="Zielverzeichnis für Downloads (default: data/raw)"
    )

    args = parser.parse_args()

    # Initialisiere Downloader
    downloader = DatasetDownloader(data_dir=args.data_dir)

    # Prüfe Voraussetzungen
    if not downloader.check_kaggle_api():
        sys.exit(1)

    if not downloader.check_kaggle_credentials():
        sys.exit(1)

    # Führe Downloads durch
    results = {}

    if args.all:
        results = downloader.download_all()
    else:
        if args.banking:
            results["banking_churn"] = downloader.download_banking_churn()

        if args.banking_alt:
            results["banking_churn_alt"] = downloader.download_banking_churn_alternative()

        if args.credit_card:
            results["credit_card_churn"] = downloader.download_credit_card_churn()

        if args.telco:
            results["telco_churn"] = downloader.download_telco_churn()

        if not any([args.banking, args.banking_alt, args.credit_card, args.telco]):
            print("Keine Dataset-Option ausgewählt.")
            print("Verwenden Sie --all oder spezifische Optionen (--banking, --credit-card, etc.)")
            print("Für Hilfe: python scripts/download_datasets.py --help")
            sys.exit(1)

    # Zeige Zusammenfassung
    if results:
        downloader.print_summary(results)

        # Exit Code basierend auf Erfolg
        if all(results.values()):
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
