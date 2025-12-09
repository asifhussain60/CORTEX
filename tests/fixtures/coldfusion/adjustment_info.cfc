<cfcomponent>
	<cffunction name="employee_search_results" access="public" returntype="struct" output="no">
		<cfargument name="search_employee_id" type="string" required="no" default=""/>
		<cfargument name="search_employer_id" type="string" required="no" default=""/>
		<cfargument name="search_last_name" type="string" required="no" default=""/>
		<cfargument name="search_first_name" type="string" required="no" default=""/>
		<cfargument name="search_ssn" type="string" required="no" default=""/>
		<cfargument name="search_zip_code" type="string" required="no" default=""/>
		<cfargument name="search_employer_name" type="string" required="no" default=""/>
		<cfargument name="search_benefit_type" type="string" required="no" default=""/>
		<cfargument name="appl_user_id" type="string" required="yes" default=""/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_info.get_employee_search_results" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_id" null="#iif(isNumeric(arguments.search_employee_id),de('no'),de('yes'))#" value="#arguments.search_employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" null="#iif(isNumeric(arguments.search_employer_id),de('no'),de('yes'))#" value="#arguments.search_employer_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_lastname" null="#iif(len(trim(arguments.search_last_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_last_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_firstname" null="#iif(len(trim(arguments.search_first_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_first_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_ssn" null="#iif(len(trim(arguments.search_ssn)) gt 0,de('no'),de('yes'))#" value="#arguments.search_ssn#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_zip_code" null="#iif(len(trim(arguments.search_zip_code)) gt 0,de('no'),de('yes'))#" value="#arguments.search_zip_code#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_employer_name" null="#iif(len(trim(arguments.search_employer_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_employer_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_selected_service_type" null="#iif(len(trim(arguments.search_benefit_type)) gt 0,de('no'),de('yes'))#" value="#arguments.search_benefit_type#"/>

			<cfprocresult name="result.cur_employee_search_results"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
			<cfprocparam type="in"  cfsqltype="cf_sql_numeric" dbvarname=":p_appl_user_id" null="no" value="#arguments.appl_user_id#"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="catalog_operator_search" access="public" returntype="struct" output="no">
		<cfargument name="search_operator_id" type="string" required="no" default=""/>
		<cfargument name="search_operator_name" type="string" required="no" default=""/>
		<cfargument name="search_operator_nickname" type="string" required="no" default=""/>
		<cfargument name="search_pmss_operator_id" type="string" required="no" default=""/>
		<cfargument name="search_state" type="string" required="no" default=""/>
		<cfargument name="search_partner_type_id" type="string" required="no" default=""/>
		<cfargument name="search_uza_city" type="string" required="no" default=""/>
		<cfset var cur_catalog_operators = ""/>

		<cfstoredproc procedure="wweb.transit_catalog_info.catalog_operator_search" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_operator_id" null="#iif(isNumeric(arguments.search_operator_id),de('no'),de('yes'))#" value="#arguments.search_operator_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_operator_name" null="#iif(len(trim(arguments.search_operator_name)) gt 0,de('no'),de('yes'))#" value="#arguments.search_operator_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_operator_nickname" null="#iif(len(trim(arguments.search_operator_nickname)) gt 0,de('no'),de('yes'))#" value="#arguments.search_operator_nickname#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_pmss_operator_id" null="#iif(isNumeric(arguments.search_pmss_operator_id),de('no'),de('yes'))#" value="#arguments.search_pmss_operator_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_state" null="#iif(len(trim(arguments.search_state)) gt 0,de('no'),de('yes'))#" value="#arguments.search_state#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_partner_type_id" null="#iif(isNumeric(arguments.search_partner_type_id),de('no'),de('yes'))#" value="#arguments.search_partner_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_uza_city" null="#iif(len(trim(arguments.search_uza_city)) gt 0,de('no'),de('yes'))#" value="#arguments.search_uza_city#"/>
			<cfprocresult name="cur_catalog_operators">
		</cfstoredproc>
		<cfreturn cur_catalog_operators/>
	</cffunction>

	<cffunction name="single_adjustment_info" access="public" returntype="query" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfset var cur_single_adjustment_info = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.get_single_adjustment">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_instruction_id" value="#arguments.adjustment_instruction_id#" null="no">
		<cfprocresult name="cur_single_adjustment_info">
		</cfstoredproc>
		<cfreturn cur_single_adjustment_info/>
	</cffunction>

	<cffunction name="employee_credit_info" access="public" returntype="query" output="no">
		<cfargument name="employee_id" type="string" required="no" default=""/>
		<cfargument name="cf_txn_id" type="string" required="no" default=""/>
		<cfset var cur_employee_credit_info = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.employee_credit_info">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_id" null="#iif(isNumeric(arguments.employee_id),de('no'),de('yes'))#" value="#arguments.employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_cf_txn_id" null="#iif(isNumeric(arguments.cf_txn_id),de('no'),de('yes'))#" value="#arguments.cf_txn_id#"/>
			<cfprocresult name="cur_employee_credit_info">
		</cfstoredproc>
		<cfreturn cur_employee_credit_info/>
	</cffunction>

	<cffunction name="adjustment_type_info" access="public" returntype="query" output="no">
		<cfargument name="adjustment_type_id" type="string" required="yes"/>
		<cfset var cur_adjustment_type_info = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.get_adjustment_type_info" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocresult name="cur_adjustment_type_info">
		</cfstoredproc>
		<cfreturn cur_adjustment_type_info/>
	</cffunction>

	<cffunction name="base_invoice_template_info" access="public" returntype="query" output="no">
		<cfset var cur_base_invoice_template_info = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.get_base_invoice_template_info" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_invoice_line_template_id" null="yes">
			<cfprocresult name="cur_base_invoice_template_info">
		</cfstoredproc>
		<cfreturn cur_base_invoice_template_info/>
	</cffunction>

	<cffunction name="bulk_adj_template_info" access="public" returntype="query" output="no">
		<cfargument name="bulk_adjustment_template_id" type="string" required="no" default=""/>
		<cfargument name="active_flag" type="string" required="no" default=""/>
		<cfset var cur_bulk_adj_template_info = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.adjustment_bulk_template_info">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_bulk_adjustment_template_id" null="#iif(isNumeric(arguments.bulk_adjustment_template_id),de('no'),de('yes'))#" value="#arguments.bulk_adjustment_template_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_active_flag" null="#iif(isNumeric(arguments.active_flag),de('no'),de('yes'))#" value="#arguments.active_flag#"/>
			<cfprocresult name="cur_bulk_adj_template_info">
		</cfstoredproc>
		<cfreturn cur_bulk_adj_template_info/>
	</cffunction>

	<cffunction name="adjustment_type_list" access="public" returntype="query" output="no">
		<cfargument name="exclude_txt" type="string" required="no" default=""/>
		<cfset var cur_adjustment_type_list = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.get_adjustment_type_list">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_exclude_txt" null="#iif(len(trim(arguments.exclude_txt)) gt 0,de('no'),de('yes'))#" value="#arguments.exclude_txt#"/>
			<cfprocresult name="cur_adjustment_type_list">
		</cfstoredproc>
		<cfreturn cur_adjustment_type_list/>
	</cffunction>

	<cffunction name="check_bulk_adj_threshold" access="public" returntype="numeric" output="no">
		<cfargument name="process_log_id" type="numeric" required="yes"/>
		<cfset var threshold_exceeded = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.check_bulk_adj_threshold">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_process_log_id" value="#arguments.process_log_id#" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_threshold_exceeded" variable="threshold_exceeded" null="no">
		</cfstoredproc>
		<cfreturn threshold_exceeded/>
	</cffunction>

	<cffunction name="find_ee_commuter_card_accounts" access="public" returntype="struct" output="no">
		<cfargument name="employee_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.find_ee_commuter_card_accounts">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_employee_id" value="#arguments.employee_id#" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_transit_tran_account_number" variable="result.transit_tran_account_number">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_parking_tran_account_number" variable="result.parking_tran_account_number">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="commuter_card_account_details" access="public" returntype="query" output="no">
		<cfargument name="tran_account_number" type="string" required="yes"/>
		<cfset var cur_commuter_card_account_dtls = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.commuter_card_account_details">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_tran_account_number" value="#arguments.tran_account_number#" null="no"/>
			<cfprocresult name="cur_commuter_card_account_dtls">
		</cfstoredproc>
		<cfreturn cur_commuter_card_account_dtls/>
	</cffunction>

	<cffunction name="consolidate_cx_ee_check" access="public" returntype="struct" output="no">
		<cfargument name="transit_employee_id" type="numeric" required="yes"/>
		<cfargument name="parking_employee_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="wp_employee_info.consolidate_cx_ee_check" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_transit_employee_id" null="no" value="#arguments.transit_employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_parking_employee_id" null="no" value="#arguments.parking_employee_id#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="cx_ee_consolidation_info" access="public" returntype="struct" output="no">
		<cfargument name="transit_employee_id" type="numeric" required="yes"/>
		<cfargument name="parking_employee_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="wp_employee_info.cx_ee_consolidation_info" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_transit_employee_id" null="no" value="#arguments.transit_employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_parking_employee_id" null="no" value="#arguments.parking_employee_id#"/>
			<cfprocresult name="result.cur_transit_info" resultset="1">
			<cfprocresult name="result.cur_parking_info" resultset="2">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="unprocessable_bulk_adjs" returntype="query" access="public" output="no">
		<cfargument name="process_log_id" type="numeric" required="yes"/>
		<cfset var cur_unprocessable_bulk_adjs = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.unprocessable_bulk_adjs" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_process_log_id" value="#arguments.process_log_id#" null="no">
			<cfprocresult name="cur_unprocessable_bulk_adjs">
		</cfstoredproc>
		<cfreturn cur_unprocessable_bulk_adjs/>
	</cffunction>

	<cffunction name="adj_election_types" returntype="query" access="public" output="no">
		<cfargument name="adjustment_election_type_id" type="string" required="no" default=""/>
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfset var cur_adj_election_types = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.adj_election_types" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_election_type_id" null="#iif(isNumeric(arguments.adjustment_election_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_election_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocresult name="cur_adj_election_types">
		</cfstoredproc>
		<cfreturn cur_adj_election_types/>
	</cffunction>

	<cffunction name="adj_type_display_fields" returntype="query" access="public" output="no">
		<cfargument name="adj_display_field_id" type="string" required="no" default=""/>
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfset var cur_adj_type_display_fields = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.adj_type_display_fields" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_display_field_id" null="#iif(isNumeric(arguments.adj_display_field_id),de('no'),de('yes'))#" value="#arguments.adj_display_field_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocresult name="cur_adj_type_display_fields">
		</cfstoredproc>
		<cfreturn cur_adj_type_display_fields/>
	</cffunction>

	<cffunction name="adj_type_reason_codes" returntype="query" access="public" output="no">
		<cfargument name="adj_reason_code_id" type="string" required="no" default=""/>
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfset var cur_adj_type_reason_codes = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.adj_type_reason_codes" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_reason_code_id" null="#iif(isNumeric(arguments.adj_reason_code_id),de('no'),de('yes'))#" value="#arguments.adj_reason_code_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocresult name="cur_adj_type_reason_codes">
		</cfstoredproc>
		<cfreturn cur_adj_type_reason_codes/>
	</cffunction>

	<cffunction name="adj_ui_rules" returntype="query" access="public" output="no">
		<cfargument name="adjustment_ui_rule_id" type="string" required="no" default=""/>
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfset var cur_adj_ui_rules = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.adj_ui_rules" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_ui_rule_id" null="#iif(isNumeric(arguments.adjustment_ui_rule_id),de('no'),de('yes'))#" value="#arguments.adjustment_ui_rule_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocresult name="cur_adj_ui_rules">
		</cfstoredproc>
		<cfreturn cur_adj_ui_rules/>
	</cffunction>

	<cffunction name="adj_ui_validation_rules" returntype="query" access="public" output="no">
		<cfargument name="adj_ui_validation_rule_id" type="string" required="no" default=""/>
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfset var cur_adj_ui_validation_rules = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.adj_ui_validation_rules" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_ui_validation_rule_id" null="#iif(isNumeric(arguments.adj_ui_validation_rule_id),de('no'),de('yes'))#" value="#arguments.adj_ui_validation_rule_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocresult name="cur_adj_ui_validation_rules">
		</cfstoredproc>
		<cfreturn cur_adj_ui_validation_rules/>
	</cffunction>

	<cffunction name="assignable_display_fields" returntype="query" access="public" output="no">
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfargument name="adj_display_field_id" type="string" required="no" default=""/>
		<cfset var cur_assignable_display_fields = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.assignable_display_fields" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_display_field_id" null="#iif(isNumeric(arguments.adj_display_field_id),de('no'),de('yes'))#" value="#arguments.adj_display_field_id#"/>
			<cfprocresult name="cur_assignable_display_fields">
		</cfstoredproc>
		<cfreturn cur_assignable_display_fields/>
	</cffunction>

	<cffunction name="applicable_adj_types" returntype="query" access="public" output="no">
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfargument name="benefit_type_id" type="string" required="no" default=""/>
		<cfargument name="election_type_id" type="string" required="no" default=""/>
		<cfset var cur_applicable_adj_types = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.applicable_adj_types" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" null="#iif(isNumeric(arguments.benefit_type_id),de('no'),de('yes'))#" value="#arguments.benefit_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_election_type_id" null="#iif(isNumeric(arguments.election_type_id),de('no'),de('yes'))#" value="#arguments.election_type_id#"/>
			<cfprocresult name="cur_applicable_adj_types">
		</cfstoredproc>
		<cfreturn cur_applicable_adj_types/>
	</cffunction>

	<cffunction name="applicable_adj_display_fields" returntype="query" access="public" output="no">
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfset var cur_applicable_adjdisplay_flds = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.applicable_adj_display_fields" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocresult name="cur_applicable_adjdisplay_flds">
		</cfstoredproc>
		<cfreturn cur_applicable_adjdisplay_flds/>
	</cffunction>

	<cffunction name="transit_operator_info" returntype="query" access="public" output="no">
		<cfargument name="operator_id" type="numeric" required="yes"/>
		<cfset var cur_transit_operator_info = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.get_transit_operator_info" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_operator_id" value="#arguments.operator_id#"  null="no"/>
			<cfprocresult name="cur_transit_operator_info">
		</cfstoredproc>
		<cfreturn cur_transit_operator_info/>
	</cffunction>

	<cffunction name="runtime_adj_validation_rules" returntype="struct" access="public" output="no">
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>
		<cfstoredproc procedure="wweb.adjustment_info.runtime_adj_validation_rules" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" value="#arguments.adjustment_type_id#" null="no"/>
			<cfprocresult name="cur_failure_rules" resultset="1">
			<cfprocresult name="cur_warning_rules" resultset="2">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="adj_type_er_exclusions" returntype="query" access="public" output="no">
		<cfargument name="adj_type_er_exclusion_id" type="string" required="no" default=""/>
		<cfargument name="adjustment_type_id" type="string" required="no" default=""/>
		<cfargument name="employer_id" type="string" required="no" default=""/>
		<cfset var cur_adj_type_er_exclusions = ""/>
		<cfstoredproc procedure="wweb.adjustment_info.adj_type_er_exclusions" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_type_er_exclusion_id" null="#iif(isNumeric(arguments.adj_type_er_exclusion_id),de('no'),de('yes'))#" value="#arguments.adj_type_er_exclusion_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" null="#iif(isNumeric(arguments.employer_id),de('no'),de('yes'))#" value="#arguments.employer_id#"/>
			<cfprocresult name="cur_adj_type_er_exclusions">
		</cfstoredproc>
		<cfreturn cur_adj_type_er_exclusions/>
	</cffunction>

	<cffunction name="election_details" returntype="query" access="public" output="no">
		<cfargument name="commuter_election_id" type="numeric" required="yes"/>
		<cfset var cur_commuter_election = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.election_details">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_commuter_election_id" value="#arguments.commuter_election_id#" null="no">
			<cfprocresult name="cur_commuter_election">
		</cfstoredproc>
		<cfreturn cur_commuter_election/>
	</cffunction>

	<cffunction name="applied_adj_dtls" returntype="query" access="public" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfset var cur_applied_payroll_adj_dtls = ""/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_info.get_applied_payroll_adj_dtls">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_instr_id" value="#arguments.adjustment_instruction_id#" null="no">
			<cfprocresult name="cur_applied_payroll_adj_dtls">
		</cfstoredproc>
		<cfreturn cur_applied_payroll_adj_dtls/>
	</cffunction>

	<!--- Get array of adjustment types --->
	<cffunction name="adjustment_types_lov_array" returnType="array" access="remote">
		<!--- Define variables --->
		<cfset var cur_adjustment_type_list = "">
		<cfset var result=ArrayNew(2)>
		<cfset var i=0>

		<cfstoredproc procedure="wweb.adjustment_info.get_adjustment_type_list" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_exclude_txt" value="ALL" null="no">
			<cfprocresult name="cur_adjustment_type_list">
		</cfstoredproc>

		<!--- Convert results to array --->
		<cfloop index="i" from="1" to="#cur_adjustment_type_list.RecordCount#">
			<cfset result[i][1]=cur_adjustment_type_list.adjustment_type_id[i]>
			<cfset result[i][2]=cur_adjustment_type_list.name[i]>
		</cfloop>

		<!--- And return it --->
		<cfreturn result>
	</cffunction>

	<!--- Get array of reason codes --->
	<cffunction name="reason_codes_lov_array" returnType="array" access="remote">
		<cfargument name="adjustment_type_id" type="string" required="no" default="">

		<!--- Define variables --->
		<cfset var cur_adj_type_reason_codes = "">
		<cfset var result=ArrayNew(2)>
		<cfset var i=0>

