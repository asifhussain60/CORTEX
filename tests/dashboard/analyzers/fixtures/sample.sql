-- Users table
CREATE TABLE dbo.Users (
    UserId INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(100) NOT NULL UNIQUE,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    FirstName NVARCHAR(100),
    LastName NVARCHAR(100),
    PasswordHash VARBINARY(64) NOT NULL,
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT CHK_Email CHECK (Email LIKE '%@%.%')
);

-- Roles table
CREATE TABLE dbo.Roles (
    RoleId INT PRIMARY KEY IDENTITY(1,1),
    RoleName NVARCHAR(50) NOT NULL UNIQUE,
    Description NVARCHAR(255)
);

-- UserRoles junction table
CREATE TABLE dbo.UserRoles (
    UserId INT NOT NULL,
    RoleId INT NOT NULL,
    AssignedDate DATETIME DEFAULT GETDATE(),
    PRIMARY KEY (UserId, RoleId),
    CONSTRAINT FK_UserRoles_Users FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId),
    CONSTRAINT FK_UserRoles_Roles FOREIGN KEY (RoleId) REFERENCES dbo.Roles(RoleId)
);

-- Indexes
CREATE NONCLUSTERED INDEX IX_Users_Email ON dbo.Users(Email);
CREATE NONCLUSTERED INDEX IX_Users_Username ON dbo.Users(Username);
CREATE UNIQUE NONCLUSTERED INDEX IX_Users_Active_Username ON dbo.Users(Username) WHERE IsActive = 1;

-- View for active users
CREATE VIEW dbo.vw_ActiveUsers
AS
SELECT 
    u.UserId,
    u.Username,
    u.Email,
    u.FirstName + ' ' + u.LastName AS FullName,
    u.CreatedDate
FROM dbo.Users u
WHERE u.IsActive = 1;
GO

-- Stored procedure to get user by ID
CREATE PROCEDURE dbo.sp_GetUserById
    @UserId INT
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        SELECT 
            UserId,
            Username,
            Email,
            FirstName,
            LastName,
            IsActive,
            CreatedDate
        FROM dbo.Users
        WHERE UserId = @UserId;
        
        -- Get user roles
        SELECT 
            r.RoleId,
            r.RoleName,
            r.Description
        FROM dbo.Roles r
        INNER JOIN dbo.UserRoles ur ON r.RoleId = ur.RoleId
        WHERE ur.UserId = @UserId;
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, 1);
    END CATCH
END;
GO

-- Stored procedure to search users
CREATE PROCEDURE dbo.sp_SearchUsers
    @SearchTerm NVARCHAR(100),
    @IncludeInactive BIT = 0
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @SearchTerm IS NULL OR LEN(@SearchTerm) = 0
    BEGIN
        RAISERROR('Search term cannot be empty', 16, 1);
        RETURN;
    END
    
    SELECT 
        UserId,
        Username,
        Email,
        FirstName,
        LastName,
        IsActive
    FROM dbo.Users
    WHERE (
        Username LIKE '%' + @SearchTerm + '%'
        OR Email LIKE '%' + @SearchTerm + '%'
        OR FirstName LIKE '%' + @SearchTerm + '%'
        OR LastName LIKE '%' + @SearchTerm + '%'
    )
    AND (@IncludeInactive = 1 OR IsActive = 1)
    ORDER BY Username;
END;
GO

-- Function to get user count
CREATE FUNCTION dbo.fn_GetUserCount(@IsActive BIT)
RETURNS INT
AS
BEGIN
    DECLARE @Count INT;
    
    SELECT @Count = COUNT(*)
    FROM dbo.Users
    WHERE IsActive = @IsActive;
    
    RETURN @Count;
END;
GO

-- Function to get active users (table-valued)
CREATE FUNCTION dbo.fn_GetActiveUsersCreatedAfter(@Date DATETIME)
RETURNS TABLE
AS
RETURN (
    SELECT 
        UserId,
        Username,
        Email,
        CreatedDate
    FROM dbo.Users
    WHERE IsActive = 1
    AND CreatedDate >= @Date
);
GO

-- Trigger for audit trail
CREATE TRIGGER dbo.tr_Users_Audit
ON dbo.Users
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @Action CHAR(1);
    
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        SET @Action = 'U'; -- Update
    ELSE IF EXISTS(SELECT * FROM inserted)
        SET @Action = 'I'; -- Insert
    ELSE
        SET @Action = 'D'; -- Delete
    
    -- Create temp table for audit
    CREATE TABLE #AuditTemp (
        UserId INT,
        Action CHAR(1),
        ModifiedDate DATETIME
    );
    
    INSERT INTO #AuditTemp (UserId, Action, ModifiedDate)
    SELECT 
        COALESCE(i.UserId, d.UserId),
        @Action,
        GETDATE()
    FROM inserted i
    FULL OUTER JOIN deleted d ON i.UserId = d.UserId;
    
    DROP TABLE #AuditTemp;
END;
GO
