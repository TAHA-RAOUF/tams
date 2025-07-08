import os
import requests
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
EMBEDDING_SERVICE_URL = os.getenv('EMBEDDING_SERVICE_URL')

# --- Document Formatting Functions ---

def format_anomaly_document(anomaly):
    """Formats an anomaly record into a text document for embedding."""
    rex_info = f"REX file is available at {anomaly.rex_file}." if anomaly.rex_file else "No REX file is associated with this anomaly."
    return (
        f"Anomaly Record ID {anomaly.id}: '{anomaly.description}' reported on {anomaly.created_at.strftime('%Y-%m-%d')}. "
        f"The affected component is '{anomaly.component_name}' on equipment '{anomaly.equipment_name}'. "
        f"Current status is '{anomaly.status}'. "
        f"{rex_info}"
    )

def format_maintenance_document(maintenance):
    """Formats a maintenance record into a text document for embedding."""
    return (
        f"Maintenance Record ID {maintenance.id} for Anomaly ID {maintenance.anomaly_id}: "
        f"Scheduled from {maintenance.start_date.strftime('%Y-%m-%d')} to {maintenance.end_date.strftime('%Y-%m-%d')}. "
        f"The status is '{maintenance.status}'. Notes: '{maintenance.notes}'."
    )

def format_action_plan_document(action_plan):
    """Formats an action plan record into a text document for embedding."""
    return (
        f"Action Plan ID {action_plan.id} for Anomaly ID {action_plan.anomaly_id}: "
        f"'{action_plan.description}'. Due by {action_plan.due_date.strftime('%Y-%m-%d')}. "
        f"Current status is '{action_plan.status}'."
    )

# --- Unified Indexing/Deletion Functions ---

def index_record(record):
    """
    Determines the type of a database record, formats it, and indexes it.
    """
    doc = None
    metadata = {}
    record_id = None

    if record.__tablename__ == 'anomalies':
        doc = format_anomaly_document(record)
        metadata = {'source': 'anomaly', 'id': record.id}
        record_id = f"anomaly_{record.id}"
    elif record.__tablename__ == 'maintenance':
        doc = format_maintenance_document(record)
        metadata = {'source': 'maintenance', 'id': record.id}
        record_id = f"maintenance_{record.id}"
    elif record.__tablename__ == 'action_plans':
        doc = format_action_plan_document(record)
        metadata = {'source': 'action_plan', 'id': record.id}
        record_id = f"action_plan_{record.id}"

    if doc and record_id:
        try:
            payload = {"texts": [doc], "metadatas": [metadata], "ids": [record_id]}
            response = requests.post(f"{EMBEDDING_SERVICE_URL}/index", json=payload)
            response.raise_for_status()
            print(f"Successfully indexed record via service: {record_id}")
        except requests.RequestException as e:
            print(f"Error calling embedding service to index record {record_id}: {e}")

def delete_record(record):
    """
    Deletes a record from the vector store based on its type and ID.
    """
    record_id = None
    if record.__tablename__ == 'anomalies':
        record_id = f"anomaly_{record.id}"
    elif record.__tablename__ == 'maintenance':
        record_id = f"maintenance_{record.id}"
    elif record.__tablename__ == 'action_plans':
        record_id = f"action_plan_{record.id}"

    if record_id:
        try:
            payload = {"ids": [record_id]}
            response = requests.post(f"{EMBEDDING_SERVICE_URL}/delete", json=payload)
            response.raise_for_status()
            print(f"Successfully deleted record via service: {record_id}")
        except requests.RequestException as e:
            print(f"Error calling embedding service to delete record {record_id}: {e}")
