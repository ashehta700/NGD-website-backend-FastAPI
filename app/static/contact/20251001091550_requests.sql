-- Create DB if missing
IF DB_ID('NGD_Website') IS NULL
BEGIN
    CREATE DATABASE NGD_Website;
END
GO

USE NGD_Website;
GO

-- Create schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Requests')
BEGIN
    EXEC('CREATE SCHEMA Requests');
END
GO

-- Lookup: Category (Complains | RequestData | Suggestion)
CREATE TABLE [Requests].[Category](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [Name] NVARCHAR(100) NOT NULL,
    [Name_Ar] NVARCHAR(100) NOT NULL,
    [CreatedAt] DATETIME2(0) DEFAULT SYSUTCDATETIME(),
    [IsDeleted] BIT DEFAULT 0
);
GO

-- Lookup: RequestInformation (multi-select groups like Geography, Geology, ...)
CREATE TABLE [Requests].[RequestInformation](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [Name] NVARCHAR(200) NOT NULL,
    [Name_Ar] NVARCHAR(200) NOT NULL,
    [CreatedAt] DATETIME2(0) DEFAULT SYSUTCDATETIME(),
    [IsDeleted] BIT DEFAULT 0
);
GO

-- Lookup: Format (Vector, Raster, Other and their subtypes can be stored as values)
CREATE TABLE [Requests].[Format](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [Name] NVARCHAR(150) NOT NULL,
	[Type] NVARCHAR(150) NOT NULL,
    [CreatedAt] DATETIME2(0) DEFAULT SYSUTCDATETIME(),
    [IsDeleted] BIT DEFAULT 0
);
GO

-- Lookup: Projection (UTM, ETM, etc)
CREATE TABLE [Requests].[Projection](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [Name] NVARCHAR(100) NOT NULL,
    [CreatedAt] DATETIME2(0) DEFAULT SYSUTCDATETIME()
);
GO

-- Status (In Progress, Responded, Rejected)
CREATE TABLE [Requests].[Status](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [Name] NVARCHAR(50) NOT NULL,
    [Name_Ar] NVARCHAR(50) NULL,
    [CreatedAt] DATETIME2(0) DEFAULT SYSUTCDATETIME()
);
GO

-- NEW: Lookup for Complaint Screens
CREATE TABLE [Requests].[ComplaintScreen](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [Name] NVARCHAR(150) NOT NULL,     -- e.g. User Login
    [Name_Ar] NVARCHAR(150) NOT NULL,  -- e.g. ???? ????? ??????
    [CreatedAt] DATETIME2(0) DEFAULT SYSUTCDATETIME(),
    [IsDeleted] BIT DEFAULT 0
);
GO

/* ===============================
   Main Requests Table
   =============================== */
CREATE TABLE [Requests].[Requests](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [UserId] INT NOT NULL,                  -- from login
    [CategoryId] INT NOT NULL,              -- FK to Category
    [ComplaintScreenId] INT NULL,           -- NEW: FK to ComplaintScreen (only for Complaints)
    [Subject] NVARCHAR(250) NULL,
    [Body] NVARCHAR(MAX) NULL,

    -- RequestData-specific fields:
    [ProspectiveName] NVARCHAR(200) NULL,
    [Coordinate_TopLeft] NVARCHAR(50) NULL,
    [Coordinate_BottomRight] NVARCHAR(50) NULL,
    [ProjectionId] INT NULL,                -- FK to Projection
    [OtherSpecification] NVARCHAR(200) NULL,
    [OtherFormat] NVARCHAR(200) NULL,
    [IntendedPurpose] NVARCHAR(300) NULL,
    [RequirementsDetails] NVARCHAR(MAX) NULL,

    -- Workflow
    [StatusId] INT NULL,
    [AssignedRoleId] INT NULL,              -- which role is assigned
    [RequestNumber] NVARCHAR(50) NULL,      -- e.g. "RQ-20250916-0001" (generate in app)

    -- Audit
    [CreatedAt] DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    [CreatedByUserID] INT NULL,
    [UpdatedAt] DATETIME2(0) NULL,
    [UpdatedByUserID] INT NULL,
    [IsDeleted] BIT DEFAULT 0,

    -- Constraints
    CONSTRAINT FK_Requests_Category FOREIGN KEY (CategoryId) REFERENCES [Requests].[Category](Id),
    CONSTRAINT FK_Requests_Projection FOREIGN KEY (ProjectionId) REFERENCES [Requests].[Projection](Id),
    CONSTRAINT FK_Requests_Status FOREIGN KEY (StatusId) REFERENCES [Requests].[Status](Id),
    CONSTRAINT FK_Requests_Role FOREIGN KEY (AssignedRoleId) REFERENCES [Website].[Roles](RoleID),
    CONSTRAINT FK_Requests_ComplaintScreen FOREIGN KEY (ComplaintScreenId) REFERENCES [Requests].[ComplaintScreen](Id)
);
GO




