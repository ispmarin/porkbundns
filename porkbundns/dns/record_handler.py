import json
import logging

import pandas as pd
import requests
from dns.dns_types import record_types

logger = logging.getLogger(__name__)


def _check_record(record_type):
    if record_type not in record_types:
        logger.error(f"Wrong record type. Must be one of the following: {record_types}")
        raise requests.exceptions.ConnectionError


class RecordHandler:
    def __init__(self, secrets_file: str):
        try:
            with open(secrets_file, "r") as f:
                api_config = json.load(f)
        except FileNotFoundError:
            logger.error(f"Secrets file {secrets_file} not found.")
            exit(-1)

        self.secretapikey = api_config["secretapikey"]
        self.apikey = api_config["apikey"]
        self.endpoint = api_config["endpoint"]
        self.domain = api_config["domain"]
        self.base_payload = {"apikey": self.apikey, "secretapikey": self.secretapikey}

    @staticmethod
    def call_api(payload: dict, url: str) -> requests.Response:

        try:

            response = requests.post(
                url,
                data=json.dumps(payload),
            )
            payload.pop('apikey')
            payload.pop('secretapikey')
            if response.status_code != 200:
                logger.error(f"Failed to change record {response.json()}: {response.status_code} {payload} ")
            else:
                logger.info(f"Record changed: {response.json()} {payload}")
            return response

        except requests.exceptions.ConnectionError as e:
            logger.error(e, payload)

    def create_record(
        self,
        record_name: str,
        record_type: str,
        record_content: str,
    ) -> requests.Response:

        payload = {
            "type": record_type,
            "name": record_name,
            "content": record_content,
        }
        payload.update(self.base_payload)
        url = f"{self.endpoint}/create/{self.domain}"

        return self.call_api(payload, url)

    def update_record(
        self, record_content: str, record_type: str, record_name: str
    ) -> requests.Response:

        payload = {
            "content": record_content,
        }
        payload.update(self.base_payload)
        url = (
            f"{self.endpoint}/editByNameType/{self.domain}/{record_type}/{record_name}"
        )

        return self.call_api(payload, url)

    def delete_record(self, record_name: str, record_type: str) -> requests.Response:

        payload = self.base_payload
        url = f"{self.endpoint}/deleteByNameType/{self.domain}/{record_type}/{record_name}"

        return self.call_api(payload, url)

    def change_records(self, domain_db, action: str) -> None:

        try:
            df = pd.read_csv(domain_db)
            records = df[["host", "type", "answer"]].to_dict("records")

            if action == "update":
                [self.update_record(entry["host"], entry["type"], entry["answer"]) for entry in records]
            elif action == "create":
                [self.create_record(entry["host"], entry["type"], entry["answer"]) for entry in records]
            elif action == "delete":
                [self.delete_record(entry["host"], entry["type"]) for entry in records]
            else:
                logger.error(f"{action} is not valid")
        except FileNotFoundError:
            logger.error(f"File not found: {domain_db}")
