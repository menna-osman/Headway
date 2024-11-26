from abc import ABC, abstractmethod
import json
from datetime import datetime
import sqlite3

import os

class OutputMessage:
    def __init__(self,asset_id,attribute_id, timestamp, value):
        self.asset_id = asset_id
        self.attribute_id = attribute_id
        self.timestamp = timestamp
        self.value =value


class IMessageFormatter(ABC):
    @abstractmethod
    def format_message(self, message: OutputMessage) -> str:
        pass


class IMessageStorage(ABC):
    @abstractmethod
    def store_message(self, message: OutputMessage):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

class ITimestampGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass

class UTCTimestampGenerator(ITimestampGenerator):
    def generate(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ[UTC]")



class JsonMessageFormatter(IMessageFormatter):
    """
    converts a Python object into a JSON string
    """
    def format_message(self, message: OutputMessage):
        return json.dumps({
            "asset_id": message.asset_id,
            "attribute_id": message.attribute_id,
            "timestamp": message.timestamp,
            "value": message.value
        })



class SQLiteMessageStorage(IMessageStorage):
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            directory = os.path.dirname(self.db_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self.create_table()
        except sqlite3.Error:
            raise Exception(f"Database connection error")

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def create_table(self):

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS output_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT NOT NULL,
                attribute_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                value TEXT NOT NULL
            )
        ''')
        self.connection.commit()

    # def store_message(self, message: OutputMessage) -> bool:
    #     try:
    #         self.cursor.execute('''
    #             INSERT INTO output_messages (asset_id, attribute_id, timestamp, value)
    #             VALUES (?, ?, ?, ?)
    #         ''', (message.asset_id, message.attribute_id, message.timestamp, message.value))
    #         self.connection.commit()
    #         return True
    #     except sqlite3.Error as e:
    #         print(f"Error storing message: {str(e)}")
    #         return False

    def store_message(self, message: OutputMessage) -> bool:
        try:
            if not self.connection or not self.cursor:
                raise sqlite3.Error("Database connection not established")

            self.cursor.execute('''
                INSERT INTO output_messages (asset_id, attribute_id, timestamp, value)
                VALUES (?, ?, ?, ?)
            ''', (message.asset_id, message.attribute_id, message.timestamp, message.value))
            self.connection.commit()
            print(f"Successfully stored message for asset {message.asset_id}")
            return True
        except sqlite3.Error as e:
            print(f"SQLite error storing message: {str(e)}")
            return False
        except Exception as e:
            print(f"Error storing message: {str(e)}")
            return False

class MessageProducer:
    def __init__(self, formatter: IMessageFormatter, storage: IMessageStorage,timestamp_generator: ITimestampGenerator):
        self.formatter = formatter
        self.storage = storage
        self.timestamp_generator = timestamp_generator


    def produce_message(self, asset_id, attribute_id, value):
        message = OutputMessage(
            asset_id=asset_id,
            attribute_id=attribute_id,
            timestamp=self.timestamp_generator.generate(),
            value=value
        )

        formatted_message = self.formatter.format_message(message)

        if self.storage.store_message(message):
            return json.loads(formatted_message)
        else:
            raise Exception("Failed to store message")



class DatabaseMessage:
    @staticmethod
    def create(db_path = "output_messages.db"):
        formatter = JsonMessageFormatter()
        storage = SQLiteMessageStorage(db_path)
        timestamp_generator = UTCTimestampGenerator()
        storage.connect()
        return MessageProducer(formatter, storage, timestamp_generator=timestamp_generator)





