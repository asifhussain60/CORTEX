<cfsilent>
<!--- fusebox40.runtime.cfmx.cfm --->

<!---
Fusebox Software License
Version 1.0

Copyright (c) 2003 The Fusebox Corporation. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form or otherwise encrypted form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. The end-user documentation included with the redistribution, if any, must include the following acknowledgment:

"This product includes software developed by the Fusebox Corporation (http://www.fusebox.org/)."

Alternately, this acknowledgment may appear in the software itself, if and wherever such third-party acknowledgments normally appear.

4. The names "Fusebox" and "Fusebox Corporation" must not be used to endorse or promote products derived from this software without prior written (non-electronic) permission. For written permission, please contact fusebox@fusebox.org.

5. Products derived from this software may not be called "Fusebox", nor may "Fusebox" appear in their name, without prior written (non-electronic) permission of the Fusebox Corporation. For written permission, please contact fusebox@fusebox.org.

If one or more of the above conditions are violated, then this license is immediately revoked and can be re-instated only upon prior written authorization of the Fusebox Corporation.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE FUSEBOX CORPORATION OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

-------------------------------------------------------------------------------

This software consists of voluntary contributions made by many individuals on behalf of the Fusebox Corporation. For more information on Fusebox, please see <http://www.fusebox.org/>.

--->

<cfscript>
  // copy all FORM and URL variables to ATTRIBUTES scope
  // here, FORM has precendence although this can be over-written later depending on the application's fusebox.xml setting.
  if (NOT IsDefined("attributes"))
    attributes=structNew();
  StructAppend(attributes, url, "yes");
  StructAppend(attributes, form, "yes");
  
  // initialize the fusebox "working" structure (only for internal use of the core file(s) -- considered hands-off to developers
  fb_ = structNew();
  fb_.fuseQ = ArrayNew(1);
  
  // initialize the myFusebox structure which is specific to a given request (can be read by the developer (and written to if creating plugins)
  myFusebox = structNew();
  myFusebox.version.runtime     = "unknown";
  myFusebox.version.loader      = "unknown";
  myFusebox.version.transformer = "unknown";
  myFusebox.version.parser      = "unknown";
  
  myFusebox.version.runtime     = "4.0.3";
  
  myFusebox.thisCircuit = "";
  myFusebox.thisFuseaction =  "";
  myFusebox.thisPlugin = "";
  myFusebox.thisPhase = "";
  myFusebox.plugins = structNew();
  myFusebox.parameters = structNew();
  
  myFusebox.parameters.load = true;
  myFusebox.parameters.parse = true;
  myFusebox.parameters.execute = true;
  
  // default myFusebox.parameters depending on "mode" of the application set in fusebox.xml
  if (IsDefined("application.fusebox") AND IsDefined("application.fusebox.mode")) {
    if (application.fusebox.mode EQ "development") {
      myFusebox.parameters.load = true;
		  myFusebox.parameters.parse = true;
		  myFusebox.parameters.execute = true;
    }
    if (application.fusebox.mode EQ "production") {
      myFusebox.parameters.load = false;
		  myFusebox.parameters.parse = false;
		  myFusebox.parameters.execute = true;
    }
  }
</cfscript>

<!--- did the user pass in any special "fuseboxDOT" parameters for this request? --->
<!--- If so, process them --->
<!--- note: only if attributes.fusebox.password matches the application password --->
<cfparam name="attributes['fusebox.password']" default="">
<cfscript>
  if (IsDefined("application.fusebox.password") AND application.fusebox.password EQ attributes['fusebox.password']) {
    if (StructKeyExists(attributes, 'fusebox.load') and IsBoolean(attributes['fusebox.load'])) {
      myFusebox.parameters.load = attributes['fusebox.load'];
    }
    if (StructKeyExists(attributes, 'fusebox.parse') and IsBoolean(attributes['fusebox.parse'])) {
      myFusebox.parameters.parse = attributes['fusebox.parse'];
    }
    if (StructKeyExists(attributes, 'fusebox.execute') and IsBoolean(attributes['fusebox.execute'])) {
      myFusebox.parameters.execute = attributes['fusebox.execute'];
    }
  }
  
  // if application.fusebox doesn't already exist we definitely want to reload
  if (NOT IsDefined("application.fusebox")) {
    myFusebox.parameters.load = true;
  }
</cfscript>

<!--- if necessary, call the fusebox40.loader --->
<cfif myFusebox.parameters.load>
	<cfinclude template="fusebox40.loader.cfmx.cfm">
</cfif>

<cfscript>
  // make sure the correct structures are set up for myFusebox.plugins.{plugin-name} and any potential parameters it might have
  for (fb_.aPlugin in application.fusebox.plugins) {
    myFusebox.plugins[fb_.aPlugin] = structNew();
  }
  
  // does this app give higher precedence to URL scope over FORM scope? If so, adjust
  if (application.fusebox.precedenceFormOrURL EQ "URL") {
    StructAppend(attributes, url, "yes");
  }
  
  // how about a default fuseaction?
  if (NOT IsDefined('attributes.#application.fusebox.fuseactionVariable#')) {
    "attributes.#application.fusebox.fuseactionVariable#" = application.fusebox.defaultFuseaction;
  }
  
  // copy the value of the fuseactionVariable into the variable "attributes.fuseaction" for standardization
  attributes.fuseaction = Evaluate('attributes.#application.fusebox.fuseactionVariable#');
