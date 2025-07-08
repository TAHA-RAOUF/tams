"""
This module defines SQLAlchemy event listeners to automatically synchronize 
the ChromaDB vector store with database changes.
"""
from sqlalchemy import event
from app.models.anomaly import Anomaly
from app.models.maintenance import MaintenanceWindow as Maintenance
from app.models.action_plan import ActionPlan
from app.core.embedding_store import index_record, delete_record

def register_event_listeners(app):
    """
    Registers listeners for database events (after_insert, after_update, after_delete)
    for the Anomaly, Maintenance, and ActionPlan models.
    """
    models = [Anomaly, Maintenance, ActionPlan]

    for model in models:
        @event.listens_for(model, 'after_insert')
        def after_insert_listener(mapper, connection, target):
            """Calls index_record after a new record is inserted."""
            with app.app_context():
                print(f"Detected insert for {type(target).__name__} ID: {target.id}. Triggering indexing.")
                index_record(target)

        @event.listens_for(model, 'after_update')
        def after_update_listener(mapper, connection, target):
            """Calls index_record after a record is updated."""
            with app.app_context():
                print(f"Detected update for {type(target).__name__} ID: {target.id}. Triggering re-indexing.")
                index_record(target)

        @event.listens_for(model, 'after_delete')
        def after_delete_listener(mapper, connection, target):
            """Calls delete_record after a record is deleted."""
            with app.app_context():
                print(f"Detected delete for {type(target).__name__} ID: {target.id}. Triggering deletion from index.")
                delete_record(target)

    print("SQLAlchemy event listeners registered for automatic indexing.")
