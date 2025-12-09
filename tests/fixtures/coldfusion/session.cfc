<cfcomponent>
	<cffunction name="check_session" returntype="boolean" output="no" access="public">
		<cfargument name="strtoken" type="string" required="yes"/>
		<cfargument name="timeout" type="numeric" required="yes"/>

		<cfstoredproc procedure="wweb.security_info.check_session" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_token" null="no" value="#arguments.strtoken#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_idle_time" null="no" value="#arguments.timeout#"/>
			<cfprocresult name="cur_session_data"/>
		</cfstoredproc>

		<cfif cur_session_data.RecordCount GT 0>
			<cfreturn true>
		<cfelse>
			<cfreturn false>
		</cfif>
	</cffunction>

	<cffunction name="get_session" returntype="struct" output="no" access="public">
		<cfargument name="strtoken" type="string" required="yes"/>
		<cfset var cur_session_data = ""/>
		<cfset var session_packet = structNew()/>

		<cfstoredproc procedure="wweb.security_info.get_session" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_token" null="no" value="#arguments.strtoken#"/>
			<cfprocresult name="cur_session_data"/>
		</cfstoredproc>

		<cfif isWDDX(cur_session_data.session_values)>
			<cfwddx action="WDDX2CFML" input="#cur_session_data.session_values#" output="session_packet"/>
		</cfif>

		<cfreturn session_packet/>
	</cffunction>

	<cffunction name="create_session" returntype="any" output="no" access="public">
		<cfargument name="strtoken" type="string" required="yes"/>
		<cfargument name="fuseaction" type="string" required="yes"/>
		<cfargument name="app_short_name" type="string" required="yes"/>
		<cfstoredproc procedure="wweb.security_api.create_session" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_token" null="no" value="#arguments.strtoken#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_fuseaction" null="no" value="#arguments.fuseaction#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_appl_short_name" null="no" value="#arguments.app_short_name#"/>
		</cfstoredproc>
	</cffunction>

	<cffunction name="refresh_session" returntype="any" output="no" access="public">
		<cfargument name="strtoken" type="string" required="yes">
		<cfstoredproc procedure="wweb.security_api.refresh_session" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_token" null="no" value="#arguments.strtoken#"/>
		</cfstoredproc>
	</cffunction>

	<cffunction name="update_session" output="no" access="public">
		<cfargument name="strtoken" type="string" required="yes"/>
		<cfargument name="fuseaction" type="string" required="yes" default=""/>
		<cfargument name="session_vars" type="any" required="yes"/>

		<cfwddx action="CFML2WDDX" input="#session_vars#" output="packet"/>

		<cfstoredproc procedure="wweb.security_api.update_session" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_token" null="no" value="#arguments.strtoken#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_fuseaction" null="#iif(len(trim(arguments.fuseaction)) gt 0,de('no'),de('yes'))#" value="#arguments.fuseaction#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_clob" dbvarname=":p_session_vars" null="no" value="#packet#"/>
		</cfstoredproc>
	</cffunction>

	<cffunction name="get_users_assigned_resources" returntype="query" output="no" access="public">
		<cfargument name="app_short_name" type="string" required="yes">
		<cfargument name="txtLogin" type="string" required="yes">
		<cfset var tmp_security = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_info.get_users_assigned_resources" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_short_name" value="#arguments.app_short_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_logon_name" value="#arguments.txtLogin#" null="no">
			<cfprocresult name="tmp_security">
		</cfstoredproc>
		<cfreturn tmp_security/>
	</cffunction>

	<cffunction name="needto_change_password" returntype="numeric" output="no" access="public">
		<cfargument name="txtLogin" type="string" required="yes">
		<cfset var password_reset = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_info.needto_change_password" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_logon_name" value="#arguments.txtLogin#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_reset" variable="password_reset" null="no">
		</cfstoredproc>
		<cfreturn password_reset/>
	</cffunction>
</cfcomponent>