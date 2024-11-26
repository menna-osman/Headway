from data_ingestor import CSVDataReader, DataFilter, DataIngestor
from equation_reader import FileConfigReader, EquationReader, VariableReplacer, EquationProcessor
from interpreter import Lexer, Parser, Interpreter, token_map
from message_producer import DatabaseMessage


def create_equation_processor(asset_id):
    equation_reader = EquationReader(asset_id=asset_id, db_path=".\kpi_project\db.sqlite3")
    variable_processor = VariableReplacer()
    return EquationProcessor(equation_reader, variable_processor)


def process_equation(equation_str, record):
    lexer = Lexer(equation_str,token_map)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    return interpreter.interpret()


def main():
    csv_reader = CSVDataReader('asset_data.csv')
    data_filter = DataFilter()
    data_ingestor = DataIngestor(csv_reader, data_filter, interval=5)
    message_producer = DatabaseMessage.create(db_path="output_messages.db")

    try:
        for record in data_ingestor.process():
            try:
                equation_processor = create_equation_processor(record['asset_id'])
                processed_equation = equation_processor.process_equation(record)

                if processed_equation:
                    result = process_equation(processed_equation, record)  # Added record parameter
                    output_message = message_producer.produce_message(
                        asset_id=record['asset_id'],
                        attribute_id=record['attribute_id'],
                        value=str(result)
                    )
                    print(f"Processed message: {output_message}")
                else:
                    print(f"No equation found for asset_id: {record['asset_id']}")

            except Exception as e:
                print(f"Error processing record {record}: {str(e)}")
                continue

    except KeyboardInterrupt:
        print("\nStopping the application...")
    except Exception as e:
        print(f"Application error: {str(e)}")
    finally:
        csv_reader.close_file()
        if message_producer and message_producer.storage:
            message_producer.storage.disconnect()


if __name__ == "__main__":
    main()