<cfsilent>
<!--- fusebox40.loader.cfmx.cfm --->

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

<cfset myFusebox.version.loader = "4.0.3">
<cflock scope="application" timeout="10" type="EXCLUSIVE">

  <cfscript>
    // initialize the application.fusebox (available to be read by developers but not to be written to)
	fb_.application.fusebox = structNew();
	fb_.application.fusebox.circuits = structNew();
	fb_.application.fusebox.plugins = structNew();
	fb_.application.fusebox.pluginphases = structNew();
	
	// compute the current directory.  This is the same as the 
	// fb_.rootdir variable that gets later, but this variable is needed
	// for ALL requests, not just for the loader.
	fb_.application.fusebox.rootdirectory = getDirectoryFromPath(getCurrentTemplatePath());
	// the file separator for the platform
	fb_.application.fusebox.osdelimiter = left(REreplace(fb_.application.fusebox.rootdirectory, "[^\\/]", "", "all"), 1);
  </cfscript>

	<!--- read the fusebox.xml file --->
	<cfif FileExists("#fb_.application.fusebox.rootdirectory#fusebox.xml.cfm")>
		<cfset fb_.fuseboxXMLfile = "fusebox.xml.cfm">
	<cfelse>
		<cfset fb_.fuseboxXMLfile = "fusebox.xml">
	</cfif>
	<cftry>
		<cffile 
			action="READ" 
			file="#fb_.application.fusebox.rootdirectory##fb_.fuseboxXMLfile#" 
			variable="fb_.FuseboxXMLcode">
		<cfset fb_.application.fusebox.xml = xmlParse(trim(fb_.FuseboxXMLcode))>
		<cfcatch type="application">
			<cfthrow type="fusebox.missingFuseboxXML" message="missing fusebox.xml" detail="The file '#fb_.fuseboxXMLfile#' could not be found.">
		</cfcatch>
		<cfcatch type="any">
			<!--- <cfset structDelete(application, 'fusebox')> --->
			<cfthrow type="fusebox.fuseboxXMLError" message="Error reading fusebox.xml" detail="A problem was encountered while reading the #fb_.fuseboxXMLfile# file. This is usually caused by unmatched XML tags (a &lt;tag&gt; without a &lt;/tag&gt; or without use of the &lt;tag/&gt; short-cut.)">
		</cfcatch>
	</cftry>
	
  
  <cfscript>
    // pull out the character encoding
    fb_.xnParameters = XMLsearch(fb_.application.fusebox.xml, "//parameters/parameter[@name='characterEncoding']");
    if (arrayLen(fb_.xnParameters) AND structKeyExists(fb_.xnParameters[1].xmlAttributes, "value")) {
      fb_.application.fusebox.characterEncoding = fb_.xnParameters[1].xmlAttributes['value'];
    }
    else {
      fb_.application.fusebox.characterEncoding = "UTF-8";
    }
  </cfscript>
  
	<!--- now reload the fusebox.xml file using the known characterEncoding in case anything else in it requires some special encoding --->
	<cffile 
		action="READ" 
		file="#fb_.application.fusebox.rootdirectory##fb_.fuseboxXMLfile#" 
		variable="fb_.FuseboxXMLcode"
		charset="#fb_.application.fusebox.characterEncoding#">
		
	<cfset fb_.application.fusebox.xml = xmlParse(trim(fb_.FuseboxXMLcode))>
  
    <cfscript>
      fb_.application.fusebox.xml = xmlParse(fb_.FuseboxXMLcode);
      // give this memory structure a timestamp
      fb_.application.fusebox.timestamp = Now();

    // parse the "application.fusebox" fusebox parameters properties
    fb_.xnParameters = XMLsearch(fb_.application.fusebox.xml, "//parameters/parameter");
    for (fb_.i = 1; fb_.i LTE arrayLen(fb_.xnParameters); fb_.i = fb_.i + 1) {
      fb_.name = "fb_.application.fusebox.#fb_.xnParameters[fb_.i].xmlAttributes['name']#";
      fb_.value  = fb_.xnParameters[fb_.i].xmlAttributes['value'];
      setVariable(fb_.name, fb_.value);
    }
    </cfscript>
	<cfparam name="fb_.application.fusebox.precedenceFormOrUrl" default="form">
	<cfparam name="fb_.application.fusebox.defaultFuseaction" default="">
	<cfparam name="fb_.application.fusebox.fuseactionVariable" default="fuseaction">
	<cfparam name="fb_.application.fusebox.parseWithComments" default="false">
	<cfparam name="fb_.application.fusebox.ignoreBadGrammar" default="true">

	<cfparam name="fb_.application.fusebox.password" default="">
	<cfparam name="fb_.application.fusebox.mode" default="production">
	<cfparam name="fb_.application.fusebox.scriptlanguage" default="cfmx">
	<cfparam name="fb_.application.fusebox.scriptFileDelimiter" default="cfm">
	<cfparam name="fb_.application.fusebox.maskedFileDelimiters" default="htm,cfm,cfml,php,php4,asp,aspx">	

	
	<cfparam name="fb_.application.fusebox.parseWithIndentation" default="#fb_.application.fusebox.parseWithComments#">
  <cfscript>
    // location of parsed files
    fb_.application.fusebox.parsePath = "parsed" & fb_.application.fusebox.osdelimiter;
    
    // location of plugins
    fb_.application.fusebox.pluginsPath = "plugins" & fb_.application.fusebox.osdelimiter;
    
    //parse the global fuseactions, both preprocess and postprocess
    fb_.xnPreprocessFA = XMLsearch(fb_.application.fusebox.xml, "//globalfuseactions/preprocess");
    fb_.application.fusebox.globalfuseactions.preprocess.xml = fb_.xnPreprocessFA[1];
    fb_.xnPostprocessFA = XMLsearch(fb_.application.fusebox.xml, "//globalfuseactions/postprocess");
    fb_.application.fusebox.globalfuseactions.postprocess.xml = fb_.xnPostprocessFA[1];
    
    // parse the circuit definitions
    fb_.xnCircuits = XMLsearch(fb_.application.fusebox.xml, "//circuits/circuit");
  </cfscript>
  
	<cfloop from="1" to="#arrayLen(fb_.xnCircuits)#" index="fb_.i">
    <cfscript>
      fb_.path  = fb_.xnCircuits[fb_.i].xmlAttributes['path'];
      fb_.parent = fb_.xnCircuits[fb_.i].xmlAttributes['parent'];
      fb_.alias = fb_.xnCircuits[fb_.i].xmlAttributes['alias'];
      fb_.application.fusebox.circuits['#fb_.alias#'] = structNew();
      
      setVariable("fb_.application.fusebox.circuits['#fb_.alias#']['path']", fb_.path);
      setVariable("fb_.application.fusebox.circuits['#fb_.alias#']['parent']", fb_.parent);
      
      fb_.rootpath = "";
      fb_.rootdir = GetDirectoryFromPath(GetCurrentTemplatePath());
      
      fb_.aDirs = ListToArray(fb_.path,"/");
      for (fb_.j = 1; fb_.j LTE arrayLen(fb_.aDirs); fb_.j = fb_.j + 1) {
        if (fb_.aDirs[fb_.j] EQ "..") {
          fb_.rootpath = listPrepend(fb_.rootpath, ListLast(fb_.rootdir, "/"), "/");
          fb_.rootdir = ListDeleteAt(fb_.rootdir, ListLen(fb_.rootdir), "\/");
        }
        else {
          fb_.rootpath = listPrepend(fb_.rootpath, "..", "/");
        }
      }
      if (Len(fb_.rootpath)) {
        fb_.rootpath = fb_.rootpath & "/";
      }
      setVariable("fb_.application.fusebox.circuits['#fb_.alias#']['rootpath']", fb_.rootpath);
    </cfscript>
	
		<cfif FileExists("#fb_.application.fusebox.rootdirectory##REreplace(fb_.application.fusebox.circuits[fb_.alias]['path'], '\\/', fb_.application.fusebox.osdelimiter, 'all')#circuit.xml.cfm")>
			<cfset fb_.circuitXMLfile = "circuit.xml.cfm">
		<cfelse>
			<cfset fb_.circuitXMLfile = "circuit.xml">
		</cfif>

		<cftry>
      	<cffile	action="READ" 
			file="#fb_.application.fusebox.rootdirectory##REreplace(fb_.application.fusebox.circuits[fb_.alias]['path'], '\\/', fb_.application.fusebox.osdelimiter, 'all')##fb_.circuitXMLfile#" 
			variable="fb_.CircuitXML"
			charset="#fb_.application.fusebox.characterEncoding#">
		<cfset setVariable("fb_.application.fusebox.circuits['#fb_.alias#']['xml']", xmlParse(trim(fb_.CircuitXML)))>

			<cfcatch type="application">
				<cfthrow type="fusebox.missingCircuitXML" message="missing circuit.xml" detail="The circuit xml file, #fb_.circuitXMLfile#, for circuit #fb_.alias# could not be found.">
			</cfcatch>
			<cfcatch type="any">
				<cfthrow type="fusebox.circuitXMLError" message="Error reading circuit.xml" detail="A problem was encountered while reading the circuit file #fb_.circuitXMLfile# for circuit #fb_.alias#. This is usually caused by unmatched XML tag-pairs. Close all XML tags explicitly or use the / (slash) short-cut.">
			</cfcatch>
		</cftry>

	</cfloop>
	
  <cfscript>
    // loop over all circuits to determine each circuit's "circuitTrace"
    for (fb_.aCircuit in fb_.application.fusebox.circuits) {
      fb_.application.fusebox.circuits[fb_.aCircuit]['circuitTrace'] = arrayNew(1);
      arrayAppend(fb_.application.fusebox.circuits[fb_.aCircuit]['circuitTrace'], fb_.aCircuit);
      fb_.thisCircuit = fb_.application.fusebox.circuits[fb_.aCircuit]['parent'];
      while (len(trim(fb_.thisCircuit))) {
        arrayAppend(fb_.application.fusebox.circuits[fb_.aCircuit]['circuitTrace'], fb_.thisCircuit);
        fb_.thisCircuit = fb_.application.fusebox.circuits[fb_.thisCircuit]['parent'];
      }
    }
    
    // loop over all circuits to determine its attributes and its fuseactions
    for (fb_.aCircuit in fb_.application.fusebox.circuits) {
      fb_.xnCircuit = xmlSearch(fb_.application.fusebox.circuits[fb_.aCircuit]['xml'], "//circuit");
      
      // determine the circuit's access modifier
      if (structKeyExists(fb_.xnCircuit[1].xmlAttributes, 'access')) {
        fb_.application.fusebox.circuits[fb_.aCircuit]['access'] = fb_.xnCircuit[1].xmlAttributes['access'];
      }
      else {
      // by default, a circuit's access modifier is "internal" (accessible anywhere from inside the app but not from outside)
			// note: this is important since any of a circuit's fuseactions who do not have an access modifier will inherit the access modifier of its circuit
        fb_.application.fusebox.circuits[fb_.aCircuit]['access'] = "internal";
      }
      
      // determine the circuit's permissions
      if (structKeyExists(fb_.xnCircuit[1].xmlAttributes, 'permissions')) {
        fb_.application.fusebox.circuits[fb_.aCircuit]['permissions'] = fb_.xnCircuit[1].xmlAttributes['permissions'];
      }
      else {
        fb_.application.fusebox.circuits[fb_.aCircuit]['permissions'] = "";
      }
      
      // determine all the circuit's fuseactions, prefuseactions, and postfuseactions
      fb_.application.fusebox.circuits[fb_.aCircuit].fuseactions = structNew();
	  fb_.application.fusebox.circuits[fb_.aCircuit].prefuseaction = structNew();
	  fb_.application.fusebox.circuits[fb_.aCircuit].postfuseaction = structNew();

	  fb_.application.fusebox.circuits[fb_.aCircuit].prefuseaction.xml = arrayNew(1);
	  fb_.application.fusebox.circuits[fb_.aCircuit].postfuseaction.xml = arrayNew(1);

	  fb_.application.fusebox.circuits[fb_.aCircuit].prefuseaction.callsuper = false;
	  fb_.application.fusebox.circuits[fb_.aCircuit].postfuseaction.callsuper = false;
      
      for (fb_.i = 1; fb_.i LTE arrayLen(fb_.xnCircuit[1].xmlChildren); fb_.i = fb_.i + 1) {
        /* the fuseactions */
        if (fb_.xnCircuit[1].xmlChildren[fb_.i].xmlName EQ "fuseaction") {
          fb_.name = fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes['name'];
          fb_.application.fusebox.circuits[fb_.aCircuit].fuseactions[fb_.name] = structNew();
          fb_.application.fusebox.circuits[fb_.aCircuit].fuseactions[fb_.name].xml = fb_.xnCircuit[1].xmlChildren[fb_.i];
          
          // determine the fuseaction's access modifier
          if (structKeyExists(fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes, 'access')) {
            fb_.application.fusebox.circuits[fb_.aCircuit].fuseactions[fb_.name].access = fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes.access;
          }
          else {
            // by default, a fuseaction has no access modifier then it inherits that of its parent
            fb_.application.fusebox.circuits[fb_.aCircuit].fuseactions[fb_.name].access = fb_.application.fusebox.circuits[fb_.aCircuit].access;
          }
          
          // determine the fuseaction's permissions
          if (structKeyExists(fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes, 'permissions')) {
            fb_.application.fusebox.circuits[fb_.aCircuit].fuseactions[fb_.name].permissions = fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes.permissions;
          }
          else {
            // by default, a fuseaction's permissions is the empty string
            fb_.application.fusebox.circuits[fb_.aCircuit].fuseactions[fb_.name].permissions = "";
          }                    
        }
        /* the prefuseactions */
        else if (fb_.xnCircuit[1].xmlChildren[fb_.i].xmlName EQ "prefuseaction") {
          if (arrayLen(fb_.xnCircuit[1].xmlChildren[fb_.i].xmlChildren)) {
            fb_.application.fusebox.circuits[fb_.aCircuit].prefuseaction.xml = fb_.xnCircuit[1].xmlChildren[fb_.i];
          }
          if ((StructKeyExists(fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes, 'callsuper')) AND
              (fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes.callsuper EQ "true")){
            fb_.application.fusebox.circuits[fb_.aCircuit].prefuseaction.callsuper = true;
          }
        }
        /* the postfuseactions */
        else if (fb_.xnCircuit[1].xmlChildren[fb_.i].xmlName EQ "postfuseaction") {
          if (arrayLen(fb_.xnCircuit[1].xmlChildren[fb_.i].xmlChildren)) {
            fb_.application.fusebox.circuits[fb_.aCircuit].postfuseaction.xml = fb_.xnCircuit[1].xmlChildren[fb_.i];
          }
          if ((StructKeyExists(fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes, 'callsuper')) AND
              (fb_.xnCircuit[1].xmlChildren[fb_.i].xmlAttributes.callsuper EQ "true")) {
            fb_.application.fusebox.circuits[fb_.aCircuit].postfuseaction.callsuper = true;
          }
        }
      }
    }
    
    /* determine application.fusebox.parseRootPath, the inverse path of application.fusebox.parsePath */
    fb_.application.fusebox.parseRootPath = "";
    fb_.rootdir = Replace(GetDirectoryFromPath(getCurrentTemplatePath()), '\', fb_.application.fusebox.osdelimiter, 'all');
    fb_.aDirs = ListToArray(fb_.application.fusebox.parsePath,fb_.application.fusebox.osdelimiter);
    for (fb_.i = 1; fb_.i LTE arrayLen(fb_.aDirs); fb_.i = fb_.i + 1) {
      if (fb_.aDirs[fb_.i] EQ "..") {
        fb_.application.fusebox.parseRootPath = listPrepend(fb_.application.fusebox.parseRootPath, ListLast(fb_.rootdir, fb_.application.fusebox.osdelimiter), fb_.application.fusebox.osdelimiter);
        fb_.rootdir = ListDeleteAt(fb_.rootdir, ListLen(fb_.rootdir), fb_.application.fusebox.osdelimiter);
      }
      else {
        fb_.application.fusebox.parseRootPath = listPrepend(fb_.application.fusebox.parseRootPath, "..", fb_.application.fusebox.osdelimiter);
      }
    }
    
    if (Len(fb_.application.fusebox.parseRootPath)) {
      fb_.application.fusebox.parseRootPath = fb_.application.fusebox.parseRootPath & fb_.application.fusebox.osdelimiter;
    }
    
    /*  parse the plugins 
        sometimes we'll need to refer to the plugins by Name and sometimes by Phase
     */
    fb_.xnPluginPhases = XMLsearch(fb_.application.fusebox.xml, "//plugins/phase");
    
    // loop over all the plugin phases
    for (fb_.i = 1; fb_.i LTE arrayLen(fb_.xnPluginPhases); fb_.i = fb_.i + 1) {
      fb_.phase = fb_.xnPluginPhases[fb_.i].xmlAttributes['name'];
      fb_.application.fusebox.pluginphases[fb_.phase] = arrayNew(1);
      fb_.xnPlugins = xmlSearch(fb_.application.fusebox.xml, "//plugins/phase[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='#lcase(fb_.phase)#']/plugin");
      
      // loop over all the plugins for a given phase
      for (fb_.j = 1; fb_.j LTE arrayLen(fb_.xnPlugins); fb_.j = fb_.j + 1) {
        fb_.name = fb_.xnPlugins[fb_.j].xmlAttributes['name'];
        fb_.template = fb_.xnPlugins[fb_.j].xmlAttributes['template'];
        fb_.path = fb_.application.fusebox.pluginsPath;
        if (structKeyExists(fb_.xnPlugins[fb_.j].xmlAttributes, 'path')) {
          fb_.path = fb_.path & fb_.xnPlugins[fb_.j].xmlAttributes['path'];
        }
        
        if (NOT structKeyExists(fb_.application.fusebox.plugins, fb_.name)) {
          fb_.application.fusebox.plugins[fb_.name] = structNew();
        }
        fb_.application.fusebox.plugins[fb_.name][fb_.phase] = structNew();
        
        fb_.rootpath = "";
        fb_.rootdir = getDirectoryFromPath(getCurrentTemplatePath());
        fb_.aDirs = ListToArray(fb_.path,"/");
        for (fb_.k = 1; fb_.k LTE arrayLen(fb_.aDirs); fb_.k = fb_.k + 1) {
          if (fb_.aDirs[fb_.k] EQ "..") {
            fb_.rootpath = listPrepend(fb_.rootpath, ListLast(fb_.rootdir, "/"), "/");
            fb_.rootdir = listDeleteAt(fb_.rootdir, ListLen(fb_.rootdir), "/");
          }
          else {
            fb_.rootpath = listPrepend(fb_.rootpath, "..", "/");
          }
        }
        
        if (Len(fb_.rootpath)) {
          fb_.rootpath = fb_.rootpath & "/";
        }
        setVariable("fb_.application.fusebox.plugins['#fb_.name#']['#fb_.phase#'].path", fb_.path);
        setVariable("fb_.application.fusebox.plugins['#fb_.name#']['#fb_.phase#'].template", fb_.template);
        setVariable("fb_.application.fusebox.plugins['#fb_.name#']['#fb_.phase#'].rootpath", fb_.rootpath);
        
        fb_.application.fusebox.pluginphases[fb_.phase][fb_.j] = structNew();
        setVariable("fb_.application.fusebox.pluginphases['#fb_.phase#'][#fb_.j#].name", fb_.name);
        setVariable("fb_.application.fusebox.pluginphases['#fb_.phase#'][#fb_.j#].path", fb_.path);
        setVariable("fb_.application.fusebox.pluginphases['#fb_.phase#'][#fb_.j#].template", fb_.template);
        setVariable("fb_.application.fusebox.pluginphases['#fb_.phase#'][#fb_.j#].rootpath", fb_.rootpath);
        setVariable("fb_.application.fusebox.pluginphases['#fb_.phase#'][#fb_.j#].parameters", fb_.xnPlugins[fb_.j].xmlChildren);
      }
    }
  </cfscript>
  
  <cfscript>
	  // now, finally, copy the entire fb_.application.fusebox structure to the application.fusebox structure
	  application.fusebox = duplicate(fb_.application.fusebox);
  </cfscript>

</cflock>
</cfsilent>
