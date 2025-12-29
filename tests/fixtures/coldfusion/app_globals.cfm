<!--- Used to reset application, session, and client variables for testing purposes.  You must remove the comments surrounding the next set of code variables to clear all variable scopes, and then replace the comments so the application will run normally. --->
<!---
<cfset StructClear(application)>
<cfset StructClear(session)>
<cfset StructClear(attributes)>
<cfloop index="x" list="#GetClientVariablesList()#">
	<cfset deleted = DeleteClientVariable("#x#")>
</cfloop>
<cfcookie name="cfid" expires="NOW">
<cfcookie name="cftoken" expires="NOW">
<cfcookie name="cfglobals" expires="NOW">
<cfabort>
--->

<!--- COMTST Environment variables --->
<cfset request.ds = "ptclprd"/>
<cfset request.environment = "PRD"/>
<cfset request.directory = "/var/www/html/WageWorks/AdjustmentManager/">
<cfset request.libdir = "/wwprd_adjustment_mgr_lib"/>
<cfset request.common_cfc_library = "/wwprd_common_cfc_library"/>
<cfset request.local_webservices = "https://csd.wageworks.com/WebServices"/>
<cfset request.reports_path = "/var/www/html/WageWorks/Files/reports/">
<cfset request.rpt_download_url = "https://csd.wageworks.com/Files/reports/">
<cfset request.file_path = "/var/www/html/WageWorks/Files/AdjustmentManager/">
<cfset request.email_server = "mail.us.mi-services.com">
<cfset request.service_site_directory = "https://csd.wageworks.com/Service/">
<cfset request.employee_site_directory = "https://employeetest.wageworks.com/WWSSO.aspx">
<cfset request.cfr_reports_directory = "/var/www/html/WageWorks/Reports/"/>

<!--- Common Parameters do not comment out --->
<cfset request.session_timeout = "480"/>
<cfset request.app_short_name = "WW_ADJUSTMENT_MGR"/>
<cfset request.app_title = "Adjustment Manager"/>
<cfset request.version_num = "2.0"/>

<cfset request.mailBuildDirectory = "/var/www/html/WageWorks/Files/cannon/">
<cfset request.dropOffDirectory = " /var/www/html/WageWorks/Files/MailDropOff">
<cfset request.email_user = "maildropoff">
<cfset request.email_password = "ups1day">


<!--- Empty strings for content objects --->
<cfparam name="header" default=""/>
<cfparam name="javascript" default=""/>
<cfparam name="menu" default=""/>
<cfparam name="error" default=""/>
<cfparam name="breadcrumb" default=""/>
<cfparam name="body" default=""/>
<cfparam name="body2" default=""/>
<cfparam name="body3" default=""/>
<cfparam name="footer" default=""/>
<!---
<cfinclude template="lib/function_lib.cfm"/>--->

<cfparam name="self" default="index.cfm"/>
