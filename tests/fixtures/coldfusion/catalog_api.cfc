<cfcomponent>
	<cffunction name="create_catalog_message" access="public" returntype="numeric" output="no">
		<cfargument name="operator_id" type="string" required="no" />
		<cfargument name="commuter_product_id" type="string" required="no" />
		<cfargument name="payee_id" type="string" required="no" />
		<cfargument name="location_id" type="string" required="no" />
		<cfargument name="message_type" type="string" required="yes" />
		<cfargument name="text" type="string" required="yes" />
		<cfargument name="active_flag" type="numeric" required="yes" />
		<cfargument name="display_order" type="numeric" required="yes" />
		<cfargument name="create_user" type="string" required="yes" />
		<cfargument name="expiration_date" type="string" required="no" />

		<cfstoredproc procedure="catalog_api.create_catalog_message" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_operator_id" null="#iif(isNumeric(arguments.operator_id),de('no'),de('yes'))#" value="#arguments.operator_id#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_commuter_product_id" null="#iif(isNumeric(arguments.commuter_product_id),de('no'),de('yes'))#" value="#arguments.commuter_product_id#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_payee_id" null="#iif(isNumeric(arguments.payee_id),de('no'),de('yes'))#" value="#arguments.payee_id#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_location_id" null="#iif(isNumeric(arguments.location_id),de('no'),de('yes'))#" value="#arguments.location_id#" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_message_type" null="no" value="#arguments.message_type#" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_text" null="no" value="#arguments.text#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_active_flag" null="no" value="#arguments.active_flag#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_display_order" null="no" value="#arguments.display_order#" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_create_user" null="no"  value="#arguments.create_user#" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_expiration_date" null="#iif(len(trim(arguments.expiration_date)) gt 0,de('no'),de('yes'))#" value="#arguments.expiration_date#" />
		</cfstoredproc>
		<cfreturn 1/>
	</cffunction>

	<cffunction name="change_catalog_message_state" access="public" returntype="numeric" output="no">
		<cfargument name="catalog_message_id" type="numeric" required="yes" />
		<cfargument name="active_flag" type="numeric" required="yes" />
		<cfargument name="last_update_user" type="string" required="yes" />
		<cfstoredproc procedure="wweb.catalog_api.change_catalog_message_state" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_catalog_message_id" value="#arguments.catalog_message_id#" null="no" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_active_flag" value="#arguments.active_flag#" null="no" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_last_update_user" value="#arguments.last_update_user#" null="no" />
		</cfstoredproc>
		<cfreturn 1/>
	</cffunction>

	<cffunction name="update_catalog_message" access="public" returntype="numeric" output="no">
		<cfargument name="catalog_message_id" type="numeric" required="yes" />
		<cfargument name="operator_id" type="string" required="no" />
		<cfargument name="commuter_product_id" type="string" required="no"/>
		<cfargument name="payee_id" type="string" required="no" />
		<cfargument name="location_id" type="string" required="no" />
		<cfargument name="message_type" type="string" required="yes" />
		<cfargument name="text" type="string" required="yes" />
		<cfargument name="active_flag" type="numeric" required="yes" />
		<cfargument name="display_order" type="numeric" required="yes" />
		<cfargument name="last_update_user" type="string" required="yes" />
		<cfargument name="expiration_date" type="string" required="no" />

		<cfstoredproc procedure="catalog_api.update_catalog_message" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_catalog_message_id" value="#arguments.catalog_message_id#" null="no" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_operator_id" null="#iif(isNumeric(arguments.operator_id),de('no'),de('yes'))#" value="#arguments.operator_id#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_commuter_product_id" null="#iif(isNumeric(arguments.commuter_product_id),de('no'),de('yes'))#" value="#arguments.commuter_product_id#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_payee_id" null="#iif(isNumeric(arguments.payee_id),de('no'),de('yes'))#" value="#arguments.payee_id#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_location_id" null="#iif(isNumeric(arguments.location_id),de('no'),de('yes'))#" value="#arguments.location_id#" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_message_type" null="no"  value="#arguments.message_type#" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_text" null="no" value="#arguments.text#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_active_flag" null="no" value="#arguments.active_flag#" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_display_order" null="no" value="#arguments.display_order#" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_last_update_user" null="no"  value="#arguments.last_update_user#" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_expiration_date" null="#iif(len(trim(arguments.expiration_date)) gt 0,de('no'),de('yes'))#" value="#arguments.expiration_date#" />
		</cfstoredproc>
		<cfreturn 1/>
	</cffunction>

	<cffunction name="refresh_catalog" access="public" returntype="numeric" output="no">
		<cfargument name="username" type="string" required="yes" />

		<cfstoredproc procedure="wweb.uber_utils_pkg.uber_enqueue2" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_uber_prefix" null="no" value="CATREFRESH" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_source_table_name" null="no" value="Ops_Catalog_Summary" />
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_source_table_id" null="no" value="1" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_filename" null="yes" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no" />
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_process_log_id" variable="process_log_id" null="no" />
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="success_flag" null="no" />
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="process_message" null="no" />
		</cfstoredproc>
		<cfreturn 1/>
	</cffunction>

	<cffunction name="activate_commuter_product" access="public" returntype="struct" output="no">
		<cfargument name="commuter_product_id" type="numeric" required="yes" />
		<cfargument name="username" type="string" required="yes" />
		<cfset var result = StructNew() />
		<cfstoredproc procedure="wweb.catalog_api.activate_commuter_product" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_commuter_product_id"  value="#arguments.commuter_product_id#" null="no" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no" />
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no" />
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no" />
		</cfstoredproc>
		<cfreturn result />
	</cffunction>

	<cffunction name="inactivate_commuter_product" access="public" returntype="struct" output="no">
		<cfargument name="commuter_product_id" type="numeric" required="yes" />
		<cfargument name="username" type="string" required="yes" />
		<cfset var result = StructNew() />
		<cfstoredproc procedure="wweb.catalog_api.inactivate_commuter_product" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_commuter_product_id"  value="#arguments.commuter_product_id#" null="no" />
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no" />
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no" />
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no" />
		</cfstoredproc>
		<cfreturn result />
	</cffunction>
</cfcomponent>
