# 🩺 Kodys CAN: Clinical Licensing & Fleet Procedures

This guide outlines the standard operating procedures (SOP) for managing software licenses, activating clinical workstations, and monitoring your global fleet using the **Enterprise License Terminal**.

---

## 1. Administrative License Provisioning
**Location:** Central Admin Portal `/admin/license/`

When a new hospital or doctor purchases the Kodys software, follow these steps:

1.  **Obtain Hardware ID:** Ask the customer to launch the app. They will see a blocked screen showing a unique **Hardware ID** (e.g., `KODY-7F13-1C77-DFAA`).
2.  **Access the Terminal:** Log into the Admin Portal as a Superuser.
3.  **Generate Key:**
    *   **Customer Name:** Enter the doctor or hospital name.
    *   **Hardware ID:** Paste the ID. The system handles dashes/spaces automatically.
    *   **Internal Notes:** Add any technical or billing notes (e.g., "Trial for 3 months").
4.  **Automatic De-duplication:** If you register the same Hardware ID twice, the system will **update** the existing record instead of creating a duplicate.

---

## 2. Customer Activation Methods
There are two ways to activate a workstation. **Method B is recommended** for high-reliability medical environments.

### Method A: Manual 20-Digit Key
1. Copy the generated key from the dashboard (e.g., `FDE4-E475-3A05-F89C-D1BF`).
2. Send this to the customer. They type/paste it and click **Activate Software**.

### Method B: Offline License File (.dat) [Recommended]
1. Click the **📥 Download** icon in the Admin Dashboard for that specific license.
2. Send the `kodys_license.dat` file to the customer.
3. The customer clicks **"Import License File (.dat)"** in the app and selects the file. Activation is instant.

---

## 3. Global Fleet Monitoring (v3.6)
The Kodys platform features a real-time **Clinical Pulse** engine. You can monitor every install from your central office:

*   **PULSE Indicator:** A pulsing green light means the machine is "Live" or was used recently.
*   **Last Seen:** Shows exactly how long ago the doctor last launched the software (e.g., *"10 minutes ago"*).
*   **Version Tracking:** Displays the exact software version the customer is running.
*   **Status Legend:**
    *   **PENDING SYNC:** Key generated/sent, but the customer has not yet successfully run the app.
    *   **ACTIVE:** Customer has validated the key, and the machine has performed its first "Handshake" with your server.
    *   **REVOKED:** You have manually disabled the license. The software will **Lock Out** the user on their next launch.

---

## 4. Incident Analysis & Troubleshooting
The application is designed to run as a **Standard User**. No "Run as Administrator" is required.

### A. Check the Black-Box Log
Ask the customer to send you the **`kodys_debug.log`** file.
*   **Windows Location:** `%USERPROFILE%\kodys_debug.log`
*   **Mac Location:** `~/kodys_debug.log`
*   *This log captures every cryptographic event and system permission error.*

### B. macOS Security Bypass (Gatekeeper)
MacOS may show: *"Apple could not verify..."* or *"Malware warning"*.

**Standard Procedural Fix (v4.9):**
1.  Open the **KodysCAN-Setup.dmg**.
2.  **CRITICAL:** **Right-Click** (do not double-click) the file **`🛡️_ENABLE_SECURITY.command`**.
3.  Select **Open** from the menu.
4.  A prompt will appear; click **Open** again.
5.  Enter your Mac password (it will say *"Cleaning Quarantine"*).
6.  You can now launch **KodysCAN** normally.

**How to Trace/Find the Cause:**
If you want to verify why it's blocked, open Terminal and run:
`ls -l@ /Applications/KodysCAN.app`
If you see **`com.apple.quarantine`**, macOS is intentionally holding the app in "Isolation" because it was downloaded from the web.

### C. Problem / Solution Ledger
| Incident | Symptom | Fix |
| :--- | :--- | :--- |
| **Silent Hang** | Button clicked, nothing happens. | Check `kodys_debug.log`. Ensure antivirus is not blocking the app. |
| **Invalid Key** | "Key Mismatch" in logs. | Ensure they didn't copy the Hardware ID by mistake. Use **Method B (File Import)**. |
| **No Sync** | Status stays `PENDING` in Admin. | Machine has no internet. You can manually click 🔄 in Admin to force status change. |

---

## 5. Security & Maintenance
*   **🗑️ Record Management:** Use the Trash icon to remove trial or demo licenses.
*   **🔄 Remote Lockdown:** If a license is compromised, click the toggle icon to change status to **REVOKED**. The customer app will receive a "Kill Signal" on the next launch and terminate the session.
*   **Hardware Changes:** If a customer replaces their PC, the Hardware ID will change. You must generate a **New License** for the new ID.

---
*Document Version: 3.7*  
*Last Updated: March 2026*
