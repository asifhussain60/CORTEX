<cfheader name="X-Frame-Options" value="SAMEORIGIN">
<cfsilent>
<!--- <cfsetting showdebugoutput="no"/> --->
<cfif right(cgi.script_name, Len("index.cfm")) NEQ "index.cfm" AND right(cgi.script_name, 3) NEQ "cfc">
	<cflocation url="index.cfm" addtoken="no">
</cfif>
</cfsilent>