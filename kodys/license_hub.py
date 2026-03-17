"""
Kodys CLINICAL HUB: Master Licensing & Usage Engine (v8.0)
Centralized logic for Generating, Activating, and Deactivating licenses.
"""
import logging
from .models import TX_MASTER_GENERATED_LICENSES
from . import license_core
from django.utils import timezone

logger = logging.getLogger("KodysDiagnostic")

def generate_new_license(client_name, hardware_id, email=None, notes=None):
    """Generates a cryptographic key and saves it to the Master Registry."""
    # Ensure key matches the hardware ID using the standard HMAC logic
    key = license_core.generate_expected_license(hardware_id)
    
    license_entry = TX_MASTER_GENERATED_LICENSES.objects.create(
        CLIENT_NAME=client_name,
        HARDWARE_ID=hardware_id,
        EMAIL=email,
        GENERATED_KEY=key,
        NOTES=notes,
        STATUS="PENDING_ACTIVATION",
        IS_ACTIVE=True
    )
    return license_entry

def process_client_pulse(hardware_id, key, machine_name=None, version_info=None):
    """
    Handles a pulse from a desktop client.
    Verifies key validity and returns current license status.
    """
    try:
        # 1. Verification of the key format/correctness locally
        if not license_core.verify_license(hardware_id, key):
            return {"status": "INVALID", "message": "Cryptographic mismatch with local hardware footprint."}

        # 2. Check the Central Database for this Hardware ID
        lic = TX_MASTER_GENERATED_LICENSES.objects.filter(HARDWARE_ID=hardware_id, GENERATED_KEY=key).first()
        
        if not lic:
            # If valid cryptographically but not in DB, it might be a pre-generated manual key
            # We auto-register it if we want to allow manual keys, or block it.
            # For strict control, we return UNAUTHORIZED.
            return {"status": "UNAUTHORIZED", "message": "Hardware NOT registered in Central Hub."}

        # 3. Check if Admin has deactivated this seat
        if not lic.IS_ACTIVE:
            return {"status": "REVOKED", "message": "Activation has been revoked by Clinical Administrator."}

        # 4. Update Heartbeat and Session Info
        lic.LAST_HEARTBEAT = timezone.now()
        lic.STATUS = "ACTIVE"
        if machine_name: lic.MACHINE_NAME = machine_name
        if version_info: lic.VERSION_INFO = version_info
        lic.save()

        return {
            "status": "APPROVED",
            "message": "License Verified.",
            "client": lic.CLIENT_NAME,
            "expiry": "PERPETUAL" # Can be expanded to Handle Subscription Dates
        }

    except Exception as e:
        logger.error(f"Licensing Hub Error: {e}")
        return {"status": "ERROR", "message": str(e)}

def toggle_license_status(lic_pk, is_active):
    """Deactivates/Activates a license from the admin portal."""
    lic = TX_MASTER_GENERATED_LICENSES.objects.filter(pk=lic_pk).first()
    if lic:
        lic.IS_ACTIVE = is_active
        lic.STATUS = "ACTIVE" if is_active else "REVOKED"
        lic.save()
        return True
    return False
