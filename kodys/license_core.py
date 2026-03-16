import os
import uuid
import hashlib
import hmac

LICENSE_SECRET = b"KODYS_SECURE_ENTERPRISE_LICENSE_KEY_2026_!@#$"
LICENSE_FILE = "kodys_license.dat"

# --- Centralized Writable Data Path ---
import sys
if getattr(sys, 'frozen', False):
    if sys.platform == 'win32':
        KODYS_DATA_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.join(os.path.expanduser("~"), "AppData", "Local")), "KodysCAN")
    else:
        KODYS_DATA_DIR = os.path.join(os.path.expanduser("~"), ".kodys_can")
else:
    # Use config dir in root for development
    KODYS_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config"))

if not os.path.exists(KODYS_DATA_DIR):
    os.makedirs(KODYS_DATA_DIR)

def get_hardware_id():
    """Generates a unique hardware footprint for the machine."""
    try:
        mac = uuid.getnode()
        hw_hash = hashlib.sha256(str(mac).encode('utf-8')).hexdigest()
        formatted_id = f"KODY-{hw_hash[:4].upper()}-{hw_hash[4:8].upper()}-{hw_hash[8:12].upper()}"
        return formatted_id
    except Exception:
        return "KODY-ERR0-HARD-WARE1"

def generate_expected_license(hardware_id):
    signature = hmac.new(LICENSE_SECRET, hardware_id.encode('utf-8'), hashlib.sha256).hexdigest()
    key = f"{signature[:4]}-{signature[4:8]}-{signature[8:12]}-{signature[12:16]}-{signature[16:20]}".upper()
    return key

def verify_license(hardware_id, user_license_key):
    expected_key = generate_expected_license(hardware_id)
    # Robust comparison: ignore dashes and spaces
    clean_user = user_license_key.replace("-", "").replace(" ", "").upper()
    clean_expected = expected_key.replace("-", "").replace(" ", "").upper()
    return clean_user == clean_expected

def get_license_filepath():
    return os.path.join(KODYS_DATA_DIR, LICENSE_FILE)

def load_saved_license():
    path = get_license_filepath()
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return ""

def save_license(license_key):
    path = get_license_filepath()
    # Save the key in standard format (with dashes)
    clean_key = license_key.replace("-", "").replace(" ", "").upper()
    formatted_key = f"{clean_key[:4]}-{clean_key[4:8]}-{clean_key[8:12]}-{clean_key[12:16]}-{clean_key[16:20]}"
    with open(path, 'w') as f:
        f.write(formatted_key)

def is_system_licensed():
    """Returns True if the system has a valid license."""
    hw_id = get_hardware_id()
    saved_key = load_saved_license()
    return verify_license(hw_id, saved_key)
