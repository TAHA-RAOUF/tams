"""
API route registration
"""
from app.api.v1.endpoints.auth import RegisterAPI, LoginAPI, LogoutAPI, ProfileAPI
from app.api.v1.endpoints.anomalies import (
    AnomalyAPI, BatchAnomalyAPI, FileAnomalyAPI, 
    AnomalyApprovalAPI, AnomalyPredictionEditAPI
)
from app.api.v1.endpoints.status import AnomalyStatusAPI, AnomalyBulkStatusAPI
from app.api.v1.endpoints.maintenance import MaintenanceWindowAPI, ScheduleAnomalyAPI
from app.api.v1.endpoints.action_plans import ActionPlanAPI, ActionItemAPI
from app.api.v1.endpoints.dashboard import (
    DashboardMetricsAPI, AnomaliesByMonthAPI, AnomaliesByServiceAPI, 
    AnomaliesByCriticalityAPI, MaintenanceWindowChartAPI
)
from app.api.v1.endpoints.import_data import ImportAnomaliesAPI
from app.api.v1.endpoints.predictions import (
    EquipmentReliabilityPredictorAPI as PredictAPI,
    BatchEquipmentPredictorAPI as BatchPredictAPI,
    FileEquipmentPredictorAPI as FilePredictAPI
)

def register_routes(app, api):
    """Register all API routes"""
    
    # Authentication endpoints
    api.add_resource(RegisterAPI, '/auth/register')
    api.add_resource(LoginAPI, '/auth/login')
    api.add_resource(LogoutAPI, '/auth/logout')
    api.add_resource(ProfileAPI, '/auth/profile')
    
    # Anomaly management endpoints
    api.add_resource(AnomalyAPI, '/anomalies', '/anomalies/<int:anomaly_id>')
    api.add_resource(BatchAnomalyAPI, '/anomalies/batch')
    api.add_resource(FileAnomalyAPI, '/anomalies/upload')
    api.add_resource(AnomalyApprovalAPI, '/anomalies/<int:anomaly_id>/approve')
    api.add_resource(AnomalyPredictionEditAPI, '/anomalies/<int:anomaly_id>/predictions')
    api.add_resource(AnomalyStatusAPI, '/anomalies/<int:anomaly_id>/status')
    api.add_resource(AnomalyBulkStatusAPI, '/anomalies/bulk/status')
    
    # Register maintenance window endpoints
    api.add_resource(MaintenanceWindowAPI, '/maintenance-windows', '/maintenance-windows/<int:window_id>')
    api.add_resource(ScheduleAnomalyAPI, '/maintenance-windows/<int:window_id>/schedule-anomaly')
    
    # Register action plan endpoints
    api.add_resource(ActionPlanAPI, '/action-plans', '/action-plans/<int:anomaly_id>')
    api.add_resource(ActionItemAPI, '/action-plans/<int:action_plan_id>/items', 
                    '/action-plans/<int:action_plan_id>/items/<int:item_id>')
    
    # Register dashboard endpoints
    api.add_resource(DashboardMetricsAPI, '/dashboard/metrics')
    api.add_resource(AnomaliesByMonthAPI, '/dashboard/charts/anomalies-by-month')
    api.add_resource(AnomaliesByServiceAPI, '/dashboard/charts/anomalies-by-service')
    api.add_resource(AnomaliesByCriticalityAPI, '/dashboard/charts/anomalies-by-criticality')
    api.add_resource(MaintenanceWindowChartAPI, '/dashboard/charts/maintenance-windows')
    
    # Register data import endpoints
    api.add_resource(ImportAnomaliesAPI, '/import/anomalies')
    
    # Register prediction endpoints
    api.add_resource(PredictAPI, '/predict')
    api.add_resource(BatchPredictAPI, '/predict-batch')
    api.add_resource(FilePredictAPI, '/predict-file')
    
    return api