<!--- 		<cfif arguments.adjustment_type_id IS NOT "-1">
			<cfstoredproc procedure="wweb.adjustment_info.adj_type_reason_codes" datasource="#request.ds#">
				<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_reason_code_id" null="yes">
				<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#">
				<cfprocresult name="cur_adj_type_reason_codes">
			</cfstoredproc>
		<cfelse> --->
			<cfstoredproc procedure="wweb.adjustment_info.adj_type_reason_codes_ajax" datasource="#request.ds#">
				<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_reason_code_id" null="yes">
				
				<cfif arguments.adjustment_type_id IS "-1">
					<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="yes">
				<cfelse>
					<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="#iif(isNumeric(arguments.adjustment_type_id),de('no'),de('yes'))#" value="#arguments.adjustment_type_id#">
				</cfif>
				<cfprocresult name="cur_adj_type_reason_codes">
			</cfstoredproc>
		<!--- </cfif> --->

		<!--- Convert results to array --->
		<cfloop index="i" from="1" to="#cur_adj_type_reason_codes.RecordCount#">
			<cfset result[i][1]=cur_adj_type_reason_codes.reason[i]>
			<cfset result[i][2]=cur_adj_type_reason_codes.reason[i]>
		</cfloop>

		<!--- And return it --->
		<cfreturn result>
	</cffunction>
</cfcomponent>
