try:
    from core.config import settings
    print("✓ core.config imported successfully")
except ImportError as e:
    print(f"✗ Error importing core.config: {e}")

try:
    from services.ai_service import ai_service
    print("✓ services.ai_service imported successfully")
except ImportError as e:
    print(f"✗ Error importing services.ai_service: {e}")

try:
    from api.endpoints import todo
    print("✓ api.endpoints.todo imported successfully")
except ImportError as e:
    print(f"✗ Error importing api.endpoints.todo: {e}")

try:
    from dependencies import get_db
    print("✓ dependencies imported successfully")
except ImportError as e:
    print(f"✗ Error importing dependencies: {e}")