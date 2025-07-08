import os
import sys
import click
import requests
from flask.cli import with_appcontext

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.anomaly import Anomaly
from app.models.maintenance import MaintenanceWindow as Maintenance
from app.models.action_plan import ActionPlan
from app.core.embedding_store import (
    format_anomaly_document, format_maintenance_document, 
    format_action_plan_document
)

EMBEDDING_SERVICE_URL = os.getenv('EMBEDDING_SERVICE_URL')

@click.command('index-db')
@with_appcontext
def index_database_command():
    """
    Indexes all content from the database by sending it to the standalone embedding service.
    """
    if not EMBEDDING_SERVICE_URL:
        click.secho("EMBEDDING_SERVICE_URL is not set. Please configure it in your .env file.", fg='red')
        sys.exit(1)

    click.echo("Starting database indexing process via embedding service...")
    
    try:
        documents, metadatas, ids = [], [], []

        # 1. Format Anomalies
        anomalies = Anomaly.query.all()
        click.echo(f"Found {len(anomalies)} anomalies to format.")
        for anomaly in anomalies:
            documents.append(format_anomaly_document(anomaly))
            metadatas.append({'source': 'anomaly', 'id': anomaly.id})
            ids.append(f"anomaly_{anomaly.id}")

        # 2. Format Maintenance records
        maintenances = Maintenance.query.all()
        click.echo(f"Found {len(maintenances)} maintenance records to format.")
        for maint in maintenances:
            documents.append(format_maintenance_document(maint))
            metadatas.append({'source': 'maintenance', 'id': maint.id})
            ids.append(f"maintenance_{maint.id}")

        # 3. Format Action Plans
        action_plans = ActionPlan.query.all()
        click.echo(f"Found {len(action_plans)} action plans to format.")
        for plan in action_plans:
            documents.append(format_action_plan_document(plan))
            metadatas.append({'source': 'action_plan', 'id': plan.id})
            ids.append(f"action_plan_{plan.id}")

        if not documents:
            click.echo("No documents to index. The database might be empty.")
            return

        # Send all documents to the embedding service in one batch
        click.echo(f"Sending {len(documents)} documents to the embedding service...")
        payload = {"texts": documents, "metadatas": metadatas, "ids": ids}
        response = requests.post(f"{EMBEDDING_SERVICE_URL}/index", json=payload)
        response.raise_for_status()
        
        click.secho(f"Successfully indexed all database content via the embedding service: {response.json()}", fg='green')

    except requests.RequestException as e:
        click.secho(f"An error occurred while calling the embedding service: {e}", fg='red')
        sys.exit(1)
    except Exception as e:
        click.secho(f"An unexpected error occurred during indexing: {e}", fg='red')
        sys.exit(1)

if __name__ == '__main__':
    # To run this script, you need a Flask app context.
    # It's better to run it via the Flask CLI.
    # Example: flask index-db
    # However, to make it runnable directly, we can create an app context.
    app = create_app()
    with app.app_context():
        # This setup allows running `python scripts/index_database.py`
        # but the click command is the primary interface.
        # The command needs to be registered with the app.
        pass

# To make this command available via `flask index-db`, 
# you would typically register it in your `run.py` or a similar entry point.
# For example, in `run.py`:
#
# from scripts.index_database import index_database_command
# app = create_app()
# app.cli.add_command(index_database_command)
#
# This script is now ready to be used.
