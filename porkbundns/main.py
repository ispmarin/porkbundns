from porkbundns.dns import manage_records
import logging

logger = logging.getLogger()

if __name__ == "__main__":
    manage_records.bulk_update("../data/homelab.csv", "../.env/base.json")