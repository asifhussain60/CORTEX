<cfcomponent>
	<cffunction name="info_message_search_results" access="public" returntype="struct" output="no">
		<cfargument name="search_message_code" type="string" required="no" default=""/>
		<cfargument name="search_start_range" type="string" required="no" default=""/>
		<cfargument name="search_end_range" type="string" required="no" default=""/>
		<cfargument name="search_message_text" type="string" required="no" default=""/>
		<cfargument name="search_oracle_error_number" type="string" required="no" default=""/>
		<cfargument name="search_oracle_error_text" type="string" required="no" default=""/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="info_message.info_message_search_results" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_message_code" null="#iif(isNumeric(arguments.search_message_code),de('no'),de('yes'))#" value="#arguments.search_message_code#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_search_start_range" null="#iif(isNumeric(arguments.search_start_range),de('no'),de('yes'))#" value="#arguments.search_start_range#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_search_end_range" null="#iif(isNumeric(arguments.search_end_range),de('no'),de('yes'))#" value="#arguments.search_end_range#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_search_message_text" null="#iif(len(trim(arguments.search_message_text)) gt 0,de('no'),de('yes'))#" value="#arguments.search_message_text#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_oracle_error_number" null="#iif(isNumeric(arguments.search_oracle_error_number),de('no'),de('yes'))#" value="#arguments.search_oracle_error_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_search_oracle_error_text" null="#iif(len(trim(arguments.search_oracle_error_text)) gt 0,de('no'),de('yes'))#" value="#arguments.search_oracle_error_text#"/>
			<cfprocresult name="result.cur_info_messages"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="info_message_details" access="public" returntype="query" output="no">
		<cfargument name="message_code" type="string" required="yes"/>
		<cfset var cur_info_message_dtls = ""/>
		<cfstoredproc procedure="info_message.info_message_details" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_message_code" null="no" value="#arguments.message_code#"/>
			<cfprocresult name="cur_info_message_dtls"/>
		</cfstoredproc>
		<cfreturn cur_info_message_dtls/>
	</cffunction>

	<cffunction name="add_info_message" access="public" returntype="numeric" output="no">
		<cfargument name="message_code" type="numeric" required="yes"/>
		<cfargument name="message_text" type="string" required="yes"/>
		<cfargument name="oracle_error_number" type="string" required="no"/>
		<cfargument name="oracle_error_text" type="string" required="no"/>
		<cfargument name="create_user" type="string" required="yes"/>

		<cfstoredproc procedure="info_message_api.add_info_message" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_message_code" null="no" value="#arguments.message_code#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_message_text" null="no" value="#arguments.message_text#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_oracle_error_number" null="#iif(isNumeric(arguments.oracle_error_number),de('no'),de('yes'))#" value="#arguments.oracle_error_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_oracle_error_text" null="#iif(len(trim(arguments.oracle_error_text)) gt 0,de('no'),de('yes'))#" value="#arguments.oracle_error_text#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.create_user#"/>
		</cfstoredproc>
		<cfreturn 1/>
	</cffunction>

	<cffunction name="delete_info_message" access="public" returntype="numeric" output="no">
		<cfargument name="message_code" type="string" required="yes"/>
		<cfstoredproc procedure="info_message_api.delete_info_message" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_message_code" null="no" value="#arguments.message_code#"/>
		</cfstoredproc>
		<cfreturn 1/>
	</cffunction>

	<cffunction name="update_info_message" access="public" returntype="numeric" output="no">
		<cfargument name="message_code" type="string" required="yes"/>
		<cfargument name="message_text" type="string" required="yes"/>
		<cfargument name="oracle_error_number" type="string" required="no"/>
		<cfargument name="oracle_error_text" type="string" required="no"/>
		<cfargument name="last_update_user" type="string" required="yes"/>

		<cfstoredproc procedure="info_message_api.update_info_message" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_message_code" null="no" value="#arguments.message_code#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_message_text" null="no" value="#arguments.message_text#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_oracle_error_number" null="#iif(isNumeric(arguments.oracle_error_number),de('no'),de('yes'))#" value="#arguments.oracle_error_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_oracle_error_text" null="#iif(len(trim(arguments.oracle_error_text)) gt 0,de('no'),de('yes'))#" value="#arguments.oracle_error_text#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.last_update_user#"/>
		</cfstoredproc>
		<cfreturn 1/>
	</cffunction>

	<cffunction name="find_app_error_msg" access="public" returntype="string" output="no">
		<cfargument name="message_code" type="numeric" required="yes"/>
		<cfset var message_text = ""/>
		<cfstoredproc procedure="wweb.info_message.find_app_error_msg" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_message_code" value="#arguments.message_code#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_message_text" variable="message_text" null="no">
		</cfstoredproc>
		<cfreturn message_text/>
	</cffunction>
</cfcomponent>
