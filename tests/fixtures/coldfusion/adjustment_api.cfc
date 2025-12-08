<cfcomponent>
	<cffunction name="add_adjustment" access="public" returntype="struct" output="no">
		<cfargument name="employee_id" type="numeric" required="yes"/>
		<cfargument name="employer_id" type="numeric" required="yes"/>
		<cfargument name="transaction_id" type="numeric" required="yes"/>
		<cfargument name="selected_election_type" type="string" required="yes"/>
		<cfargument name="benefit_amount" type="numeric" required="yes"/>
		<cfargument name="other_expenses_amount" type="numeric" required="yes"/>
		<cfargument name="total_amount" type="numeric" required="yes"/>
		<cfargument name="benefit_month" type="string" required="yes"/>
		<cfargument name="selected_benefit_type" type="numeric" required="yes"/>
		<cfargument name="case_number" type="string" required="no" default=""/>
		<cfargument name="case_originator" type="string" required="no" default=""/>
		<cfargument name="selected_adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="selected_agency_id" type="string" required="no" default=""/>
		<cfargument name="pass_credit_flag" type="string" required="no" default=""/>
		<cfargument name="selected_reason_code" type="string" required="no" default=""/>
		<cfargument name="affidavit_sent_date" type="string" required="no" default=""/>
		<cfargument name="affidavit_received_date" type="string" required="no" default=""/>
		<cfargument name="manual_check_flag" type="string" required="no" default=""/>
		<cfargument name="comments" type="string" required="no" default=""/>
		<cfargument name="immediate_pay_flag" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.add_adj_instr">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_id" value="#arguments.employee_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" value="#arguments.employer_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_source_id" value="#arguments.transaction_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_source_type" value="#arguments.selected_election_type#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" scale="2" dbvarname=":p_transaction_amount" value="#arguments.benefit_amount#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" scale="2" dbvarname=":p_other_expenses_amount" value="#arguments.other_expenses_amount#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" scale="2" dbvarname=":p_amount" value="#arguments.total_amount#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_usage_month" value="#arguments.benefit_month#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" value="#arguments.selected_benefit_type#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_case_number" null="#iif(len(trim(arguments.case_number)) gt 0,de('no'),de('yes'))#" value="#arguments.case_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_case_originator" null="#iif(len(trim(arguments.case_originator)) gt 0,de('no'),de('yes'))#" value="#arguments.case_originator#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" value="#arguments.selected_adjustment_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_agency_id" null="#iif(isNumeric(arguments.selected_agency_id),de('no'),de('yes'))#" value="#arguments.selected_agency_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_pass_credit_flag" null="#iif(isNumeric(arguments.pass_credit_flag),de('no'),de('yes'))#" value="#arguments.pass_credit_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_reason_code_id" null="yes"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_reason_code" null="#iif(len(trim(arguments.selected_reason_code)) gt 0,de('no'),de('yes'))#" value="#arguments.selected_reason_code#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_affidavit_sent_date" null="#iif(len(trim(arguments.affidavit_sent_date)) gt 0,de('no'),de('yes'))#" value="#arguments.affidavit_sent_date#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_affidavit_received_date" null="#iif(len(trim(arguments.affidavit_received_date)) gt 0,de('no'),de('yes'))#" value="#arguments.affidavit_received_date#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_manual_check_flag" null="#iif(isNumeric(arguments.manual_check_flag),de('no'),de('yes'))#" value="#arguments.manual_check_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" null="#iif(len(trim(arguments.comments)) gt 0,de('no'),de('yes'))#" value="#arguments.comments#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_associated_adjustment_id" null="yes">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_immediate_pay_flag" null="#iif(isNumeric(arguments.immediate_pay_flag),de('no'),de('yes'))#" value="#arguments.immediate_pay_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">

			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_instruction_id" variable="result.adjustment_instruction_id" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="edit_adjustment" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfargument name="transaction_id" type="numeric" required="yes"/>
		<cfargument name="selected_election_type" type="string" required="yes"/>
		<cfargument name="benefit_amount" type="numeric" required="yes"/>
		<cfargument name="other_expenses_amount" type="numeric" required="yes"/>
		<cfargument name="total_amount" type="numeric" required="yes"/>
		<cfargument name="benefit_month" type="string" required="yes"/>
		<cfargument name="selected_benefit_type" type="numeric" required="yes"/>
		<cfargument name="case_number" type="string" required="no" default=""/>
		<cfargument name="case_originator" type="string" required="no" default=""/>
		<cfargument name="selected_adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="selected_agency_id" type="string" required="no" default=""/>
		<cfargument name="pass_credit_flag" type="string" required="no" default=""/>
		<cfargument name="selected_reason_code" type="string" required="no" default=""/>
		<cfargument name="affidavit_sent_date" type="string" required="no" default=""/>
		<cfargument name="affidavit_received_date" type="string" required="no" default=""/>
		<cfargument name="manual_check_flag" type="string" required="no" default=""/>
		<cfargument name="comments" type="string" required="no" default=""/>
		<cfargument name="immediate_pay_flag" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.update_adj_instr">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_instruction_id" value="#arguments.adjustment_instruction_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_source_id" value="#arguments.transaction_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_source_type" value="#arguments.selected_election_type#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" scale="2" dbvarname=":p_transaction_amount" value="#arguments.benefit_amount#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" scale="2" dbvarname=":p_other_expenses_amount" value="#arguments.other_expenses_amount#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" scale="2" dbvarname=":p_amount" value="#arguments.total_amount#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_usage_month" value="#arguments.benefit_month#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" value="#arguments.selected_benefit_type#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_case_number" null="#iif(len(trim(arguments.case_number)) gt 0,de('no'),de('yes'))#" value="#arguments.case_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_case_originator" null="#iif(len(trim(arguments.case_originator)) gt 0,de('no'),de('yes'))#" value="#arguments.case_originator#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" value="#arguments.selected_adjustment_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_agency_id" null="#iif(isNumeric(arguments.selected_agency_id),de('no'),de('yes'))#" value="#arguments.selected_agency_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_pass_credit_flag" null="#iif(isNumeric(arguments.pass_credit_flag),de('no'),de('yes'))#" value="#arguments.pass_credit_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_reason_code_id" null="yes"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_reason_code" null="#iif(len(trim(arguments.selected_reason_code)) gt 0,de('no'),de('yes'))#" value="#arguments.selected_reason_code#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_affidavit_sent_date" null="#iif(len(trim(arguments.affidavit_sent_date)) gt 0,de('no'),de('yes'))#" value="#arguments.affidavit_sent_date#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_affidavit_received_date" null="#iif(len(trim(arguments.affidavit_received_date)) gt 0,de('no'),de('yes'))#" value="#arguments.affidavit_received_date#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_manual_check_flag" null="#iif(isNumeric(arguments.manual_check_flag),de('no'),de('yes'))#" value="#arguments.manual_check_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" null="#iif(len(trim(arguments.comments)) gt 0,de('no'),de('yes'))#" value="#arguments.comments#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_associated_adjustment_id" null="yes">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_immediate_pay_flag" null="#iif(isNumeric(arguments.immediate_pay_flag),de('no'),de('yes'))#" value="#arguments.immediate_pay_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="approve_adjustment" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfargument name="comments" type="string" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.approve_adj_instr">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_instruction_id" value="#arguments.adjustment_instruction_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" value="#arguments.comments#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="reject_adjustment" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfargument name="comments" type="string" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.reject_adj_instr">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_instruction_id" value="#arguments.adjustment_instruction_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" value="#arguments.comments#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="cancel_adjustment" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfargument name="comments" type="string" required="no"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.cancel_adj_instr">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_instruction_id" value="#arguments.adjustment_instruction_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" null="#iif(len(trim(arguments.comments)) gt 0,de('no'),de('yes'))#" value="#arguments.comments#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_adjustment" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.delete_adj_instr">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_instruction_id" value="#adjustment_instruction_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="add_comments" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfargument name="comments" type="string" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.add_comments">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_adjustment_instruction_id" value="#arguments.adjustment_instruction_id#" null="no">

			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" value="#arguments.comments#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="cancel_cx_txn" access="public" returntype="struct" output="no">
		<cfargument name="employee_id" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.wp_employee_api.cancel_cx_txn">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_id" value="#arguments.employee_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="create_late_pmb" access="public" returntype="struct" output="no">
		<cfargument name="employee_id" type="numeric" required="yes"/>
		<cfargument name="benefit_type_id" type="numeric" required="yes"/>
		<cfargument name="usage_month" type="string" required="yes"/>
		<cfargument name="amount" type="numeric" required="yes"/>
		<cfargument name="reason" type="string" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.wp_employee_api.create_late_pmb">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_id" value="#arguments.employee_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" value="#arguments.benefit_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_usage_month" value="#arguments.usage_month#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_amount" value="#arguments.amount#" scale="2" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_reason" value="#arguments.reason#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_update_user" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<!-- credits -->
	<cffunction name="add_carry_forward_credit" access="public" returntype="struct" output="no">
		<cfargument name="benefit_type_id" type="numeric" required="yes"/>
		<cfargument name="employee_id" type="numeric" required="yes"/>
		<cfargument name="employer_id" type="numeric" required="yes"/>
		<cfargument name="status_id" type="numeric" required="yes"/>
		<cfargument name="amount" type="numeric" required="yes"/>
		<cfargument name="effective_month" type="string" required="yes"/>
		<cfargument name="rollover_credit_flag" type="numeric" required="yes"/>
		<cfargument name="comments" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.add_carry_forward_credit">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" value="#arguments.benefit_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_id" value="#arguments.employee_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" value="#arguments.employer_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_status_id" value="#arguments.status_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_amount" value="#arguments.amount#" scale="2" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_effective_month" value="#arguments.effective_month#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_rollover_credit_flag" value="#arguments.rollover_credit_flag#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" null="#iif(len(trim(arguments.comments)) gt 0,de('no'),de('yes'))#" value="#arguments.comments#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="update_carry_forward_credit" access="public" returntype="struct" output="no">
		<cfargument name="cf_txn_id" type="numeric" required="yes"/>
		<cfargument name="benefit_type_id" type="numeric" required="yes"/>
		<cfargument name="employee_id" type="numeric" required="yes"/>
		<cfargument name="employer_id" type="numeric" required="yes"/>
		<cfargument name="status_id" type="numeric" required="yes"/>
		<cfargument name="amount" type="numeric" required="yes"/>
		<cfargument name="effective_month" type="string" required="yes"/>
		<cfargument name="rollover_credit_flag" type="numeric" required="yes"/>
		<cfargument name="comments" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.update_carry_forward_credit">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_cf_txn_id" value="#arguments.cf_txn_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" value="#arguments.benefit_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_id" value="#arguments.employee_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" value="#arguments.employer_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_status_id" value="#arguments.status_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_amount" value="#arguments.amount#" scale="2" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_effective_month" value="#arguments.effective_month#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_rollover_credit_flag" value="#arguments.rollover_credit_flag#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" null="#iif(len(trim(arguments.comments)) gt 0,de('no'),de('yes'))#" value="#arguments.comments#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="cancel_carry_forward_credit" access="public" returntype="struct" output="no">
		<cfargument name="cf_txn_id" type="numeric" required="yes"/>
		<cfargument name="comments" type="string" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfargument name="user_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.cancel_carry_forward_credit">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_cf_txn_id" value="#arguments.cf_txn_id#" null="no">
