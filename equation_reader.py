from abc import ABC, abstractmethod
import yaml
import sqlite3
import os

# Interfaces
class ConfigReader(ABC):
    @abstractmethod
    def read_config(self):
        pass

class EquationReaderInterface(ABC):
    @abstractmethod
    def get_equation(self) :
        pass

class VariableProcessorInterface(ABC):
    @abstractmethod
    def process(self, equation, record):
        pass



# Implementations
class FileConfigReader(ConfigReader):
    def __init__(self, config_file):
        self.config_file = config_file

    def read_config(self):
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)

        except FileNotFoundError:
            print(f"Error: Config file '{self.config_file}' not found.")

class EquationConfigReader(EquationReaderInterface):
    def __init__(self, config_reader: ConfigReader):
        self.config_reader = config_reader
        self.variable_replacer = None

    def get_equation(self):
        config = self.config_reader.read_config()
        equation = config['equation']
        return equation





class EquationReader(EquationReaderInterface):
    def __init__(self, asset_id, db_path):
        self.asset_id = asset_id
        self.db_path = db_path

    def get_equation(self):
        """
        Fetch equation from SQLite database based on asset_id
        """
        connection = None
        try:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Database file not found at: {self.db_path}")

            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            cursor.execute("""
                SELECT k.expression 
                FROM kpi_monitor_assetkpi ak
                JOIN kpi_monitor_kpi k ON ak.kpi_id = k.id
                WHERE ak.asset_id = ?
            """, (self.asset_id,))

            result = cursor.fetchone()
            return result[0] if result else None

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

        finally:
            if connection:
                connection.close()

class VariableReplacer(VariableProcessorInterface):

        """
        Replace variables in equation with values from the current record
        """
        def process(self, equation, record) :
            result = equation
            # for var_name, value in record.items():
            #     formatted_value = str(value)
            #     result = result.replace(var_name, formatted_value)
            result = result.replace("ATTR", record['attribute_id'])
            return result



# select weather to process from a config or from kpi db
class EquationProcessor:
    def __init__(self,
                 equation_provider: EquationReaderInterface,
                 variable_processor: VariableProcessorInterface):
        self.equation_provider = equation_provider
        self.variable_processor = variable_processor

    def process_equation(self, record) :
        equation = self.equation_provider.get_equation()
        return self.variable_processor.process(equation, record)

