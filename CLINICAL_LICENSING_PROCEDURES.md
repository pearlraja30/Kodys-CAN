# 🩺 Kodys CAN: Clinical Licensing & Fleet Procedures

This guide outlines the standard operating procedures (SOP) for managing software licenses, activating clinical workstations, and troubleshooting installation incidents for the Kodys CAN platform.

---

## 1. Administrative License Provisioning
**Location:** Central Admin Portal `/admin/license/`

When a new hospital or doctor purchases the Kodys software, follow these steps to provision their access:

1.  **Obtain Hardware ID:** Ask the customer to launch the app. They will see a blocked screen showing a `Hardware ID` (e.g., `KODY-7F13-1C77-DFAA`).
2.  **Access the Dashboard:** Log into the **Enterprise License Terminal** using Superuser credentials.
3.  **Generate Key:**
    *   Enter the **Client/Hospital Name**.
    *   Paste the **Hardware ID** (Dashes/spaces are automatically handled).
    *   Click **SECURELY GENERATE KEY**.
4.  **License Ledger:** The new key is now saved in the master ledger with a status of `PENDING SYNC`.

---

## 2. Customer Activation Methods
There are two ways to activate a customer's machine. **Method B is recommended** for high-reliability medical environments.

### Method A: Manual 20-Digit Key
*   Copy the generated key (e.g., `FDE4-E475-3A05-F89C-D1BF`).
*   Send this key via Email/WhatsApp to the customer.
*   The customer pastes it into the "Enter License Key" field and clicks **Activate Software**.

### Method B: Offline License File (.dat) [Recommended]
*   In the Admin Dashboard, click the **📥 Download** icon next to the license record.
*   This downloads a file named `kodys_license.dat`.
*   Send this file to the customer (via Email or Pen-Drive).
*   The customer clicks **"Import License File (.dat)"** in the app, selects the file, and is activated instantly.

---

## 3. Real-Time Fleet Monitoring
The Kodys platform features **Global Sync V3.5**. You can monitor your installs from the central office:

*   **PENDING SYNC:** The key has been sent but the customer has not yet successfully activated the app.
*   **ACTIVE:** The customer has validated the key locally, and their machine has sent a "Handshake" back to your server.
*   **REVOKED:** You have manually disabled the license (click the 🔄 toggle), and the software will block access on the next launch.

---

## 4. Incident Analysis & Troubleshooting
If a customer reports that "Activation is doing nothing" or "The button hangs," perform the following analysis:

### A. Check the Black-Box Log
Ask the customer to send you the file: **`kodys_debug.log`**
*   **Windows Location:** `%USERPROFILE%\kodys_debug.log`
*   **Mac Location:** `~/kodys_debug.log`

Search the log for keywords: `[ERROR]`, `FATAL`, or `Key Mismatch`.

### C. macOS Security Bypass (Gatekeeper)
Because the app is built for clinical environments without an Apple Store subscription, macOS will show a message: *"Apple could not verify..."*
**Workaround:**
1.  **Right-click** (or Command-Click) the application icon.
2.  Select **Open** from the menu.
3.  A now-different window will appear with an **Open** button. Click it.
4.  This only needs to be done **once**. Subsequent launches will work normally.

### D. Common Issues & Solutions
| Incident | Symptom | Fix |
| :--- | :--- | :--- |
| **Silent Hang** | Button clicked, nothing happens. | Check `kodys_debug.log` for **Permission Denied**. Ask user to **Run as Administrator**. |
| **Invalid Key** | "Key Mismatch" in logs. | Ensure they didn't copy the ID instead of the Key. Use **Method B (File Import)**. |
| **No Sync** | Status stays `PENDING` even after use. | Customer machine has no internet or is behind a Firewall. You can click 🔄 in Admin to **Force Activate**. |

---

## 5. System Maintenance
*   **Deleting Records:** Click the 🗑️ icon to remove trial or demo licenses.
*   **License Security:** The `LICENSE_SECRET` is embedded in the binary. Never share the source code with customers.
*   **Hardware Changes:** If a customer replaces their motherboard or hard drive, their Hardware ID will change, and you must generate a **New License**.

---
*Document Version: 3.5.2*  
*Last Updated: March 2026*
