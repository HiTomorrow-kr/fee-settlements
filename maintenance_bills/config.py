import os

# maintenance_bills owns its own data and template locations. Orchestrators
# just launch this program as a subprocess and never need to know or pass
# any of this.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.environ.get("MAINTENANCE_BILLS_DATA_DIR") or os.path.join(_REPO_ROOT, "data")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
IMAGES_DIR = os.path.join(DATA_DIR, "bills")

TEMPLATES_DIR = os.path.join(_REPO_ROOT, "templates")

# Fixed fee amounts and meter unit prices are edited by hand in this file.
CONFIG_PATH = os.path.join(_REPO_ROOT, "bill_config.json")
