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

        self.secretapikey = api_config['secretapikey']
        self.apikey = api_config['apikey']
        self.endpoint = api_config['endpoint']
        self.domain = api_config['domain']

    def create_record(self, record_name: str, record_type: str, record_content: str,
    ) -> None:
        """
        Create a DNS record.

        This function creates one DNS record using porkbun API and a secrets dictionary
        with API key and secret.

        Parameters
        ----------
        record_name: str
            name of the DNS record to be inserted.

        record_type: str
            type of the record to be inserted. It has to be one of the valid DNS types.

        record_content: str
            the value of the record.
        """
        _check_record(record_type)

        payload = {"apikey":self.apikey, "secretapikey":self.secretapikey}
        try:
            payload["name"] = record_name
            payload["type"] = record_type
            payload["content"] = record_content
            url = f"{self.endpoint}/create/{self.domain}"

            response = requests.post(
                url,
                data=json.dumps(payload),
            )
            if response.status_code != 200:
                logger.error(f"Failed to create record {response.json()} {record_name}")
            else:
                logger.info(
                    f"Record created: {record_name} \t\t {record_type} \t\t {record_content}"
                )

        except requests.exceptions.ConnectionError as e:
            logger.error(e, record_name, record_type, record_content)

    def update_record(self,
        record_name: str, record_type: str, record_content: str
    ) -> None:
        """
        Update a DNS record.

        This function updates one DNS record using porkbun API and a secrets dictionary
        with API key and secret.

        Parameters
        ----------
        record_name: str
            name of the DNS record to be inserted.

        record_type: str
            type of the record to be inserted. It has to be one of the valid DNS types.

        record_content: str
            the value of the record.
        """

        _check_record(record_type)
        payload = {"apikey":self.apikey, "secretapikey":self.secretapikey}

        try:
            payload["content"] = record_content
            url = f"{self.endpoint}/editByNameType/{self.domain}/{record_type}/{record_name}"

            response = requests.post(
                url,
                data=json.dumps(payload),
            )

            if response.status_code != 200:
                logger.error(f"Failed to update record {response.json()} {record_name}")
            else:
                logger.info(
                    f"Record updated: {record_name} \t\t {record_type} \t\t {record_content}"
                )

        except requests.exceptions.ConnectionError as e:
            logger.error(e, record_name, record_type, record_content)

    def change_records(self, domain_db, action: str) -> None:
        """
        Update DNS records in bulk.

        This function updates the DNS records from a domain database file,
        in CSV format.

        Parameters
        ----------
        domain_db: str
            The path of the domain database file.

        action: str
            The action expected to be done. Create and Update are currently implemented.

        """
        try:
            df = pd.read_csv(domain_db)
            records = df[["host", "type", "answer"]].to_dict("records")

            for entry in records:
                if action == "update":
                    self.update_record(entry["host"], entry["type"], entry["answer"])
                elif action == "create":
                    self.create_record(entry["host"], entry["type"], entry["answer"])
                else:
                    logger.error(f"{action} is not valid")
        except FileNotFoundError:
            logger.error(f"File not found: {domain_db}")
