<cfsilent><cfapplication name="Adjustment Manager" sessionmanagement="yes" clientmanagement="yes" sessiontimeout="#createtimespan(0,12,0,0)#" applicationtimeout="#createtimespan(1,0,0,0)#"></cfsilent>
<cfscript>
	if (NOT IsDefined("ATTRIBUTES.EMPLOYEE_ID")) ATTRIBUTES.EMPLOYEE_ID = "0";
	if (NOT IsDefined("ATTRIBUTES.SEARCH_ZIP_CODE")) ATTRIBUTES.SEARCH_ZIP_CODE="";
	if (NOT IsDefined("ATTRIBUTES.OPERATOR_ID")) ATTRIBUTES.OPERATOR_ID="";
	if (NOT IsDefined("ATTRIBUTES.ELECTION_TYPE")) ATTRIBUTES.ELECTION_TYPE="";
	
</cfscript>
<cftry>
<cfinclude template="fusebox40.runtime.cfmx.cfm">
	<cfcatch type="Any">
		<cfif isDefined("request.environment") AND request.environment IS 'PRD'>
		<cfelse>
			Catch:<br>
			<cfdump var="#cfcatch#"/><br>
		</cfif>
	</cfcatch>
</cftry>
<cfif (cgi.http_host IS NOT 'sd.wageworks.com') AND (cgi.http_host IS NOT 'csd.wageworks.com')>
	<h2>Fusebox Version</h2>
	<cfdump var="#myFusebox.version#">
	<h2>Attributes</h2>
	<cfdump var="#attributes#">
	<h2>Request</h2>
	<cfdump var="#request#">
</cfif>
