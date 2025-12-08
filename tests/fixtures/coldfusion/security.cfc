<cfcomponent>
	<cffunction name="login" returntype="query" output="no" access="public">
		<cfargument name="logon_name" type="string" required="yes"/>
		<cfargument name="password" type="string" required="yes"/>
		<cfargument name="appl_id" type="numeric" required="yes"/>
		<cfset var cur_user_info = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_api.login" returncode="no">
			<cfprocresult name="cur_user_info">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_logon_name" value="#arguments.logon_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_password" value="#arguments.password#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_appl_id" value="#arguments.appl_id#" null="no">
		</cfstoredproc>
		<cfreturn cur_user_info/>
	</cffunction>

	<cffunction name="logout" returntype="struct" access="public" output="no">
		<cfargument name="strtoken" type="string" required="yes"/>
		<cfset var result = StructNew()/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_api.logout" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_token" value="#arguments.strtoken#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="get_group_info" returntype="query" output="no" access="public">
		<cfset var cur_group_info = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_info.get_group_info" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_appl_group_id" value="#arguments.group_id#" null="no">
			<cfprocresult name="cur_group_info">
		</cfstoredproc>
		<cfreturn cur_group_info/>
	</cffunction>

	<cffunction name="get_all_users" returntype="query" output="no" access="public">
		<cfset var cur_all_users = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_info.get_all_users" returncode="no">
			<cfprocresult name="cur_all_users"/>
		</cfstoredproc>
		<cfreturn cur_all_users/>
	</cffunction>

	<cffunction name="get_group_users" returntype="query" output="no" access="public">
		<cfargument name="group_id" type="numeric" required="yes"/>
		<cfset var cur_group_users = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_info.get_group_users" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_group_id" value="#arguments.group_id#" null="no"/>
			<cfprocresult name="cur_group_users"/>
		</cfstoredproc>
		<cfreturn cur_group_users/>
	</cffunction>

	<cffunction name="get_application_users" returntype="query" output="no" access="public">
		<cfargument name="app_short_name" type="string" required="yes"/>
		<cfset var cur_users = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_info.get_application_users" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_short_name" value="#arguments.app_short_name#" null="no"/>
			<cfprocresult name="cur_users"/>
		</cfstoredproc>
		<cfreturn cur_users/>
	</cffunction>
	
	<cffunction name="get_application_groups" returntype="query" output="no" access="public">
		<cfargument name="app_short_name" type="string" required="yes"/>
		<cfset var cur_application_groups = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_info.get_application_groups" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_short_name" value="#arguments.app_short_name#" null="no"/>
			<cfprocresult name="cur_application_groups"/>
		</cfstoredproc>
		<cfreturn cur_application_groups/>
	</cffunction>

	<cffunction name="change_password" returntype="numeric" output="no" access="public">
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="old_pwd" type="string" required="yes"/>
		<cfargument name="new_pwd" type="string" required="yes"/>
		<cfset var success_flag = ""/>
		<cfset var process_message = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_api.change_password" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_logon_name" value="#UCase(arguments.username)#" null="no"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_old_password" value="#arguments.old_pwd#" null="no"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_new_password" value="#arguments.new_pwd#" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="process_message" null="no"/>
		</cfstoredproc>
		<cfreturn success_flag/>
	</cffunction>

	<cffunction name="add_group_member" returntype="numeric" output="no" access="public">
		<cfargument name="group_id" type="numeric" required="yes"/>
		<cfargument name="appl_user_id" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var success_flag = ""/>
		<cfset var process_message = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_api.add_group_member_by_id" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_appl_group_id" value="#arguments.group_id#" null="no"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_appl_user_id" value="#arguments.appl_user_id#" null="no"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_user" value="#arguments.username#" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="process_message" null="no"/>
		</cfstoredproc>
		<cfreturn success_flag/>
	</cffunction>

	<cffunction name="remove_group_member" returntype="numeric" output="no" access="public">
		<cfargument name="group_id" type="numeric" required="yes"/>
		<cfargument name="appl_user_id" type="numeric" required="yes"/>
		<cfset var success_flag = ""/>
		<cfset var process_message = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_api.delete_group_member" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_appl_group_id" value="#arguments.group_id#" null="no"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_appl_user_id" value="#arguments.appl_user_id#" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="process_message" null="no"/>
		</cfstoredproc>
		<cfreturn success_flag/>
	</cffunction>

	<cffunction name="reset_appl_user" returntype="numeric" access="public" output="no">
		<cfargument name="logon_name" type="string" required="yes"/>
		<cfset var success_flag = ""/>
		<cfset var process_message = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_api.reset_password" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_logon_name" value="#arguments.logon_name#" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="process_message" null="no"/>
		</cfstoredproc>
		<cfreturn success_flag/>
	</cffunction>

	<cffunction name="unlock_appl_user" returntype="numeric" access="public" output="no">
		<cfargument name="logon_name" type="string" required="yes"/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.security_api.unlock_appl_user" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_logon_name" value="#arguments.logon_name#" null="no"/> null="no"/>
		</cfstoredproc>
		<cfreturn 1/>
	</cffunction>
</cfcomponent>