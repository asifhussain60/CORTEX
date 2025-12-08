<?xml version="1.0" encoding="UTF-8"?>

<fusebox>
	<circuits>
		<circuit alias="m" path="model/" parent=""/>
		<circuit alias="v" path="view/"  parent=""/>
		<circuit alias="main" path="controller/" parent=""/>
		<circuit alias="auto" path="controller/auto/" parent="main"/>
		<circuit alias="control_adjs" path="controller/control_adjustments/" parent="main"/>
		<circuit alias="enter_adjs" path="controller/enter_adjustments/" parent="main"/>
		<circuit alias="maintenance" path="controller/maintenance/" parent="main"/>
		<circuit alias="reports" path="controller/reports/" parent="main"/>
		<circuit alias="research" path="controller/research/" parent="main"/>
		<circuit alias="popups" path="controller/popups/" parent="main"/>
		<circuit alias="security" path="controller/security/" parent="main"/>
		<circuit alias="m_auto" path="model/auto/" parent="m"/>
		<circuit alias="m_control_adjs" path="model/control_adjustments/" parent="m"/>
		<circuit alias="m_enter_adjs" path="model/enter_adjustments/" parent="m"/>
		<circuit alias="m_maintenance" path="model/maintenance/" parent="m"/>
		<circuit alias="m_reports" path="model/reports/" parent="m"/>
		<circuit alias="m_research" path="model/research/" parent="m"/>
		<circuit alias="m_popups" path="model/popups/" parent="m"/>
		<circuit alias="m_security" path="model/security/" parent="m"/>
		<circuit alias="v_auto" path="view/auto/" parent="v"/>
		<circuit alias="v_control_adjs" path="view/control_adjustments/" parent="v"/>
		<circuit alias="v_enter_adjs" path="view/enter_adjustments/" parent="v"/>
		<circuit alias="v_maintenance" path="view/maintenance/" parent="v"/>
		<circuit alias="v_reports" path="view/reports/" parent="v"/>
		<circuit alias="v_research" path="view/research/" parent="v"/>
		<circuit alias="v_popups" path="view/popups/" parent="v"/>
		<circuit alias="v_security" path="view/security/" parent="v"/>
		<circuit alias="v_layouts" path="view/layouts/" parent="v"/>
	</circuits>

	<parameters>
		<parameter name="fuseactionVariable" value="method"/>
		<parameter name="defaultFuseaction" value="main.login"/>
		<parameter name="precedenceFormOrUrl" value="form"/>
		<parameter name="password" value="reinit_ww"/>
		<parameter name="mode" value="production"/>
		<parameter name="parseWithComments" value="true"/>
		<parameter name="scriptlanguage" value="cfmx"/>
		<parameter name="scriptFileDelimiter" value="cfm"/>
		<parameter name="maskedFileDelimiters" value="htm,cfm,cfml,php,php4,asp,aspx"/>
	</parameters>

	<globalfuseactions>
		<preprocess>
			<do action="v.header" contentvariable="header"/>
		</preprocess>
		<postprocess>
			<do action="v_layouts.main_layout"/>
			<set name="request.show_error_msg" value="0"/>
			<set name="url.show_error_msg" value="0"/>
			<set name="attributes.suppress_breadcrumb" value="0"/>
		</postprocess>
	</globalfuseactions>

	<plugins>
		<phase name="preProcess">
			<plugin name="Globals" template="Globals.cfm"/>
		</phase>
		<phase name="preFuseaction">
		</phase>
		<phase name="postFuseaction">
		</phase>
		<phase name="fuseactionException">
			<plugin name="ProcessExceptions" template="ProcessExceptions.cfm"/>
		</phase>
		<phase name="postProcess">
			<plugin name="AppRefresh" template="AppRefresh.cfm"/>
		</phase>
		<phase name="processError">
		</phase>
	</plugins>
</fusebox>