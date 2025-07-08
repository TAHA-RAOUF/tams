# dashboard_api.py
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Anomaly, MaintenanceWindow, ActionPlan, ActionItem
from datetime import datetime, timedelta
from sqlalchemy import func, extract, case, desc
import json

class DashboardMetricsAPI(Resource):
    @jwt_required()
    def get(self):
        """Get dashboard metrics and KPIs"""
        try:
            # Get current date
            now = datetime.utcnow()
            
            # Total anomalies
            total_anomalies = db.session.query(func.count(Anomaly.id)).scalar()
            
            # Anomalies by status
            status_counts = db.session.query(
                Anomaly.status, 
                func.count(Anomaly.id)
            ).group_by(Anomaly.status).all()
            
            status_data = {status: count for status, count in status_counts}
            
            # Open anomalies (not resolved or closed)
            open_anomalies = db.session.query(func.count(Anomaly.id))\
                .filter(Anomaly.status.in_(['open', 'in_progress']))\
                .scalar()
            
            # Anomalies created in last 30 days
            recent_anomalies = db.session.query(func.count(Anomaly.id))\
                .filter(Anomaly.created_at >= now - timedelta(days=30))\
                .scalar()
            
            # Average resolution time (for closed/resolved anomalies)
            # This is an approximation as we don't explicitly track resolution date
            avg_resolution_days = db.session.query(
                func.avg(func.julianday(Anomaly.updated_at) - func.julianday(Anomaly.created_at))
            ).filter(
                Anomaly.status.in_(['resolved', 'closed'])
            ).scalar()
            
            # Convert to days if not None
            avg_resolution_time = round(avg_resolution_days, 2) if avg_resolution_days else None
            
            # Critical anomalies (high criticality)
            critical_anomalies = db.session.query(func.count(Anomaly.id))\
                .filter(
                    ((Anomaly.use_user_scores == True) & (Anomaly.user_criticality_level >= 2.0)) |
                    ((Anomaly.use_user_scores == False) & (Anomaly.criticality_level >= 2.0))
                )\
                .scalar()
            
            # Maintenance windows
            total_windows = db.session.query(func.count(MaintenanceWindow.id)).scalar()
            
            active_windows = db.session.query(func.count(MaintenanceWindow.id))\
                .filter(
                    (MaintenanceWindow.start_date <= now) &
                    (MaintenanceWindow.end_date >= now) &
                    (MaintenanceWindow.status == 'in_progress')
                )\
                .scalar()
            
            upcoming_windows = db.session.query(func.count(MaintenanceWindow.id))\
                .filter(
                    (MaintenanceWindow.start_date > now) &
                    (MaintenanceWindow.status == 'scheduled')
                )\
                .scalar()
            
            # Action plans
            total_plans = db.session.query(func.count(ActionPlan.id)).scalar()
            
            metrics = {
                "anomalies": {
                    "total": total_anomalies,
                    "open": open_anomalies,
                    "critical": critical_anomalies,
                    "recent": recent_anomalies,
                    "by_status": status_data
                },
                "performance": {
                    "avg_resolution_time_days": avg_resolution_time
                },
                "maintenance": {
                    "total_windows": total_windows,
                    "active_windows": active_windows,
                    "upcoming_windows": upcoming_windows,
                    "total_plans": total_plans
                }
            }
            
            return {"metrics": metrics}, 200
            
        except Exception as e:
            return {"error": str(e)}, 500


class AnomaliesByMonthAPI(Resource):
    @jwt_required()
    def get(self):
        """Get anomalies by month for charting"""
        try:
            # Get year from query params, default to current year
            year = request.args.get('year', datetime.utcnow().year, type=int)
            
            # Query anomalies by month
            results = db.session.query(
                extract('month', Anomaly.date_detection).label('month'),
                func.count(Anomaly.id).label('count')
            ).filter(
                extract('year', Anomaly.date_detection) == year
            ).group_by(
                extract('month', Anomaly.date_detection)
            ).order_by(
                'month'
            ).all()
            
            # Format results
            months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            
            chart_data = [
                {
                    "month": months[int(month) - 1],
                    "month_num": int(month),
                    "count": count
                }
                for month, count in results
            ]
            
            # Fill in missing months with zero count
            existing_months = {item['month_num'] for item in chart_data}
            for month_num in range(1, 13):
                if month_num not in existing_months:
                    chart_data.append({
                        "month": months[month_num - 1],
                        "month_num": month_num,
                        "count": 0
                    })
            
            # Sort by month number
            chart_data.sort(key=lambda x: x['month_num'])
            
            return {"chart_data": chart_data, "year": year}, 200
            
        except Exception as e:
            return {"error": str(e)}, 500


