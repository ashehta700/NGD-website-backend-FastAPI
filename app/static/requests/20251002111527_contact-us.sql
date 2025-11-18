
--update the table of the Contact -us 
ALTER TABLE [Website].[ContactUs]
ADD Email NVARCHAR(150) NULL,
    PhoneNumber NVARCHAR(50) NULL,
    ReplyStatus BIT NOT NULL CONSTRAINT DF_ContactUs_ReplyStatus DEFAULT(0);



--Make column of firstname allownull as user now is loggin 
ALTER TABLE [NGD_Website].[Website].[ContactUs]
ALTER COLUMN [FirstName] NVARCHAR(100) NULL;

 -- Create a table of Response for the Contact us Form 
CREATE TABLE [Website].[ContactUsResponse] (
    ResponseID INT IDENTITY(1,1) NOT NULL,
    Subject NVARCHAR(150) NULL,
    Body NVARCHAR(MAX) NULL,
    AttachPath NVARCHAR(500) NULL,
    CreatedByUserID INT NOT NULL,
    CreatedAt DATETIME2(0) NOT NULL CONSTRAINT DF_ContactUsResponse_CreatedAt DEFAULT (sysutcdatetime()),
    ContactID INT NOT NULL,

    CONSTRAINT PK_ContactUsResponse PRIMARY KEY CLUSTERED (ResponseID ASC),
    CONSTRAINT FK_ContactUsResponse_Contact FOREIGN KEY (ContactID) REFERENCES [Website].[ContactUs](ContactID),
    CONSTRAINT FK_ContactUsResponse_User FOREIGN KEY (CreatedByUserID) REFERENCES [Website].[Users](UserID)
);