</cfscript>

<!--- set the myFusebox.originalCircuit, myFusebox.originalFuseaction --->
<cfif ListLen(attributes.fuseaction, '.') EQ 2>
  <cfscript>
    myFusebox.thisCircuit    = ListFirst(attributes.fuseaction, '.');
    myFusebox.thisFuseaction = ListLast(attributes.fuseaction, '.');
	myFusebox.originalCircuit    = myFusebox.thisCircuit;
	myFusebox.originalFuseaction = myFusebox.thisFuseaction;
  </cfscript>
<cfelse>
	<cfthrow type="fusebox.malformedFuseaction" message="malformed Fuseaction" detail="You specified a malformed Fuseaction of #attributes.fuseaction#.  A fully qualified Fuseaction must be in the form [Circuit].[Fuseaction].">	
</cfif>

<!--- if the circuit specified by myFusebox.originalCircuit does not exist throw an error --->
<!--- if the fuseaction specified by myFusebox.originalFuseaction does not exist throw an error --->

<cfif NOT IsDefined("application.fusebox.circuits.#myFusebox.originalCircuit#")>
	<cfthrow type="fusebox.undefinedCircuit" message="undefined Circuit" detail="You specified a Circuit of #myFusebox.originalCircuit# which is not defined.">
<cfelse>
	<cfif NOT IsDefined("application.fusebox.circuits.#myFusebox.originalCircuit#.fuseactions.#myFusebox.originalFuseaction#")>
		<cfthrow type="fusebox.undefinedFuseaction" message="undefined Fuseaction" detail="You specified a Fuseaction of #myFusebox.originalFuseaction# which is not defined in Circuit #myFusebox.originalCircuit#.">
	</cfif>
</cfif>

<!--- ensure that the fuseaction has access="public" --->
<!---<cfset fb_.xnAccess = xmlSearch(CircuitXML, "//circuit/fuseaction[@name='#fuseaction#']")>--->
<!--- <cfset fb_.xnAccess = xmlSearch(fb_.CircuitXML, "//circuit/fuseaction[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='#lcase(myFusebox.thisFuseaction)#']")> --->
<cfif application.fusebox.circuits[myFusebox.originalCircuit].fuseactions[myFusebox.thisFuseaction].access NEQ "public">
	<cfthrow type="fusebox.AccessModifier" message="Invalid Access Modifier" detail="You tried to access #myFusebox.originalCircuit#.#myFusebox.originalFuseaction# which does not have access modifier of public. A Fuseaction which is to be accessed from anywhere outside the application (such as called via an URL, or a FORM, or as a web service) must have an access modifier of public or if unspecified at least inherit such a modifier from its circuit.">
</cfif>

<!--- here is the file to be parsed --->
<cfset fb_.file2Parse = trim("#application.fusebox.parsePath#" & lcase("parsed.#myFusebox.originalCircuit#.#myFusebox.originalFuseaction#.#application.fusebox.scriptFileDelimiter#"))>

<!--- if the file doesn't exist or if it is to be re-parsed then re-parse it by calling the Transformer and Parser --->
<cfif myFusebox.parameters.parse OR NOT FileExists(application.fusebox.rootdirectory & fb_.file2Parse)>

	<cfoutput>
	<!--- call the Transformer --->
	<cfinclude template="fusebox40.transformer.#application.fusebox.scriptlanguage#.cfm">
	<!--- call the Parser --->
	<cfinclude template="fusebox40.parser.#application.fusebox.scriptlanguage#.cfm">
	</cfoutput>

	<cflock name="#application.fusebox.rootdirectory##fb_.file2Parse#" timeout="30" type="Exclusive">
		<!--- delete the old parsed file --->
		<cfif FileExists(application.fusebox.rootdirectory & fb_.file2Parse)>
			<cftry>
			<cffile action="DELETE" file="#application.fusebox.rootdirectory##fb_.file2Parse#">
			<cfcatch>
			<!--- no comment --->
			</cfcatch>
			</cftry>
		</cfif>
	
		<!--- write out the parsed file --->	
		<cftry>
			<cffile action="WRITE" file="#application.fusebox.rootdirectory##fb_.file2Parse#" output="#fb_.parsedfile#" charset="#application.fusebox.characterEncoding#" mode="660">	
			<cfcatch>
				<cfthrow type="fusebox.errorWritingParsedFile" message="An Error during write of Parsed File or Parsing Directory not found." detail="Attempting to write the parsed file '#fb_.file2Parse#' threw an error. This can also occur if the parsed file directory cannot be found.">
			</cfcatch>
		</cftry>
		
	</cflock>
	
</cfif>

</cfsilent>

<cfprocessingdirective suppresswhitespace="Yes">
<!--- OK, now execute everything --->
<cfif myFusebox.parameters.execute>
<cftry>
<cfinclude template="#fb_.file2Parse#">
<cfcatch type="missingInclude">
	<cfif right(cfcatch.missingFileName, Len(fb_.file2Parse)) EQ 
fb_.file2Parse>
		<cfthrow type="fusebox.missingParsedFile" message="Parsed File or 
Directory not found." detail="Attempting to execute the parsed file 
'#fb_.file2Parse#' threw an error. This can occur if the parsed file does 
not exist in the parsed directory or if the parsed directory itself is 
missing.">
	<cfelse>
		<cfrethrow>
	</cfif>
</cfcatch>
</cftry>
</cfif>
</cfprocessingdirective>


