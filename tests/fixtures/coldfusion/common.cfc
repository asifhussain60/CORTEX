<cfcomponent>
	<cffunction name="getUSStateList" returntype="query" access="public" output="no">
		<cfset var states_lov = ""/>
		<cfstoredproc procedure="passport_utils.get_us_states_list" datasource="#request.ds#">
			<cfprocresult name="states_lov"/>
		</cfstoredproc>
		<cfreturn states_lov/>
	</cffunction>
	
	<cffunction name="isValidEmail" returntype="boolean" access="public" output="no">
		<cfargument name="email" type="string" required="yes"/>
		<cfscript>
		if (REFindNoCase("^['_a-z0-9-]+(\.['_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*\.(([a-z]{2,3})|(aero|coop|info|museum|name))$",arguments.email)) {
			return true;
			} else {
			return false;
		}
		</cfscript>
	</cffunction>
	
	<cffunction name="getCustomOracleErrorMessage" returntype="string" output="no" access="public">
		<cfargument name="message_code" type="string" required="yes">
		<cfset var err_text = ""/>
		<cfstoredproc procedure="wweb.passport_utils.error_message_text" datasource="#request.ds#">
			<cfprocparam cfsqltype="cf_sql_numeric" null="no" value="#arguments.message_code#" type="in"/>
			<cfprocparam cfsqltype="cf_sql_varchar" type="out" variable="err_text">
		</cfstoredproc>
		<cfreturn err_text/>
	</cffunction>

	<cffunction name="get_date_range" returntype="struct" access="public" output="no">
		<cfargument name="mask" type="string" required="no" default=""/>
		<cfargument name="start_month_delta" type="numeric" required="no" default=""/>
		<cfargument name="end_month_delta" type="numeric" required="no" default=""/>
		<cfargument name="sort_order" type="string" required="no" default=""/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="wweb.pkg_ops_common.get_date_range" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_mask" value="#arguments.mask#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_start_month_delta" value="#arguments.start_month_delta#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_end_month_delta" value="#arguments.end_month_delta#" null="no">	
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_sort_order" value="#arguments.sort_order#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_start_date" variable="result.startdate" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_end_date" variable="result.enddate" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_start_date_last_day_month" variable="result.start_date_last_day_month" null="no">
			<cfprocresult name="result.cur_date_range">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="contact_types" returntype="query" access="public" output="no">
		<cfset var cur_contact_types_lov = ""/>
		<cfstoredproc procedure="pkg_ops_common.get_contact_type_list" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_excluded_contact_type" null="yes">
			<cfprocresult name="cur_contact_types_lov"/>
		</cfstoredproc>
		<cfreturn cur_contact_types_lov/>
	</cffunction>

	<cffunction name="get_lookup_id" returntype="numeric" access="public" output="no">
		<cfargument name="lookup_name" type="string" required="yes"/>
		<cfargument name="option_name" type="string" required="yes"/>
		<cfset var lookup_options_id = ""/>
		<cfstoredproc procedure="wweb.pkg_ops_common.get_lookup_id" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_lookup_name" value="#arguments.lookup_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_option_name" value="#arguments.option_name#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_lookup_options_id" variable="lookup_options_id" null="no">
		</cfstoredproc>
		<cfreturn lookup_options_id/>
	</cffunction>

	<cffunction name="get_lookup_info" returntype="query" access="public" output="no">
		<cfargument name="lookup_name" type="string" required="yes"/>
		<cfset var cur_lookup_info = ""/>
		<cfstoredproc procedure="wweb.pkg_ops_common.get_lookup_info" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_lookup_name" value="#arguments.lookup_name#" null="no">
			<cfprocresult name="cur_lookup_info">
		</cfstoredproc>
		<cfreturn cur_lookup_info/>
	</cffunction>

	<cffunction name="get_lookup_info_by_category" returntype="query" access="public" output="no">
		<cfargument name="lookup_name" type="string" required="yes"/>
		<cfargument name="option_description" type="string" required="yes"/>
		<cfargument name="category_lookup_name" type="string" required="yes"/>
		<cfargument name="category_option_name" type="string" required="yes"/>
		<cfargument name="query_name" type="string" required="yes"/>
		<cfset var cur_category_lookup_info = ""/>
		<cfstoredproc procedure="wweb.pkg_ops_common.get_lookup_info_by_category" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_lookup_name" value="#arguments.lookup_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_option_description" value="#arguments.option_description#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_category_lookup_name" value="#arguments.category_lookup_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_category_option_namee" value="#arguments.category_option_name#" null="no">
			<cfprocresult name="cur_category_lookup_info">
		</cfstoredproc>
		<cfreturn cur_category_lookup_info/>
	</cffunction>

	<cffunction name="get_lookup_info_by_id" returntype="query" access="public" output="no">
		<cfargument name="lookup_options_id" type="numeric" required="yes"/>
		<cfset var cur_lookup_info_by_id = ""/>
		<cfstoredproc procedure="wweb.pkg_ops_common.get_lookup_info_by_id" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_lookup_options_id" value="#arguments.lookup_options_id#" null="no">
			<cfprocresult name="cur_lookup_info_by_id">
		</cfstoredproc>
		<cfreturn cur_lookup_info_by_id/>
	</cffunction>

	<cffunction name="employer_search_results" access="public" returntype="struct" output="no">
		<cfargument name="search_employer_id" type="string" required="no" default=""/>
		<cfargument name="search_employer_name" type="string" required="no" default=""/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="pkg_payroll_manager.get_employer_search_results" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" null="#iif(isNumeric(arguments.search_employer_id),de('no'),de('yes'))#" value="#arguments.search_employer_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_str_employer_name" null="#iif(len(trim(arguments.search_employer_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_employer_name#"/>
			<cfprocresult name="result.cur_employer_search_results"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="employee_search_results" access="public" returntype="struct" output="no">
		<cfargument name="search_employee_id" type="string" required="no" default=""/>
		<cfargument name="search_employer_id" type="string" required="no" default=""/>
		<cfargument name="search_last_name" type="string" required="no" default=""/>
		<cfargument name="search_first_name" type="string" required="no" default=""/>
		<cfargument name="search_ssn" type="string" required="no" default=""/>
		<cfargument name="search_employer_name" type="string" required="no" default=""/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="employee_info.get_employee_search_results" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_id" null="#iif(isNumeric(arguments.search_employee_id),de('no'),de('yes'))#" value="#arguments.search_employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" null="#iif(isNumeric(arguments.search_employer_id),de('no'),de('yes'))#" value="#arguments.search_employer_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_lastname" null="#iif(len(trim(arguments.search_last_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_last_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_firstname" null="#iif(len(trim(arguments.search_first_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_first_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_ssn" null="#iif(len(trim(arguments.search_ssn)) gt 0,de('no'),de('yes'))#" value="#arguments.search_ssn#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_employer_name" null="#iif(len(trim(arguments.search_employer_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_employer_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_selected_service_type" null="yes">

			<cfprocresult name="result.cur_employee_search_results">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="lookup_option_search_results" access="public" returntype="struct" output="no">
		<cfargument name="search_lookup_name" type="string" required="no" default=""/>
		<cfargument name="search_option_name" type="string" required="no" default=""/>
		<cfargument name="search_option_description" type="string" required="no" default=""/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="pkg_ops_common.lookup_option_search_results" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_lookup_name" null="#iif(len(trim(arguments.search_lookup_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_lookup_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_option_name" null="#iif(len(trim(arguments.search_option_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_option_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_option_description" null="#iif(len(trim(arguments.search_option_description)) gt 0,de('no'),de('yes'))#" value="#arguments.search_option_description#"/>
			<cfprocresult name="result.cur_lookup_options">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>
</cfcomponent>
