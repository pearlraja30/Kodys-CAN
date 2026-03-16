# -*- coding: utf-8 -*-
import sys
import logging
import json
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from . import app_api as api
from . import app_logger as ulo
from .forms import *
import ast
from . import license_core

login_url = "/signin/"
logger = logging.getLogger(settings.LOGGER_FILE_NAME)


# Create your views here.
def about(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, about_content = api.about_content(request)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


def customer_support(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        (
            result,
            msg,
            customer_support,
            customer_support_technical,
            customer_support_marketing,
            customer_support_product,
        ) = api.customer_support(request)
        if request.method == "POST":
            result, msg = api.service_email(request, request.POST.copy())

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


def signin(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        from . import license_core
        if not license_core.is_system_licensed():
            return HttpResponseRedirect(reverse('license_activation'))

        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("home"))

        if request.method == "POST":
            result, msg, validation_error = api.user_signin(
                request, request.POST.copy()
            )
            if result:
                return HttpResponseRedirect(reverse("home"))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def license_activation(request):
    """
    Django web-based fallback for License Activation.
    If the desktop wrapper is bypassed, this ensures the web UI still blocks usage.
    """
    fn = "license_activation"
    template_name = fn
    logger.info(ulo.start_log(request, fn))
    
    hardware_id = license_core.get_hardware_id()
    activation_error = ""
    
    if request.method == "POST":
        user_key = request.POST.get("license_key", "").strip()
        if license_core.verify_license(hardware_id, user_key):
            license_core.save_license(user_key)
            return HttpResponseRedirect(reverse("signin"))
        else:
            activation_error = "Invalid License Key. Please contact Kodys Administrator."

    logger.info(ulo.end_log(request, fn))
    # Using a simple raw HTML response for the fallback to avoid creating complex templates
    html = f"""
    <html>
      <head>
        <title>Kodys - Software Activation</title>
        <style>
          body {{ background: #f4f6f9; font-family: Arial; padding: 50px; text-align: center; }}
          .box {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }}
          input[type=text] {{ font-size: 16px; padding: 10px; width: 300px; margin: 10px 0; border: 1px solid #00bdb6; }}
          input[type=submit] {{ background: #00bdb6; color: white; padding: 10px 20px; font-size: 16px; border: none; cursor: pointer; }}
          .err {{ color: red; font-weight: bold; margin-bottom: 10px; }}
        </style>
      </head>
      <body>
        <div class="box">
            <h2 style="color: #333;">Kodys CAN - Security Activation</h2>
            <p>Your Hardware ID: <strong>{hardware_id}</strong></p>
            {"<p class='err'>" + activation_error + "</p>" if activation_error else ""}
            <form method="POST">
                <input type="text" name="license_key" placeholder="Enter 20-digit License Key" required /><br>
                <input type="submit" value="Activate" />
            </form>
        </div>
      </body>
    </html>
    """
    return HttpResponse(html)

@login_required(login_url=login_url)
def admin_license_dashboard(request):
    """
    Centralized portal for superadmins to generate cryptographic hardware
    license keys for Kodys CAN software and monitor active install footprint.
    """
    fn = "admin_license_dashboard"
    logger.info(ulo.start_log(request, fn))
    
    if not request.user.is_superuser:
        return HttpResponse("You are not authorized to view the Enterprise Admin Terminal.", status=403)
        
    msg = request.GET.get('msg_text', '')
    msg_class = request.GET.get('msg_class', '')
    
    if request.method == "POST":
        client_name = request.POST.get('client_name', '').strip()
        hardware_id = request.POST.get('hardware_id', '').strip()
        email = request.POST.get('email', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        if client_name and hardware_id:
            try:
                # Clean HWID to ensure de-duplication works even with formatting variance
                clean_hwid = hardware_id.replace(" ", "").replace("-", "").upper()
                # Re-format it for consistent storage
                formatted_hwid = f"KODY-{clean_hwid[4:8]}-{clean_hwid[8:12]}-{clean_hwid[12:16]}" if clean_hwid.startswith("KODY") else hardware_id
                
                from . import license_core
                # Cryptographically generate hardware-linked code
                gen_key = license_core.generate_expected_license(hardware_id)
                
                # Atomic de-duplication: update existing record for this HWID or create a new one
                # We match on HARDWARE_ID to prevent duplicates
                obj, created = TX_MASTER_GENERATED_LICENSES.objects.update_or_create(
                    HARDWARE_ID=hardware_id,
                    defaults={
                        'CLIENT_NAME': client_name,
                        'EMAIL': email,
                        'NOTES': notes,
                        'GENERATED_KEY': gen_key,
                        # If we are re-provisioning an existing HWID, we might want to keep status 
                        # but usually it stays as is. Or reset to PENDING if name changed.
                    }
                )
                
                success_msg = f"SUCCESS: Generated key {gen_key} for {client_name}"
                return HttpResponseRedirect(f"{reverse('admin_license_dashboard')}?msg_text={success_msg}&msg_class=success")
            except Exception as e:
                error_msg = f"ERROR: Failed to generate license: {str(e)}"
                return HttpResponseRedirect(f"{reverse('admin_license_dashboard')}?msg_text={error_msg}&msg_class=error")
        else:
            error_msg = "ERROR: Missing required details (Client Name or Hardware ID)."
            return HttpResponseRedirect(f"{reverse('admin_license_dashboard')}?msg_text={error_msg}&msg_class=error")
            
    # Fetch all licenses for real-time monitoring
    licenses = TX_MASTER_GENERATED_LICENSES.objects.all().order_by('-CREATED_ON')
    
    logger.info(ulo.end_log(request, fn))
    return render(request, "admin/license_dashboard.html", locals())

@login_required(login_url=login_url)
def delete_license(request, lic_id):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)
    try:
        TX_MASTER_GENERATED_LICENSES.objects.get(id=lic_id).delete()
    except:
        pass
    return HttpResponseRedirect(reverse("admin_license_dashboard"))

@login_required(login_url=login_url)
def toggle_license_status(request, lic_id):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)
    try:
        lic = TX_MASTER_GENERATED_LICENSES.objects.get(id=lic_id)
        # Cycle through clinical states
        if lic.STATUS == "REVOKED":
            lic.STATUS = "PENDING_ACTIVATION"
        elif lic.STATUS == "ACTIVE":
            lic.STATUS = "REVOKED"
        else:
            lic.STATUS = "ACTIVE"
        lic.save()
    except:
        pass
    return HttpResponseRedirect(reverse("admin_license_dashboard"))

@login_required(login_url=login_url)
def download_license_file(request, lic_id):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)
    try:
        lic = TX_MASTER_GENERATED_LICENSES.objects.get(id=lic_id)
        file_content = lic.GENERATED_KEY.strip().upper()
        response = HttpResponse(file_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="kodys_license.dat"'
        return response
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

@csrf_exempt
def clinical_pulse(request):
    """
    The 'PULSE' API: Unified endpoint for activation sync and heartbeat monitoring.
    Clinical workstations ping this on launch and periodically.
    """
    from django.utils import timezone
    hw_id = request.POST.get('hardware_id', '').strip()
    key = request.POST.get('key', '').strip()
    version = request.POST.get('version', 'V2')
    
    if hw_id and key:
        try:
            lic = TX_MASTER_GENERATED_LICENSES.objects.get(
                HARDWARE_ID=hw_id, 
                GENERATED_KEY=key
            )
            
            # 1. Update Heartbeat Metadata
            lic.LAST_HEARTBEAT = timezone.now()
            lic.VERSION_INFO = version
            
            # 2. Auto-Transition to ACTIVE if was pending
            if lic.STATUS == "PENDING_ACTIVATION":
                lic.STATUS = "ACTIVE"
            
            lic.save()
            
            # 3. Security Response: Check if Revoked
            if lic.STATUS == "REVOKED":
                return JsonResponse({"status": "REVOKED", "message": "Access denied by central office."})
                
            return JsonResponse({
                "status": "OK", 
                "message": "Handshake successful.",
                "server_time": timezone.now().isoformat()
            })
        except:
            return JsonResponse({"status": "UNAUTHORIZED", "message": "Invalid hardware link."})
            
    return JsonResponse({"status": "ERROR", "message": "Missing payload."}, status=400)

@csrf_exempt
def report_activation_status(request):
    # This remains for backward compatibility with 3.5, but calls Pulse internally
    return clinical_pulse(request)




@login_required(login_url=login_url)
def signout(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg = api.user_signout(request)
        return HttpResponseRedirect(reverse("signin"))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def home(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        (
            result,
            msg,
            kodys_apps,
            doctors,
            examiners,
            last_test_doctor,
            last_test_examiner,
        ) = api.home(request)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def hospital_profile(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        # result, msg, hospital_profile_details = api.hospital_profile_details(request)
        form_save_msg = ""
        result, msg, state_list = api.states(request)
        if request.method == "POST":
            result, msg = api.hospital_profile(request, request.POST.copy())
            if result:
                form_save_msg = "Success"

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def doctors(request, speciality=0):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        speciality = int(speciality)
        result, msg, hcp_users, specialization = api.doctors(request, speciality)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def patients(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, patients = api.patients(request)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def app_configuration(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, app_config_dict = api.app_configuration(request)
        if request.method == "POST":
            result, msg = api.app_license(request, request.POST.copy())
            if result:
                return HttpResponseRedirect(reverse("app_configuration"))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def reports(request, speciality="All", duration=None):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, reports_list, specialization, start_date, end_date = api.reports(
            request, speciality, duration
        )
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def manuals(request, category="USERMANUAL"):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, manuals_list = api.manuals(request, category)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def thermocool(request, test_code=None):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        pass
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def thermocool_report(request, test_code=None):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        pass
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def hcp_add(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, specialization = api.hcp_specialization(request)
        form = HCPForm()
        if request.method == "POST":
            form = HCPForm(request.POST)
            if form.is_valid():
                result, msg = api.hcp_add(request, request.POST.copy())
                return HttpResponse(json.dumps({"result": result}))
            else:
                return HttpResponse(json.dumps(form.errors))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def hcp_edit(request, hcp_uid):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, hcp_details, specialization = api.hcp_details(request, hcp_uid)
        form = HCPForm()
        if request.method == "POST":
            form = HCPForm(request.POST, hcp_uid=hcp_uid)
            if form.is_valid():
                result, msg = api.hcp_edit(request, request.POST.copy(), hcp_uid)
                return HttpResponse(json.dumps({"result": result}))
            else:
                return HttpResponse(json.dumps(form.errors))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def hcp_delete(request, hcp_uid):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg = api.hcp_delete(request, hcp_uid)
        return HttpResponseRedirect(reverse("doctors"))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def patients_add(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    response_error_msg = ""
    try:
        result, msg, state_list = api.states(request)
        if request.method == "POST":
            p_dict = request.POST.copy()
            result, msg, patients = api.patients_add(request, p_dict)
            if result:
                return HttpResponseRedirect(reverse("patients"))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def patients_edit(request, patients_uid):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    response_error_msg = ""
    try:
        result, msg, patients_details, state_list = api.patients_details(
            request, patients_uid
        )
        if request.method == "POST":
            result, msg, patients = api.patients_add(
                request, request.POST.copy(), patients_uid
            )
            if result:
                return HttpResponseRedirect(reverse("patients"))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def patients_delete(request, patients_uid):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg = api.patients_delete(request, patients_uid)
        return HttpResponseRedirect(reverse("patients"))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def report_view(request, test_entry_code=None, mode=None):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        result, msg, report = api.report_view(request, test_entry_code)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def canyscope_report_view(request, test_entry_code=None):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        result, msg, report = api.report_view(request, test_entry_code)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def canyscope_report_export(request, test_entry_code=None):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        resp = api.canyscope_report_export(request, test_entry_code)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return resp


@login_required(login_url=login_url)
def manuals_view(request, manuals_code=None):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, manuals, MANUAL_PATH = api.manuals_view(request, manuals_code)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def database_backup(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg = api.database_backup(request)

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)


@login_required(login_url=login_url)
def email_report(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    result = False
    msg = ""
    try:
        result, msg = api.email_report(request, request.POST.copy())
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(json.dumps({"result": result, "msg": msg}))


@login_required(login_url=login_url)
def restore_database(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg = api.restore_database(request)

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponseRedirect(reverse("signout"))


@login_required(login_url=login_url)
def app_configuration_mail(request, key_code):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, user = api.app_configuration_mail(
                request, key_code, request.POST.copy()
            )
            return HttpResponseRedirect(reverse("app_configuration"))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def app_configuration_settings(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg = api.app_configuration_settings(request, request.POST.copy())

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result, msg)


@login_required(login_url=login_url)
def patient_search(request, search_key):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg, search_result = api.search(request, search_key)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(json.dumps(search_result))


login_required(login_url=login_url)


def medical_test_entry(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, medical_test_interpertation, right_avg, left_avg = (
                api.medical_test_entry(request, request.POST.copy())
            )

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(medical_test)


login_required(login_url=login_url)


def test_impression(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg = api.test_impression(request, request.POST.copy())

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)


login_required(login_url=login_url)


def test_referred(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg = api.test_referred(request, request.POST.copy())

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)


login_required(login_url=login_url)


def doppler(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-01"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.doppler(request, option)
        medical_test_result = dict()
        if request.method == "POST":
            result, msg, medical_test_result = api.doppler_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def doppler_graphical(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-01"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.doppler_graphical(request, option)
        medical_test_result = dict()

        if request.method == "POST":
            result, msg, medical_test_result = api.doppler_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def vpt_foot(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-02"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.vpt_foot(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )

        if request.method == "POST":
            result, msg, medical_test_result = api.vpt_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                # return HttpResponseRedirect('/%s/%s/%s/%s/%s/%s/'%(option['app_code'], patient_uid, doctor_uid, examiner_uid, medical_test_result['current_test_code'], medical_test_result['test_entry_id']))
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def vpt_hand(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-02"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.vpt_hand(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )
        if request.method == "POST":
            result, msg, medical_test_result = api.vpt_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def vpt_other(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-02"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.vpt_other(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )
        if request.method == "POST":
            result, msg, medical_test_result = api.vpt_other_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def vpt_ultra_foot(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-03"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.vpt_ultra_foot(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )

        if request.method == "POST":
            result, msg, medical_test_result = api.vpt_ultra_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                # return HttpResponseRedirect('/%s/%s/%s/%s/%s/%s/'%(option['app_code'], patient_uid, doctor_uid, examiner_uid, medical_test_result['current_test_code'], medical_test_result['test_entry_id']))
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def vpt_ultra_hand(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-03"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.vpt_ultra_hand(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )
        if request.method == "POST":
            result, msg, medical_test_result = api.vpt_ultra_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def vpt_ultra_other(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-03"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.vpt_ultra_other(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )
        if request.method == "POST":
            result, msg, medical_test_result = api.vpt_ultra_other_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def thermocool_foot(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-04"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.thermocool_foot(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["DEVICE_CONFIG"] = medical_device.DEVICE_CONFIG
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )

        if request.method == "POST":
            result, msg, medical_test_result = api.medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def thermocool_hand(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-04"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.thermocool_hand(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_test_result["DEVICE_CONFIG"] = medical_device.DEVICE_CONFIG
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )
        if request.method == "POST":
            result, msg, medical_test_result = api.medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def thermocool_other(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-04"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.thermocool_other(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_test_result["DEVICE_CONFIG"] = medical_device.DEVICE_CONFIG
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )
        if request.method == "POST":
            result, msg, medical_test_result = api.other_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def generate_report(request, test_uid):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, search_result = api.generate_report(
                request, test_uid, request.POST.copy()
            )
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(search_result)


@login_required(login_url=login_url)
def test_patient_edit(request, patient_uid, app_code, doctor_uid, examiner_uid):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, patients = api.patients_add(
                request, request.POST.copy(), patient_uid
            )
            return HttpResponseRedirect(
                "/%s/%s/%s/%s" % (app_code, patients.UID, doctor_uid, examiner_uid)
            )

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)


@login_required(login_url=login_url)
def test_patient_hand_edit(
    request, patient_uid, app_code, doctor_uid, examiner_uid, test_code
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, patients = api.patients_add(
                request, request.POST.copy(), patient_uid
            )
            return HttpResponseRedirect(
                "/hand/%s/%s/%s/%s/%s"
                % (app_code, patients.UID, doctor_uid, examiner_uid, test_code)
            )

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)


@login_required(login_url=login_url)
def test_patient_other_edit(
    request, patient_uid, app_code, doctor_uid, examiner_uid, test_code
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, patients = api.patients_add(
                request, request.POST.copy(), patient_uid
            )
            return HttpResponseRedirect(
                "/other/%s/%s/%s/%s/%s"
                % (app_code, patients.UID, doctor_uid, examiner_uid, test_code)
            )

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)


@login_required(login_url=login_url)
def device_config_save(request, app_code):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    result = False
    msg = ""
    try:
        if request.method == "POST":
            p_dict = request.POST.copy()
            result, msg = api.device_config_save(request, app_code, p_dict)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(json.dumps({"result": result, "msg": msg}))


@login_required(login_url=login_url)
def generate_license(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg = api.generate_license(request)
            return HttpResponse(result)

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)


@login_required(login_url=login_url)
def patient_email(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg = api.patient_email(request, request.POST.copy())

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(json.dumps({"result": result, "msg": msg}))


@login_required(login_url=login_url)
def patient_id_search(request, search_key):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg = api.search_id(request, search_key)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(json.dumps({"result": result, "msg": msg}))


@login_required(login_url=login_url)
def patient_edit_search(request, patient_uid, search_key):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        result, msg = api.search_edit_id(request, patient_uid, search_key)
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(json.dumps({"result": result, "msg": msg}))


@login_required(login_url=login_url)
def test_patient_graphical_edit(
    request, patient_uid, app_code, doctor_uid, examiner_uid, test_code
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, patients = api.patients_add(
                request, request.POST.copy(), patient_uid
            )
            return HttpResponseRedirect(
                "/graphical/%s/%s/%s/%s/%s"
                % (app_code, patients.UID, doctor_uid, examiner_uid, test_code)
            )

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)


login_required(login_url=login_url)


def podo_i_mat(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-05"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.podo_i_mat(request, option)
        medical_test_result = dict()
        if request.method == "POST":
            result, msg, medical_test_result = api.podo_i_mat_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def podo_t_map(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        option = dict()
        option["app_code"] = "APP-06"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.podo_t_map(request, option)
        medical_test_result = dict()
        if request.method == "POST":
            result, msg, medical_test_result = api.podo_t_map_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def doppler_graphical_template(request):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, test_entry = api.doppler_graphical_template(
                request, request.POST.copy()
            )
            if result:
                return HttpResponseRedirect(reverse("report_view", args=[test_entry]))
    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponseRedirect(reverse("home"))


@login_required(login_url=login_url)
def kodys_can(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    ecg_time_duration = settings.ECG_TESTING_DURATION
    import datetime

    tupleTime = datetime.datetime.strptime(ecg_time_duration, "%H:%M:%S")
    int_ecg_time_duration = (
        datetime.timedelta(
            seconds=tupleTime.second, minutes=tupleTime.minute
        ).total_seconds()
        * 10
    )
    try:
        if test_code == "TM-20":
            template_name = "ecg_deep_breathing"
        elif test_code == "TM-21":
            template_name = "ecg_standing"
        elif test_code == "TM-22":
            template_name = "ecg_valsalva"

        option = dict()
        option["app_code"] = "APP-07"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.kodys_can(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_test_result["DEVICE_CONFIG"] = medical_device.DEVICE_CONFIG
            medical_test_result["DEVICE_MORE_OPTION"] = ast.literal_eval(
                medical_device.DEVICE_MORE_OPTION
            )
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )

        if request.method == "POST":
            result, msg, medical_test_result = api.kodys_can_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def kodys_can_sympathetic(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    try:
        if test_code == "TM-24":
            template_name = "sustained_handgrip"

        option = dict()
        option["app_code"] = "APP-07"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.kodys_can_sympathetic(
            request, option
        )
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_test_result["DEVICE_CONFIG"] = medical_device.DEVICE_CONFIG
            medical_test_result["DEVICE_MORE_OPTION"] = ast.literal_eval(
                medical_device.DEVICE_MORE_OPTION
            )
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )

        if request.method == "POST":
            result, msg, medical_test_result = (
                api.kodys_can_sympathetic_medical_test_entry(
                    request, request.POST.copy()
                )
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


login_required(login_url=login_url)


def kodys_can_hrv(
    request,
    patient_uid,
    doctor_uid=None,
    examiner_uid=None,
    test_code=None,
    test_entry=None,
    previous_test_code=None,
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    app = settings.RUNNING_IN_APP
    ecg_time_duration = settings.ECG_HRV_TESTING_DURATION
    import datetime

    tupleTime = datetime.datetime.strptime(ecg_time_duration, "%H:%M:%S")
    int_ecg_time_duration = (
        datetime.timedelta(
            seconds=tupleTime.second, minutes=tupleTime.minute
        ).total_seconds()
        * 10
    )
    try:
        option = dict()
        option["app_code"] = "APP-07"
        option["patient_uid"] = patient_uid
        option["doctor_uid"] = doctor_uid
        option["examiner_uid"] = examiner_uid
        option["test_code"] = test_code
        option["test_entry"] = test_entry
        option["previous_test_code"] = previous_test_code
        result, msg, medical_test, state_list = api.kodys_can_hrv(request, option)
        medical_test_result = dict()
        medical_device = MA_MEDICALAPPDEVICES.objects.filter(
            MEDICAL_APP__CODE=option["app_code"], DATAMODE="A"
        )
        if medical_device:
            medical_device = medical_device.first()
            medical_test_result["DEVICE_KEY"] = medical_device.DEVICE_KEY
            medical_test_result["VENDOR_ID"] = medical_device.VENDOR_ID
            medical_test_result["PRODUCT_ID"] = medical_device.PRODUCT_ID
            medical_test_result["DEVICE_CONFIG"] = medical_device.DEVICE_CONFIG
            medical_test_result["DEVICE_MORE_OPTION"] = ast.literal_eval(
                medical_device.DEVICE_MORE_OPTION
            )
            medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(
                MEDICAL_DEVICE__id=medical_device.id, DATAMODE="A"
            )
            if medical_device_status:
                medical_device_status = medical_device_status.first()
                medical_test_result["CONNECTION_TYPE"] = (
                    medical_device_status.CONNECTION_TYPE
                )

        if request.method == "POST":
            result, msg, medical_test_result = api.kodys_can_medical_test_entry(
                request, request.POST.copy()
            )
            if result:
                return HttpResponse(json.dumps(medical_test_result))

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return render(request, ulo.get_template_name(request, template_name), locals())


@login_required(login_url=login_url)
def test_patient_hrv_edit(
    request, patient_uid, app_code, doctor_uid, examiner_uid, test_code
):
    fn = ulo._fn()
    template_name = fn
    result = False
    msg = ""
    logger.info(ulo.start_log(request, fn))
    try:
        if request.method == "POST":
            result, msg, patients = api.patients_add(
                request, request.POST.copy(), patient_uid
            )
            return HttpResponseRedirect(
                "/hrv/%s/%s/%s/%s/%s"
                % (app_code, patients.UID, doctor_uid, examiner_uid, test_code)
            )

    except Exception as e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    logger.info(ulo.end_log(request, fn))
    return HttpResponse(result)
