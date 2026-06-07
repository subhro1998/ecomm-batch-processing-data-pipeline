from pydantic import BaseModel


class BatchInput(BaseModel):
    """
    This class represents the required input for a batch processing job
    """
    environment: str
    batch_category: str
    batch_processing_category: str
    source_system: str
    processing_layer: str
    batch_run_date: str
    batch_run_time: str
