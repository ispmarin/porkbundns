from dns import manage_records
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    manage_records.bulk_update("data/homelab.csv", ".env/base.json")