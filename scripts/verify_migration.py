#!/usr/bin/env python3
"""
TAMS migration verification script - checks if we can import and run the application
"""
import os
import sys
import importlib

def try_import_all():
    """Try to import all modules to verify imports are working"""
    modules = [
        'app',
        'app.api',
        'app.api.v1',
        'app.api.v1.endpoints.auth',
        'app.api.v1.endpoints.anomalies',
        'app.api.v1.endpoints.predictions',
        'app.api.v1.endpoints.status',
        'app.api.v1.endpoints.maintenance',
        'app.api.v1.endpoints.action_plans',
        'app.api.v1.endpoints.dashboard',
        'app.api.v1.endpoints.import_data',
        'app.models',
        'app.models.user',
        'app.models.anomaly',
        'app.models.maintenance',
        'app.models.action_plan',
        'app.models.database',
        'app.core',
        'app.core.predictor',
        'app.core.browsable_api',
        'app.core.error_handlers',
        'app.utils',
        'app.utils.enhanced_auth',
    ]
    
    print("\n\033[1;34mVerifying module imports...\033[0m")
    
    success = True
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            print(f"\033[1;32m✓ {module_name}\033[0m")
        except ImportError as e:
            print(f"\033[1;31m× {module_name}: {str(e)}\033[0m")
            success = False
    
    return success

def try_create_app():
    """Try to create the Flask application"""
    print("\n\033[1;34mVerifying app creation...\033[0m")
    
    try:
        from app import create_app
        app = create_app()
        print(f"\033[1;32m✓ Application created successfully\033[0m")
        
        # Print registered routes
        print("\n\033[1;34mVerifying API routes...\033[0m")
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.endpoint}: {rule}")
        
        # Sort and print routes
        for route in sorted(routes):
            print(f"\033[1;32m✓ {route}\033[0m")
        
        return True
    except Exception as e:
        print(f"\033[1;31m× Error creating application: {str(e)}\033[0m")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print("\033[1;32m" + "=" * 80)
    print(" TAMS Migration Verification ")
    print("=" * 80 + "\033[0m")
    
    # Add project root to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.append(project_root)
    print(f"Added {project_root} to Python path")
    
    imports_ok = try_import_all()
    app_ok = try_create_app()
    
    print("\n\033[1;32m" + "=" * 80)
    if imports_ok and app_ok:
        print(" Verification PASSED ✓ ")
    else:
        print(" Verification FAILED × ")
    print("=" * 80 + "\033[0m")
    
    if imports_ok and app_ok:
        print("\nAll tests passed! The migration appears to be successful.")
        print("\nNext steps:")
        print("1. Run 'python scripts/cleanup.py' to remove old files")
        print("2. Test the application with 'python run.py'")
        print("3. Verify API endpoints work as expected")
    else:
        print("\nSome tests failed. Review the errors above and fix them.")

if __name__ == "__main__":
    main()
