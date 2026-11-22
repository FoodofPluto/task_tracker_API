It’s this URL (URL-encoded path):


sqlite:///C%3A%5CUsers%5Candro%5CDesktop%5Cweb-fundementals%5Cinstance%5Cdev.db


which corresponds to this Windows path:


C:\Users\andro\Desktop\web-fundementals\instance\dev.db

Now, from your project root (C:\Users\andro\Desktop\web-fundementals\task_tracker), do this:

Powershell
sqlite3 ..\instance\dev.db
Then at the sqlite> prompt:

SQL
.tables
.schema user
SELECT id, username, password_hash FROM user;

Login uses check_password_hash; wrong password for an existing user returns INVALID_CREDENTIALS and PowerShell throws an exception due to the 4xx response.