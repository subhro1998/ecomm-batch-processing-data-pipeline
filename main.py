from src.ingestion.load.csv_reader import BronzeIngestionCSV

if __name__ == "__main__":
    env = 'local'
    bronze_layer_processing = BronzeIngestionCSV(env=env)
    bronze_layer_processing.load_csv(env=env, batch_run_time='00')