-- Many-to-many: Request <-> RequestInformation (multi-select)
CREATE TABLE [Requests].[Request_RequestInformation](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [RequestId] INT NOT NULL,
    [RequestInformationId] INT NOT NULL,
    CONSTRAINT FK_R_RI_Request FOREIGN KEY (RequestId) REFERENCES [Requests].[Requests](Id) ON DELETE CASCADE,
    CONSTRAINT FK_R_RI_Info FOREIGN KEY (RequestInformationId) REFERENCES [Requests].[RequestInformation](Id)
);
GO

-- Many-to-many: Request <-> Format (multi-select)
CREATE TABLE [Requests].[Request_Format](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [RequestId] INT NOT NULL,
    [FormatId] INT NOT NULL,
    CONSTRAINT FK_R_F_Request FOREIGN KEY (RequestId) REFERENCES [Requests].[Requests](Id) ON DELETE CASCADE,
    CONSTRAINT FK_R_F_Format FOREIGN KEY (FormatId) REFERENCES [Requests].[Format](Id)
);
GO


-- Reply table (admin replies to user)
CREATE TABLE [Requests].[Reply](
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [RequestId] INT NOT NULL,
    [ResponderUserId] INT NOT NULL,       -- FK to Users (responder is a real user)
    [Subject] NVARCHAR(250) NULL,
    [Body] NVARCHAR(MAX) NULL,
    [AttachmentPath] NVARCHAR(500) NULL,
    [CreatedAt] DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    [CreatedByUserID] INT NULL,
    [IsDeleted] BIT DEFAULT 0,

    CONSTRAINT FK_Reply_Request FOREIGN KEY (RequestId) REFERENCES [Requests].[Requests](Id),
    CONSTRAINT FK_Reply_User FOREIGN KEY (ResponderUserId) REFERENCES [Website].[Users](UserID) -- assuming Users table exists
);


/* ===============================
   Seed Example Data
   =============================== */

delete [Requests].[Category];
INSERT INTO [Requests].[Category] ([Name],[Name_Ar]) VALUES 
('Complaints',N'??? ????'), 
('RequestData',N'??? ??????'), 
('Suggestion',N'??? ?????');


delete [Requests].[Status];

INSERT INTO [Requests].[Status] ([Name],[Name_Ar]) VALUES 
('In Progress',N'??? ????????'), 
('Responded',N'?? ????'), 
('Rejected',N'?????');

INSERT INTO [Requests].[Format] ([Name],[Type]) VALUES 
('Shapefile','Vector'), 
('File Geodatabase','Vector'), 
('AutoCad','Vector'), 

('TIFF','Raster'), 
('IMG','Raster'), 
('ECW','Raster'), 
('JPEG','Raster'), 
('PNG','Raster'), 

('Excel/CSV','Other'),
('PDF','Other')
;


delete [Requests].[Projection];
INSERT INTO [Requests].[Projection] ([Name]) VALUES 
('UTM'), 
('Geographic'), 
('KSA SGS Lamberts');



delete [Requests].[RequestInformation];


INSERT INTO [Requests].[RequestInformation] ([Name],[Name_Ar]) VALUES 
('Geography (Basemaps, Topographic, Elevation, Map Indexes)',N'????????? (????? ??????? ???????????? ??????????? ????? ???????)'), 
('Geology (Geological Maps, Digital, Other Regional)',N'?????????? (????? ????????? ?????? ??????? ????)'), 
('GeoSciences (MODS, Climatology, Geochemistry, Bibliography)',N'???? ????? (MODS? ??? ??????? ???????? ??????????? ???????)'), 
('GeoHazards (Radioactive, Soil, Seismic, Collapse Areas...)',N'??????? ?????????? (?????????? ??????? ???????? ????? ??????????...)'),
('Hydrology (Flooding, Waterm Lakes, DAM, Climate...)',N'??? ?????? (?????????? ???????? ???????? ??????? ??????...)'),
('Remote Sensing (Satellite, Rader, Bathymetry, Geophysical, Gravity, Analysis...)',N'????????? ?? ???? (??????? ????????? ???????? ???? ???????? ?????????????? ????????? ???????...)'),
('National Core Library (Lithological logging, pXRF analyses, hyperspectral data, drill core box photos)',N'??????? ??????? ???????? (??????? ??????? ??????? ?????? ??????? ???????? ???????? ??????? ???????? ??? ????? ??????? ???????? ????????)')
;



INSERT INTO [Website].[Roles] ([NameEn],[NameAr]) VALUES 
(N'Support',N'?????'), 
(N'Data Admin',N'????? ????????'), 
(N'Geospatial Team',N'???? ??????????');

-- Complaint Screens
INSERT INTO [Requests].[ComplaintScreen] ([Name],[Name_Ar]) VALUES 
(N'User Login',N'???? ????? ??????'),
(N'User Register',N'???? ???????'),
(N'Portal Screen',N'???? ???????'),
(N'Data Download',N'???? ????? ????????');
GO