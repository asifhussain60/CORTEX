<cfcomponent>
	<cffunction name="msg_template_search_results" access="public" returntype="struct" output="no">
		<cfargument name="template_name" type="string" required="no" default=""/>
		<cfargument name="event_type" type="string" required="no" default=""/>
		<cfargument name="group_name" type="string" required="no" default=""/>
		<cfargument name="communication_type" type="string" required="no" default=""/>
		<cfargument name="priority" type="string" required="no" default=""/>
		<cfargument name="status" type="string" required="no" default=""/>
		<cfargument name="subject" type="string" required="no" default=""/>
		<cfargument name="srv_title" type="string" required="no" default=""/>
		<cfargument name="email_to" type="string" required="no" default=""/>
		<cfargument name="email_from" type="string" required="no" default=""/>
		<cfargument name="email_cc" type="string" required="no" default=""/>
		<cfargument name="email_reply_to" type="string" required="no" default=""/>
		<cfargument name="email_bcc" type="string" required="no" default=""/>
		<cfargument name="email_sql" type="string" required="no" default=""/>
		<cfset var result = StructNew()/>

		<cfstoredproc procedure="wweb.email_manager_info.msg_template_search_results" datasource="#request.ds#">
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_template_name" null="#iif(len(trim(arguments.template_name)) gt 0,de('no'),de('yes'))#" value="#arguments.template_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_event_type" null="#iif(len(trim(arguments.event_type)) gt 0,de('no'),de('yes'))#" value="#arguments.event_type#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_group_name" null="#iif(len(trim(arguments.group_name)) gt 0,de('no'),de('yes'))#" value="#arguments.group_name#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_communication_type" null="#iif(len(trim(arguments.communication_type)) gt 0,de('no'),de('yes'))#" value="#arguments.communication_type#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_priority" null="#iif(len(trim(arguments.priority)) gt 0,de('no'),de('yes'))#" value="#arguments.priority#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_status" null="#iif(len(trim(arguments.status)) gt 0,de('no'),de('yes'))#" value="#arguments.status#"/>
 			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_subject" null="#iif(len(trim(arguments.subject)) gt 0,de('no'),de('yes'))#" value="#arguments.subject#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_srv_title" null="#iif(len(trim(arguments.srv_title)) gt 0,de('no'),de('yes'))#" value="#arguments.srv_title#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_email_to" null="#iif(len(trim(arguments.email_to)) gt 0,de('no'),de('yes'))#" value="#arguments.email_to#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_email_from" null="#iif(len(trim(arguments.email_from)) gt 0,de('no'),de('yes'))#" value="#arguments.email_from#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_email_cc" null="#iif(len(trim(arguments.email_cc)) gt 0,de('no'),de('yes'))#" value="#arguments.email_cc#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_email_reply_to" null="#iif(len(trim(arguments.email_reply_to)) gt 0,de('no'),de('yes'))#" value="#arguments.email_reply_to#"/>	
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_email_bcc" null="#iif(len(trim(arguments.email_bcc)) gt 0,de('no'),de('yes'))#" value="#arguments.email_bcc#"/>
			<cfprocparam type="in" cfsqltype="cf_sql_varchar" dbvarname=":p_email_sql" null="#iif(len(trim(arguments.email_sql)) gt 0,de('no'),de('yes'))#" value="#arguments.email_sql#"/>

			<cfprocresult name="result.cur_active_templates" resultset="1"/>
			<cfprocresult name="result.cur_pending_templates" resultset="2"/>
			<cfprocparam type="out" cfsqltype="cf_sql_numeric" dbvarname=":p_success_flag" variable="result.success_flag" null="no"/>
			<cfprocparam type="out" cfsqltype="cf_sql_varchar" dbvarname=":p_process_message" variable="result.process_message" null="no"/>
		</cfstoredproc>
		<cfreturn result/>
	</cffunction>
</cfcomponent>
