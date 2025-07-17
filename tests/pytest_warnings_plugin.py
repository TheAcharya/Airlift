import warnings
import pytest

def pytest_configure(config):
    """Configure pytest to suppress specific warnings."""
    # Suppress all deprecation warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    
    # Suppress specific Pydantic warnings
    warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince211.*")
    warnings.filterwarnings("ignore", message=".*model_fields.*deprecated.*")
    warnings.filterwarnings("ignore", message=".*Accessing the 'model_fields' attribute.*")

def pytest_collection_modifyitems(config, items):
    """Modify test items to suppress warnings."""
    for item in items:
        # Add warning suppression to each test
        item.add_marker(pytest.mark.filterwarnings("ignore::DeprecationWarning"))
        item.add_marker(pytest.mark.filterwarnings("ignore::UserWarning"))
        item.add_marker(pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")) 