class AnomaliesByServiceAPI(Resource):
    @jwt_required()
    def get(self):
        """Get anomalies grouped by service for charting"""
        try:
            # Query anomalies by service
            results = db.session.query(
                Anomaly.service,
                func.count(Anomaly.id).label('count')
            ).filter(
                Anomaly.service.isnot(None)
            ).group_by(
                Anomaly.service
            ).order_by(
                desc('count')
            ).all()
            
            # Format results
            chart_data = [
                {
                    "service": service or "Unspecified",
                    "count": count
                }
                for service, count in results
            ]
            
            return {"chart_data": chart_data}, 200
            
        except Exception as e:
            return {"error": str(e)}, 500


class AnomaliesByCriticalityAPI(Resource):
    @jwt_required()
    def get(self):
        """Get anomalies grouped by criticality level for charting"""
        try:
            # Define criticality levels
            criticality_ranges = [
                {"min": 0, "max": 1, "label": "Low"},
                {"min": 1, "max": 2, "label": "Medium"},
                {"min": 2, "max": 3, "label": "High"},
                {"min": 3, "max": 100, "label": "Critical"}
            ]
            
            # Query data for each range
            chart_data = []
            
            for range_def in criticality_ranges:
                # Query count using conditional logic for user vs AI scores
                count = db.session.query(func.count(Anomaly.id)).filter(
                    (
                        (Anomaly.use_user_scores == True) &
                        (Anomaly.user_criticality_level >= range_def["min"]) &
                        (Anomaly.user_criticality_level < range_def["max"])
                    ) | (
                        (Anomaly.use_user_scores == False) &
                        (Anomaly.criticality_level >= range_def["min"]) &
                        (Anomaly.criticality_level < range_def["max"])
                    )
                ).scalar()
                
                chart_data.append({
                    "criticality": range_def["label"],
                    "range": f"{range_def['min']}-{range_def['max']}",
                    "count": count
                })
            
            return {"chart_data": chart_data}, 200
            
        except Exception as e:
            return {"error": str(e)}, 500


class MaintenanceWindowChartAPI(Resource):
    @jwt_required()
    def get(self):
        """Get maintenance windows for timeline/calendar view"""
        try:
            # Get date range from query params
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)
            
            # Base query
            query = db.session.query(MaintenanceWindow)
            
            # Apply date filters if provided
            if start_date:
                try:
                    start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    query = query.filter(MaintenanceWindow.end_date >= start)
                except:
                    pass
            
            if end_date:
                try:
                    end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    query = query.filter(MaintenanceWindow.start_date <= end)
                except:
                    pass
            
            # Execute query
            windows = query.order_by(MaintenanceWindow.start_date).all()
            
            # Format results for timeline/calendar
            timeline_data = []
            for window in windows:
                # Count anomalies by status
                anomaly_counts = {}
                for anomaly in window.scheduled_anomalies:
                    status = anomaly.status
                    if status not in anomaly_counts:
                        anomaly_counts[status] = 0
                    anomaly_counts[status] += 1
                
                timeline_data.append({
                    "id": window.id,
                    "title": f"{window.type} - {window.description[:30]}...",
                    "start": window.start_date.isoformat(),
                    "end": window.end_date.isoformat(),
                    "status": window.status,
                    "type": window.type,
                    "description": window.description,
                    "anomaly_count": len(window.scheduled_anomalies),
                    "anomaly_status_counts": anomaly_counts
                })
            
            return {"timeline_data": timeline_data}, 200
            
        except Exception as e:
            return {"error": str(e)}, 500
