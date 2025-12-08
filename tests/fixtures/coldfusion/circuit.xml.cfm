<circuit access="public">
	<fuseaction name="payroll_cycle_details">
		<set name="request.page_title" value="Payroll Cycle Details"/>
		<do action="m_research.employee_information"/>
		<do action="m_research.employee_payroll_cycle_dtls"/>
		<do action="m_research.sony_elig"/>
		<do action="v_auto.payroll_cycle_details" contentvariable="body"/>
		<do action="v.footer" contentvariable="footer"/>
	</fuseaction>
</circuit>