<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_comments" value="#arguments.comments#" null="no"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_user_id" value="#arguments.user_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_carry_forward_credit" access="public" returntype="struct" output="no">
		<cfargument name="cf_txn_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.delete_carry_forward_credit">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_cf_txn_id" value="#arguments.cf_txn_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="convert_carry_forward_to_pmb" access="public" returntype="struct" output="no">
		<cfargument name="cf_txn_id" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.convert_carry_forward_to_pmb">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_cf_txn_id" value="#arguments.cf_txn_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="add_bulk_adj_template" returntype="struct" output="no" access="public">
		<cfargument name="template_name" type="string" required="yes"/>
		<cfargument name="description" type="string" required="no" default=""/>
		<cfargument name="action_for_employee" type="string" required="no" default=""/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="benefit_type_id" type="numeric" required="yes"/>
		<cfargument name="election_type_id" type="numeric" required="yes"/>
		<cfargument name="operator_id" type="string" required="no" default=""/>
		<cfargument name="pass_credit_flag" type="string" required="no" default=""/>
		<cfargument name="paper_check_flag" type="string" required="no" default=""/>
		<cfargument name="reason_code" type="string" required="no" default=""/>
		<cfargument name="immediate_pay_flag" type="string" required="no" default=""/>
		<cfargument name="id_ee_via_employee_id" type="string" required="no" default=""/>
		<cfargument name="id_ee_via_employer_id_number" type="string" required="no" default=""/>
		<cfargument name="id_ee_via_serial_number" type="string" required="no" default=""/>
		<cfargument name="id_ee_via_ssn" type="string" required="no" default=""/>
		<cfargument name="id_commuter_product_list" type="string" required="no" default=""/>
		<cfargument name="employee_email_template_id" type="string" required="no" default=""/>
		<cfargument name="email_to" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.add_bulk_adj_template" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_template_name" value="#arguments.template_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_description" null="#iif(len(trim(arguments.description)) gt 0,de('no'),de('yes'))#" value="#arguments.description#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_action_for_employee" null="#iif(len(trim(arguments.action_for_employee)) gt 0,de('no'),de('yes'))#" value="#arguments.action_for_employee#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" value="#arguments.adjustment_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" value="#arguments.benefit_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_election_type_id" value="#arguments.election_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_operator_id" null="#iif(isNumeric(arguments.operator_id),de('no'),de('yes'))#" value="#arguments.operator_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_pass_credit_flag" null="#iif(isNumeric(arguments.pass_credit_flag),de('no'),de('yes'))#" value="#arguments.pass_credit_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_paper_check_flag" null="#iif(isNumeric(arguments.paper_check_flag),de('no'),de('yes'))#" value="#arguments.paper_check_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_reason_code" null="#iif(len(trim(arguments.reason_code)) gt 0,de('no'),de('yes'))#" value="#arguments.reason_code#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_immediate_pay_flag" null="#iif(isNumeric(arguments.immediate_pay_flag),de('no'),de('yes'))#" value="#arguments.immediate_pay_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_id_ee_via_employee_id" null="#iif(isNumeric(arguments.id_ee_via_employee_id),de('no'),de('yes'))#" value="#arguments.id_ee_via_employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_id_ee_via_employer_id_number" null="#iif(isNumeric(arguments.id_ee_via_employer_id_number),de('no'),de('yes'))#" value="#arguments.id_ee_via_employer_id_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_id_ee_via_serial_number" null="#iif(isNumeric(arguments.id_ee_via_serial_number),de('no'),de('yes'))#" value="#arguments.id_ee_via_serial_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_id_ee_via_ssn" null="#iif(isNumeric(arguments.id_ee_via_ssn),de('no'),de('yes'))#" value="#arguments.id_ee_via_ssn#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_id_commuter_product_list" null="#iif(len(trim(arguments.id_commuter_product_list)) gt 0,de('no'),de('yes'))#" value="#arguments.id_commuter_product_list#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_email_template_id" null="#iif(isNumeric(arguments.employee_email_template_id),de('no'),de('yes'))#" value="#arguments.employee_email_template_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_email_to" null="#iif(len(trim(arguments.email_to)) gt 0,de('no'),de('yes'))#" value="#arguments.email_to#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="update_bulk_adj_template" returntype="struct" output="no" access="public">
		<cfargument name="bulk_adjustment_template_id" type="numeric" required="yes"/>
		<cfargument name="template_name" type="string" required="yes"/>
		<cfargument name="description" type="string" required="no" default=""/>
		<cfargument name="action_for_employee" type="string" required="no" default=""/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="benefit_type_id" type="numeric" required="yes"/>
		<cfargument name="election_type_id" type="numeric" required="yes"/>
		<cfargument name="operator_id" type="string" required="no" default=""/>
		<cfargument name="pass_credit_flag" type="string" required="no" default=""/>
		<cfargument name="paper_check_flag" type="string" required="no" default=""/>
		<cfargument name="reason_code" type="string" required="no" default=""/>
		<cfargument name="immediate_pay_flag" type="string" required="no" default=""/>
		<cfargument name="id_ee_via_employee_id" type="string" required="no" default=""/>
		<cfargument name="id_ee_via_employer_id_number" type="string" required="no" default=""/>
		<cfargument name="id_ee_via_serial_number" type="string" required="no" default=""/>
		<cfargument name="id_ee_via_ssn" type="string" required="no" default=""/>
		<cfargument name="id_commuter_product_list" type="string" required="no" default=""/>
		<cfargument name="employee_email_template_id" type="string" required="no" default=""/>
		<cfargument name="email_to" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.update_bulk_adj_template" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_bulk_adjustment_template_id" value="#arguments.bulk_adjustment_template_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_template_name" value="#arguments.template_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_description" null="#iif(len(trim(arguments.description)) gt 0,de('no'),de('yes'))#" value="#arguments.description#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_action_for_employee" null="#iif(len(trim(arguments.action_for_employee)) gt 0,de('no'),de('yes'))#" value="#arguments.action_for_employee#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" value="#arguments.adjustment_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" value="#arguments.benefit_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_election_type_id" value="#arguments.election_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_operator_id" null="#iif(isNumeric(arguments.operator_id),de('no'),de('yes'))#" value="#arguments.operator_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_pass_credit_flag" null="#iif(isNumeric(arguments.pass_credit_flag),de('no'),de('yes'))#" value="#arguments.pass_credit_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_paper_check_flag" null="#iif(isNumeric(arguments.paper_check_flag),de('no'),de('yes'))#" value="#arguments.paper_check_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_reason_code" null="#iif(len(trim(arguments.reason_code)) gt 0,de('no'),de('yes'))#" value="#arguments.reason_code#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_immediate_pay_flag" null="#iif(isNumeric(arguments.immediate_pay_flag),de('no'),de('yes'))#" value="#arguments.immediate_pay_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_id_ee_via_employee_id" null="#iif(isNumeric(arguments.id_ee_via_employee_id),de('no'),de('yes'))#" value="#arguments.id_ee_via_employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_id_ee_via_employer_id_number" null="#iif(isNumeric(arguments.id_ee_via_employer_id_number),de('no'),de('yes'))#" value="#arguments.id_ee_via_employer_id_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_id_ee_via_serial_number" null="#iif(isNumeric(arguments.id_ee_via_serial_number),de('no'),de('yes'))#" value="#arguments.id_ee_via_serial_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_id_ee_via_ssn" null="#iif(isNumeric(arguments.id_ee_via_ssn),de('no'),de('yes'))#" value="#arguments.id_ee_via_ssn#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_id_commuter_product_list" null="#iif(len(trim(arguments.id_commuter_product_list)) gt 0,de('no'),de('yes'))#" value="#arguments.id_commuter_product_list#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employee_email_template_id" null="#iif(isNumeric(arguments.employee_email_template_id),de('no'),de('yes'))#" value="#arguments.employee_email_template_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_email_to" null="#iif(len(trim(arguments.email_to)) gt 0,de('no'),de('yes'))#" value="#arguments.email_to#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_bulk_adj_template" returntype="struct" output="no" access="public">
		<cfargument name="bulk_adjustment_template_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.delete_bulk_adj_template" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_bulk_adjustment_template_id" value="#arguments.bulk_adjustment_template_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="change_bulk_adj_template_state" returntype="struct" output="no" access="public">
		<cfargument name="bulk_adjustment_template_id" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.change_bulk_adj_template_state" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_bulk_adjustment_template_id" value="#arguments.bulk_adjustment_template_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="bulk_adjustment_preprocess" returntype="struct" output="no" access="public">
		<cfargument name="process_log_id" type="numeric" required="yes"/>
		<cfargument name="parent_id" type="numeric" required="yes"/>
		<cfargument name="parent_table_name" type="string" required="yes"/>
		<cfargument name="election_type_id" type="numeric" required="yes"/>
		<cfargument name="benefit_type_id" type="numeric" required="yes"/>
		<cfargument name="benefit_month" type="string" required="yes"/>
		<cfargument name="operator_id" type="string" required="no"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.bulk_adjustment_preprocess" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_process_log_id" value="#arguments.process_log_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_parent_id" value="#arguments.parent_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_parent_table_name" value="#arguments.parent_table_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_election_type_id" value="#arguments.election_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" value="#arguments.benefit_type_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_benefit_month" value="#arguments.benefit_month#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_operator_id" null="#iif(isNumeric(arguments.operator_id),de('no'),de('yes'))#" value="#arguments.operator_id#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_threshold_exceeded" variable="result.threshold_exceeded" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="add_commuter_card_txn" returntype="struct" output="no" access="public">
		<cfargument name="institution_number" type="string" required="yes"/>
		<cfargument name="prefix" type="string" required="yes"/>
		<cfargument name="tran_account_number" type="numeric" required="yes"/>
		<cfargument name="mvefd_tran_process_date" type="string" required="yes"/>
		<cfargument name="debit_credit_ind" type="string" required="yes"/>
		<cfargument name="card_number" type="string" required="yes"/>
		<cfargument name="cardholder_name" type="string" required="yes"/>
		<cfargument name="transaction_type" type="string" required="no" default=""/>
		<cfargument name="transaction_amount" type="numeric" required="yes"/>
		<cfargument name="transaction_date" type="string" required="no" default=""/>
		<cfargument name="terminal_number" type="string" required="no" default=""/>
		<cfargument name="terminal_transaction_seq_num" type="string" required="no" default=""/>
		<cfargument name="transaction_response" type="string" required="no" default=""/>
		<cfargument name="terminal_address" type="string" required="no" default=""/>
		<cfargument name="terminal_city" type="string" required="no" default=""/>
		<cfargument name="terminal_state" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.add_commuter_card_txn" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_institution_number" value="#arguments.institution_number#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_prefix" value="#arguments.prefix#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_tran_account_number" value="#arguments.tran_account_number#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_mvefd_tran_process_date" value="#arguments.mvefd_tran_process_date#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_debit_credit_ind" value="#arguments.debit_credit_ind#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_card_number" value="#arguments.card_number#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_cardholder_name" value="#arguments.cardholder_name#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_transaction_type" null="#iif(isNumeric(arguments.transaction_type),de('no'),de('yes'))#" value="#arguments.transaction_type#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_transaction_amount" value="#arguments.transaction_amount#" scale="2" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_transaction_date" null="#iif(len(trim(arguments.transaction_date)) gt 0,de('no'),de('yes'))#" value="#arguments.transaction_date#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_terminal_number" null="#iif(len(trim(arguments.terminal_number)) gt 0,de('no'),de('yes'))#" value="#arguments.terminal_number#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_terminal_transaction_seq_num" null="#iif(len(trim(arguments.terminal_transaction_seq_num)) gt 0,de('no'),de('yes'))#" value="#arguments.terminal_transaction_seq_num#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_transaction_response" null="#iif(len(trim(arguments.transaction_response)) gt 0,de('no'),de('yes'))#" value="#arguments.transaction_response#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_terminal_address" null="#iif(len(trim(arguments.terminal_address)) gt 0,de('no'),de('yes'))#" value="#arguments.terminal_address#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_terminal_city" null="#iif(len(trim(arguments.terminal_city)) gt 0,de('no'),de('yes'))#" value="#arguments.terminal_city#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_terminal_state" null="#iif(len(trim(arguments.terminal_state)) gt 0,de('no'),de('yes'))#" value="#arguments.terminal_state#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_commuter_card_txn" returntype="struct" output="no" access="public">
		<cfargument name="card_txn_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>
		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.delete_commuter_card_txn" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_card_txn_id" value="#arguments.card_txn_id#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="edit_commuter_card_funding_amount" returntype="struct" output="no" access="public">
		<cfargument name="funding_id" type="numeric" required="yes"/>
		<cfargument name="funding_amount" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.adjustment_api.edit_commuter_card_funding_amt" returncode="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_funding_id" value="#arguments.funding_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_funding_amount" value="#arguments.funding_amount#" scale="2" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="consolidate_cx_employee" access="public" returntype="struct" output="no">
		<cfargument name="transit_employee_id" type="numeric" required="yes"/>
		<cfargument name="parking_employee_id" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="wp_employee_api.consolidate_cx_employee" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_transit_employee_id" null="no" value="#arguments.transit_employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_parking_employee_id" null="no" value="#arguments.parking_employee_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>


	<cffunction name="add_adj_election_type" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="benefit_type_id" type="numeric" required="yes"/>
		<cfargument name="election_type_id" type="string" required="no" default=""/>
		<cfargument name="cxpf_flag" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.add_adj_election_type" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" null="no" value="#arguments.benefit_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_election_type_id" null="#iif(isNumeric(arguments.election_type_id),de('no'),de('yes'))#" value="#arguments.election_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_pfcx_er_adj_flag" null="no" value="#arguments.cxpf_flag#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_adj_election_type" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_election_type_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.delete_adj_election_type" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_election_type_id" null="no" value="#arguments.adjustment_election_type_id#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="edit_adj_election_type" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_election_type_id" type="numeric" required="yes"/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="benefit_type_id" type="numeric" required="yes"/>
		<cfargument name="election_type_id" type="string" required="no" default=""/>
		<cfargument name="cxpf_flag" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.edit_adj_election_type" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_election_type_id" null="no" value="#arguments.adjustment_election_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_benefit_type_id" null="no" value="#arguments.benefit_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_election_type_id" null="#iif(isNumeric(arguments.election_type_id),de('no'),de('yes'))#" value="#arguments.election_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_pfcx_er_adj_flag" null="no" value="#arguments.cxpf_flag#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="add_adj_type_display_field" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="adj_type_base_display_field_id" type="string" required="yes"/>
		<cfargument name="label_display_name" type="string" required="yes"/>
		<cfargument name="form_field_validation_req_flag" type="string" required="no" default=""/>
		<cfargument name="default_submitted_value" type="string" required="no" default=""/>
		<cfargument name="default_display_value" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.add_adj_type_display_field" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_type_base_display_field_id" null="no" value="#arguments.adj_type_base_display_field_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_label_display_name" null="no" value="#arguments.label_display_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_form_field_validation_req" null="#iif(isNumeric(arguments.form_field_validation_req_flag),de('no'),de('yes'))#" value="#arguments.form_field_validation_req_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_default_submitted_value" null="#iif(len(trim(arguments.default_submitted_value)) gt 0,de('no'),de('yes'))#" value="#arguments.default_submitted_value#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_default_display_value" null="#iif(len(trim(arguments.default_display_value)) gt 0,de('no'),de('yes'))#" value="#arguments.default_display_value#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_adj_type_display_field" access="public" returntype="struct" output="no">
		<cfargument name="adj_display_field_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.delete_adj_type_display_field" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_display_field_id" null="no" value="#arguments.adj_display_field_id#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="edit_adj_type_display_field" access="public" returntype="struct" output="no">
		<cfargument name="adj_display_field_id" type="numeric" required="yes"/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="adj_type_base_display_field_id" type="string" required="yes"/>
		<cfargument name="label_display_name" type="string" required="yes"/>
		<cfargument name="form_field_validation_req_flag" type="string" required="no" default=""/>
		<cfargument name="default_submitted_value" type="string" required="no" default=""/>
		<cfargument name="default_display_value" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.edit_adj_type_display_field" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_display_field_id" null="no" value="#arguments.adj_display_field_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_type_base_display_field_id" null="no" value="#arguments.adj_type_base_display_field_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_label_display_name" null="no" value="#arguments.label_display_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_form_field_validation_req" null="#iif(isNumeric(arguments.form_field_validation_req_flag),de('no'),de('yes'))#" value="#arguments.form_field_validation_req_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_default_submitted_value" null="#iif(len(trim(arguments.default_submitted_value)) gt 0,de('no'),de('yes'))#" value="#arguments.default_submitted_value#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_default_display_value" null="#iif(len(trim(arguments.default_display_value)) gt 0,de('no'),de('yes'))#" value="#arguments.default_display_value#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="add_adj_type_reason_code" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="reason" type="string" required="yes"/>
		<cfargument name="description" type="string" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.add_adj_type_reason_code" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_reason" null="no" value="#arguments.reason#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_description" null="no" value="#arguments.description#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_adj_type_reason_code" access="public" returntype="struct" output="no">
		<cfargument name="adj_reason_code_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>
		<cfstoredproc procedure="adjustment_api.delete_adj_type_reason_code" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_reason_code_id" null="no" value="#arguments.adj_reason_code_id#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="edit_adj_type_reason_code" access="public" returntype="struct" output="no">
		<cfargument name="adj_reason_code_id" type="numeric" required="yes"/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="reason" type="string" required="yes"/>
		<cfargument name="description" type="string" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.edit_adj_type_reason_code" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_reason_code_id" null="no" value="#arguments.adj_reason_code_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_reason" null="no" value="#arguments.reason#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_description" null="no" value="#arguments.description#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="add_adj_ui_rule" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="error_correction_flag" type="numeric" required="yes"/>
		<cfargument name="allow_multiple_adj_flag" type="numeric" required="yes"/>
		<cfargument name="auto_process_daily_flag" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.add_adj_ui_rule" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_error_correction_flag" null="no" value="#arguments.error_correction_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_allow_multiple_adj_flag" null="no" value="#arguments.allow_multiple_adj_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_auto_process_daily_flag" null="no" value="#arguments.auto_process_daily_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_adj_ui_rule" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_ui_rule_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>
		<cfstoredproc procedure="adjustment_api.delete_adj_ui_rule" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_ui_rule_id" null="no" value="#arguments.adjustment_ui_rule_id#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="edit_adj_ui_rule" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_ui_rule_id" type="numeric" required="yes"/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="error_correction_flag" type="numeric" required="yes"/>
		<cfargument name="allow_multiple_adj_flag" type="numeric" required="yes"/>
		<cfargument name="auto_process_daily_flag" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.edit_adj_ui_rule" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_ui_rule_id" null="no" value="#arguments.adjustment_ui_rule_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_error_correction_flag" null="no" value="#arguments.error_correction_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_allow_multiple_adj_flag" null="no" value="#arguments.allow_multiple_adj_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_auto_process_daily_flag" null="no" value="#arguments.auto_process_daily_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="add_adj_ui_validation_rule" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="rule_name" type="string" required="yes"/>
		<cfargument name="rule_sql" type="any" required="no" default=""/>
		<cfargument name="rule_violation_message" type="string" required="no" default=""/>
		<cfargument name="active_flag" type="numeric" required="yes"/>
		<cfargument name="warning_only_flag" type="numeric" required="yes"/>
		<cfargument name="notification_email_flag" type="numeric" required="yes"/>
		<cfargument name="notify_client_services_flag" type="numeric" required="yes"/>
		<cfargument name="notify_requestor_flag" type="numeric" required="yes"/>
		<cfargument name="notification_recipient_list" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.add_adj_ui_validation_rule" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_name" null="no" value="#arguments.rule_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_clob" dbvarname=":p_rule_sql" null="#iif(len(trim(arguments.rule_sql)) gt 0,de('no'),de('yes'))#" value="#arguments.rule_sql#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_rule_violation_message" null="#iif(len(trim(arguments.rule_violation_message)) gt 0,de('no'),de('yes'))#" value="#arguments.rule_violation_message#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_active_flag" null="no" value="#arguments.active_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_warning_only_flag" null="no" value="#arguments.warning_only_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_notification_email_flag" null="no" value="#arguments.notification_email_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_notify_client_services_flag" null="no" value="#arguments.notify_client_services_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_notify_requestor_flag" null="no" value="#arguments.notify_requestor_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_notification_recipient_list" null="#iif(len(trim(arguments.notification_recipient_list)) gt 0,de('no'),de('yes'))#" value="#arguments.notification_recipient_list#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_ui_validation_rule" access="public" returntype="struct" output="no">
		<cfargument name="adj_ui_validation_rule_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>
		<cfstoredproc procedure="adjustment_api.delete_ui_validation_rule" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_ui_validation_rule_id" null="no" value="#arguments.adj_ui_validation_rule_id#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="edit_ui_validation_rule" access="public" returntype="struct" output="no">
		<cfargument name="adj_ui_validation_rule_id" type="numeric" required="yes"/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="rule_name" type="string" required="yes"/>
		<cfargument name="rule_sql" type="any" required="no" default=""/>
		<cfargument name="rule_violation_message" type="string" required="no" default=""/>
		<cfargument name="active_flag" type="numeric" required="yes"/>
		<cfargument name="warning_only_flag" type="numeric" required="yes"/>
		<cfargument name="notification_email_flag" type="numeric" required="yes"/>
		<cfargument name="notify_client_services_flag" type="numeric" required="yes"/>
		<cfargument name="notify_requestor_flag" type="numeric" required="yes"/>
		<cfargument name="notification_recipient_list" type="string" required="no" default=""/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.edit_ui_validation_rule" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_ui_validation_rule_id" null="no" value="#arguments.adj_ui_validation_rule_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_name" null="no" value="#arguments.rule_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_clob" dbvarname=":p_rule_sql" null="#iif(len(trim(arguments.rule_sql)) gt 0,de('no'),de('yes'))#" value="#arguments.rule_sql#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_rule_violation_message" null="#iif(len(trim(arguments.rule_violation_message)) gt 0,de('no'),de('yes'))#" value="#arguments.rule_violation_message#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_active_flag" null="no" value="#arguments.active_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_warning_only_flag" null="no" value="#arguments.warning_only_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_notification_email_flag" null="no" value="#arguments.notification_email_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_notify_client_services_flag" null="no" value="#arguments.notify_client_services_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_notify_requestor_flag" null="no" value="#arguments.notify_requestor_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_notification_recipient_list" null="#iif(len(trim(arguments.notification_recipient_list)) gt 0,de('no'),de('yes'))#" value="#arguments.notification_recipient_list#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>


	<cffunction name="validate_adjustment" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_instruction_id" type="numeric" required="yes"/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>
		<cfstoredproc procedure="adjustment_api.validate_adjustment" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_instruction_id" null="no" value="#arguments.adjustment_instruction_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="add_adj_type_er_exclusion" access="public" returntype="struct" output="no">
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="employer_id" type="numeric" required="yes"/>
		<cfargument name="active_flag" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.add_adj_type_er_exclusion" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" null="no" value="#arguments.employer_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_active_flag" null="no" value="#arguments.active_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="edit_adj_type_er_exclusion" access="public" returntype="struct" output="no">
		<cfargument name="adj_type_er_exclusion_id" type="numeric" required="yes"/>
		<cfargument name="adjustment_type_id" type="numeric" required="yes"/>
		<cfargument name="employer_id" type="numeric" required="yes"/>
		<cfargument name="active_flag" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.edit_adj_type_er_exclusion" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_type_er_exclusion_id" null="no" value="#arguments.adj_type_er_exclusion_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adjustment_type_id" null="no" value="#arguments.adjustment_type_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_employer_id" null="no" value="#arguments.employer_id#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_active_flag" null="no" value="#arguments.active_flag#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_username" null="no" value="#arguments.username#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>

	<cffunction name="delete_adj_type_er_exclusion" access="public" returntype="struct" output="no">
		<cfargument name="adj_type_er_exclusion_id" type="numeric" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="adjustment_api.delete_adj_type_er_exclusion" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_adj_type_er_exclusion_id" null="no" value="#arguments.adj_type_er_exclusion_id#"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>
</cfcomponent>
