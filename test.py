import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=NGD_Website;"
    "UID=sa;"
    "PWD=Shehta@2022;"
    "TrustServerCertificate=yes;"
)
print("✅ Connection successful!")
conn.close()
