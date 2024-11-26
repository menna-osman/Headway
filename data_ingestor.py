import time
import pandas as pd
from abc import ABC, abstractmethod


class DataReader(ABC):
    @abstractmethod
    def read_records(self):
        pass


class CSVDataReader(DataReader):
    def __init__ (self, file_path):
        self.file_path = file_path
        self.file = None
        self.header = None


    def open_file(self):
        if self.file is None:
            self.file = open(self.file_path, 'r')
            self.header = self.file.readline().strip().split(",")

    def close_file(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    def read_records(self):
        """
        Reads the file record by record using a generator to avoid re-reading the entire file.
        """
        try:
            self.open_file()
            for line in self.file:
                record = dict(zip(self.header, line.strip().split(",")))
                yield record
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
        finally:
            self.close_file()


class DataFilter:
    def __init__(self):
        self.last_timestamp = None  # Track last timestamp processed

    def is_new_records(self, record):
        """
        Checks if the given record is new based on its timestamp.
        """
        try:
            timestamp_str = record['timestamp'].replace('[UTC]', '').strip()
            record_timestamp = pd.to_datetime(timestamp_str)
        except KeyError:
            print("Error: Record is missing a 'timestamp' field.")
            return False


        if self.last_timestamp is None or record_timestamp > self.last_timestamp :
            self.last_timestamp = record_timestamp
            return  True

        return False

class DataIngestor:
    """
    Ingests data record by record at a regular interval.

    """
    def __init__ (self, data_reader: DataReader, data_filter: DataFilter, interval =5):
        self.data_reader = data_reader
        self.data_filter = data_filter
        self.interval = interval



    def process(self):
        for record in self.data_reader.read_records():
            if self.data_filter.is_new_records(record):
                yield record
            time.sleep(self.interval)


