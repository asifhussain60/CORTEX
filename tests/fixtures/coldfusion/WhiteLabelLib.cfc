component displayname="WhiteLabelLib"
{

	function WLValue(employerId, key)
	{
		value = "";
		
		qry = createObject("component", "query");
	
		qry.setName("WLQuery");
	
		qry.setDatasource(request.ds);
		
		sql = "SELECT wweb.cs_content_info.cs_object_get_value( '" & key & "', " & employerId & " ) value FROM dual";
		
		qry.setSql( sql );
	
		result = qry.execute();
		
		obj = result.getResult();
	
		if (obj.RecordCount EQ 1) value = obj.value;
	
		return value; 
	}


	function WLValueSet(employerId)
	{
		valueSet = StructNew();
		
		qry = createObject("component", "query");
	
		qry.setName("WLQuery");
	
		qry.setDatasource(request.ds);
		
		sql = "SELECT " & 
			" key_name, " & 
			" business_name, " & 
			" key_id," & 
			" wweb.cs_content_info.cs_object_get_value(key_name, " & employerId & " ) value " & 
			" FROM wweb.cs_keys";
		
		qry.setSql( sql );
	
		result = qry.execute();
		
		obj = result.getResult();
	
		if (obj.RecordCount NEQ 0) 
		{
			for( ix=1; ix LTE obj.RecordCount; ix = ix + 1)
			{
				valueSet[obj.key_name[ix]]=obj.value[ix];
				valueSet[obj.business_name[ix]]=obj.key_name[ix];
			}
		}
	
		valueSet = valueSet;
	
		return valueSet; 
	}
}