<cfcomponent name="UserService" extends="BaseService" persistent="true" table="users" accessors="true">
    
    <cfproperty name="userId" type="numeric" fieldtype="id" generator="identity">
    <cfproperty name="username" type="string" required="true">
    <cfproperty name="email" type="string" required="true">
    <cfproperty name="firstName" type="string">
    <cfproperty name="lastName" type="string">
    <cfproperty name="isActive" type="boolean" default="true">
    <cfproperty name="createdDate" type="date" ormtype="timestamp">
    
    <cffunction name="init" access="public" returntype="UserService">
        <cfreturn this>
    </cffunction>
    
    <cffunction name="getUser" access="public" returntype="query">
        <cfargument name="userId" type="numeric" required="true">
        
        <cfquery name="qUser" datasource="mydb">
            SELECT userId, username, email, firstName, lastName, isActive, createdDate
            FROM users
            WHERE userId = <cfqueryparam value="#arguments.userId#" cfsqltype="cf_sql_integer">
            AND isActive = 1
        </cfquery>
        
        <cfreturn qUser>
    </cffunction>
    
    <cffunction name="searchUsers" access="public" returntype="query">
        <cfargument name="searchTerm" type="string" required="true">
        
        <cfquery name="qUsers" datasource="mydb">
            SELECT userId, username, email, firstName, lastName
            FROM users
            WHERE (
                username LIKE <cfqueryparam value="%#arguments.searchTerm#%" cfsqltype="cf_sql_varchar">
                OR email LIKE <cfqueryparam value="%#arguments.searchTerm#%" cfsqltype="cf_sql_varchar">
            )
            AND isActive = 1
            ORDER BY username
        </cfquery>
        
        <cfreturn qUsers>
    </cffunction>
    
    <cffunction name="createUser" access="public" returntype="numeric">
        <cfargument name="username" type="string" required="true">
        <cfargument name="email" type="string" required="true">
        
        <cfset var newUserId = 0>
        
        <cfquery name="qInsert" datasource="mydb" result="insertResult">
            INSERT INTO users (username, email, createdDate)
            VALUES (
                <cfqueryparam value="#arguments.username#" cfsqltype="cf_sql_varchar">,
                <cfqueryparam value="#arguments.email#" cfsqltype="cf_sql_varchar">,
                <cfqueryparam value="#now()#" cfsqltype="cf_sql_timestamp">
            )
        </cfquery>
        
        <cfset newUserId = insertResult.generatedKey>
        
        <cfif newUserId GT 0>
            <cfinvoke method="sendWelcomeEmail" username="#arguments.username#" email="#arguments.email#">
        </cfif>
        
        <cfreturn newUserId>
    </cffunction>
    
    <cffunction name="sendWelcomeEmail" access="private" returntype="void">
        <cfargument name="username" type="string" required="true">
        <cfargument name="email" type="string" required="true">
        
        <cfmail to="#arguments.email#" 
                from="noreply@example.com" 
                subject="Welcome to Our Application"
                type="html">
            <h1>Welcome, #arguments.username#!</h1>
            <p>Thank you for registering with our application.</p>
            <p>Your account has been created successfully.</p>
        </cfmail>
    </cffunction>
    
    <cffunction name="deleteUser" access="public" returntype="boolean">
        <cfargument name="userId" type="numeric" required="true">
        
        <cfquery datasource="mydb">
            UPDATE users
            SET isActive = 0
            WHERE userId = <cfqueryparam value="#arguments.userId#" cfsqltype="cf_sql_integer">
        </cfquery>
        
        <cfreturn true>
    </cffunction>
    
</cfcomponent>

<cfinclude template="common/header.cfm">
<cfinclude template="common/navigation.cfm">
