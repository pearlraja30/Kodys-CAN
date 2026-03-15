"""app_config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path, include

# Maintain compatibility with legacy url() uses in this project.
url = re_path
from django.contrib import admin
import django.views.static as django_static_view
from django.conf import settings
from kodys.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^site_media/(?P<path>.*)$",
        django_static_view.serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
    re_path(
        r"^site_data/(?P<path>.*)$",
        django_static_view.serve,
        {"document_root": settings.MEDIA_DATA},
    ),
    re_path(
        r"^static/admin/(?P<path>.*)$",
        django_static_view.serve,
        {"document_root": settings.STATIC_ROOT},
    ),
    path("admin/license/", admin_license_dashboard, name="admin_license_dashboard"),
    path("license/", license_activation, name="license_activation"),
    path("about/", about, name="about"),
    path("signin/", signin, name="signin"),
    path("signout/", signout, name="signout"),
    path("", home, name="home"),
    path("customer/support/", customer_support, name="customer_support"),
    path("hospital/profile/", hospital_profile, name="hospital_profile"),
    path("doctors/", doctors, name="doctors"),
    path("doctors/<str:speciality>/", doctors, name="doctors"),
    path("hcp/add/", hcp_add, name="hcp_add"),
    path("hcp/edit/<str:hcp_uid>/", hcp_edit, name="hcp_edit"),
    path("hcp/delete/<str:hcp_uid>/", hcp_delete, name="hcp_delete"),
    path("patients/", patients, name="patients"),
    path("patient/add/", patients_add, name="patients_add"),
    path("patient/edit/<str:patients_uid>/", patients_edit, name="patients_edit"),
    path("patient/delete/<str:patients_uid>/", patients_delete, name="patients_delete"),
    path("app/configuration/", app_configuration, name="app_configuration"),
    path("reports/", reports, name="reports"),
    path("reports/<str:speciality>/<str:duration>/", reports, name="reports"),
    path("manuals/", manuals, name="manuals"),
    path("manuals/<str:category>/", manuals, name="manuals"),
    path(
        "report/view/canyscope/<str:test_entry_code>/",
        canyscope_report_view,
        name="canyscope_report_view",
    ),
    path(
        "report/export/canyscope/<str:test_entry_code>/",
        canyscope_report_export,
        name="canyscope_report_export",
    ),
    path("report/view/<str:test_entry_code>/", report_view, name="report_view"),
    path(
        "report/view/<str:test_entry_code>/<str:mode>/", report_view, name="report_view"
    ),
    re_path(
        r"^manuals/view/(?P<manuals_code>[-\w]+)/$", manuals_view, name="manuals_view"
    ),
    re_path(r"^database/backup/$", database_backup, name="database_backup"),
    re_path(r"^restore/database/$", restore_database, name="restore_database"),
    re_path(
        r"^app/configuration/mail/(?P<key_code>[-\w]+)/$",
        app_configuration_mail,
        name="app_configuration_mail",
    ),
    re_path(
        r"^app/configuration/settings/$",
        app_configuration_settings,
        name="app_configuration_settings",
    ),
    re_path(
        r"^patient/search/(?P<search_key>[-\w]+)/$",
        patient_search,
        name="patient_search",
    ),
    re_path(
        r"^patient/edit/search/(?P<patient_uid>[-\w]+)/(?P<search_key>[-\w]+)/$",
        patient_edit_search,
        name="patient_edit_search",
    ),
    # re_path(r'^medical/test/entry/$', medical_test_entry, name="medical_test_entry"),
    # re_path(r'^medical/test/details/(?P<app_code>[-\w]+)/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', medical_test_details, name="medical_test_details"),
    # re_path(r'^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/$', thermocool_foot, name="thermocool_foot"),
    re_path(
        r"^APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$",
        doppler,
        name="doppler",
    ),
    re_path(
        r"^APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        doppler,
        name="doppler",
    ),
    re_path(
        r"^APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        doppler,
        name="doppler",
    ),
    re_path(
        r"^graphical/APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        doppler_graphical,
        name="doppler_graphical",
    ),
    re_path(
        r"^graphical/APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        doppler_graphical,
        name="doppler_graphical",
    ),
    re_path(
        r"^graphical/template/upload/$",
        doppler_graphical_template,
        name="doppler_graphical_template",
    ),
    re_path(
        r"^APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$",
        vpt_foot,
        name="vpt_foot",
    ),
    re_path(
        r"^APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        vpt_foot,
        name="vpt_foot",
    ),
    re_path(
        r"^APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        vpt_foot,
        name="vpt_foot",
    ),
    re_path(
        r"^hand/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        vpt_hand,
        name="vpt_hand",
    ),
    re_path(
        r"^hand/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        vpt_hand,
        name="vpt_hand",
    ),
    re_path(
        r"^hand/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        vpt_hand,
        name="vpt_hand",
    ),
    re_path(
        r"^APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$",
        vpt_ultra_foot,
        name="vpt_ultra_foot",
    ),
    re_path(
        r"^APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        vpt_ultra_foot,
        name="vpt_ultra_foot",
    ),
    re_path(
        r"^APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        vpt_ultra_foot,
        name="vpt_ultra_foot",
    ),
    re_path(
        r"^hand/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        vpt_ultra_hand,
        name="vpt_ultra_hand",
    ),
    re_path(
        r"^hand/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        vpt_ultra_hand,
        name="vpt_ultra_hand",
    ),
    re_path(
        r"^hand/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        vpt_ultra_hand,
        name="vpt_ultra_hand",
    ),
    re_path(
        r"^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$",
        thermocool_foot,
        name="thermocool_foot",
    ),
    re_path(
        r"^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        thermocool_foot,
        name="thermocool_foot",
    ),
    re_path(
        r"^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        thermocool_foot,
        name="thermocool_foot",
    ),
    re_path(
        r"^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        thermocool_foot,
        name="thermocool_foot",
    ),
    re_path(
        r"^hand/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        thermocool_hand,
        name="thermocool_hand",
    ),
    re_path(
        r"^hand/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        thermocool_hand,
        name="thermocool_hand",
    ),
    re_path(
        r"^hand/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        thermocool_hand,
        name="thermocool_hand",
    ),
    re_path(
        r"^generate/report/(?P<test_uid>[-\w]+)/$",
        generate_report,
        name="generate_report",
    ),
    re_path(
        r"^test/patient/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$",
        test_patient_edit,
        name="test_patient_edit",
    ),
    re_path(
        r"^test/patient/hand/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        test_patient_hand_edit,
        name="test_patient_hand_edit",
    ),
    re_path(
        r"^test/patient/other/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        test_patient_other_edit,
        name="test_patient_other_edit",
    ),
    re_path(r"^test/impression/$", test_impression, name="test_impression"),
    re_path(
        r"^device-config-save/(?P<app_code>[-\w]+)/$",
        device_config_save,
        name="device_config_save",
    ),
    re_path(r"^test/referred/$", test_referred, name="test_referred"),
    re_path(r"^email/report/$", email_report, name="email_report"),
    # re_path(r'^other/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', thermocool_other, name="thermocool_hand"),
    re_path(
        r"^other/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        thermocool_other,
        name="thermocool_hand",
    ),
    re_path(
        r"^other/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        thermocool_other,
        name="thermocool_other",
    ),
    re_path(
        r"^other/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        thermocool_other,
        name="thermocool_other",
    ),
    re_path(
        r"^other/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        vpt_ultra_other,
        name="vpt_ultra_other",
    ),
    re_path(
        r"^other/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        vpt_ultra_other,
        name="vpt_ultra_other",
    ),
    re_path(
        r"^other/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        vpt_ultra_other,
        name="vpt_ultra_other",
    ),
    url(
        r"^other/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        vpt_other,
        name="vpt_other",
    ),
    url(
        r"^other/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        vpt_other,
        name="vpt_other",
    ),
    url(
        r"^other/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        vpt_other,
        name="vpt_other",
    ),
    url(r"^generate/license/$", generate_license, name="generate_license"),
    url(r"^patient/email/$", patient_email, name="patient_email"),
    url(
        r"^patient/id/search/(?P<search_key>[-\w]+)/$",
        patient_id_search,
        name="patient_id_search",
    ),
    url(
        r"^test/patient/graphical/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        test_patient_graphical_edit,
        name="test_patient_graphical_edit",
    ),
    url(
        r"^APP-05/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$",
        podo_i_mat,
        name="podo_i_mat",
    ),
    url(
        r"^APP-05/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        podo_i_mat,
        name="podo_i_mat",
    ),
    url(
        r"^APP-05/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        podo_i_mat,
        name="podo_i_mat",
    ),
    # url(r'^APP-05/foot/convert/$', podo_i_mat_foot_convert, name="podo_i_mat_foot_convert"),
    url(
        r"^APP-06/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$",
        podo_t_map,
        name="podo_t_map",
    ),
    url(
        r"^APP-06/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        podo_t_map,
        name="podo_t_map",
    ),
    url(
        r"^APP-06/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        podo_t_map,
        name="podo_t_map",
    ),
    url(
        r"^APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$",
        kodys_can,
        name="kodys_can",
    ),
    url(
        r"^APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        kodys_can,
        name="kodys_can",
    ),
    url(
        r"^APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        kodys_can,
        name="kodys_can",
    ),
    url(
        r"^sympathetic/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        kodys_can_sympathetic,
        name="kodys_can_sympathetic",
    ),
    url(
        r"^sympathetic/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        kodys_can_sympathetic,
        name="kodys_can_sympathetic",
    ),
    url(
        r"^sympathetic/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        kodys_can_sympathetic,
        name="kodys_can_sympathetic",
    ),
    url(
        r"^hrv/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        kodys_can_hrv,
        name="kodys_can_hrv",
    ),
    url(
        r"^hrv/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$",
        kodys_can_hrv,
        name="kodys_can_hrv",
    ),
    url(
        r"^hrv/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$",
        kodys_can_hrv,
        name="kodys_can_hrv",
    ),
    url(
        r"^test/patient/hrv/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$",
        test_patient_hrv_edit,
        name="test_patient_hrv_edit",
    ),
]
