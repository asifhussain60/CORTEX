<cfcomponent>
	<cffunction name="process_early_claim_reimb" access="public" returntype="struct" output="no">
		<cfargument name="commuter_claim_instr_id" type="numeric" required="yes"/>
		<cfargument name="username" type="string" required="yes"/>
		<cfset var result = StructNew()/>

		<cfstoredproc datasource="#request.ds#" procedure="wweb.pkg_ops_commuter_claims.process_early_claim_reimb">
			<cfprocparam type="in" cfsqltype="cf_sql_numeric" dbvarname=":p_commuter_claim_instr_id" value="#arguments.commuter_claim_instr_id#" null="no">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_last_update_user" value="#arguments.username#" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no">
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no">
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>
</cfcomponent>
