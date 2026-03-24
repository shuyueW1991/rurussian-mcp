import sys

rds_storage_path = '/home/wangshuyue/litelanglearn_repo/dev/litelanglearn/backend/rds_storage.py'
with open(rds_storage_path, 'r') as f:
    content = f.read()

old_str = """            cursor.execute("SHOW COLUMNS FROM zakuska LIKE 'audio_url'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE zakuska ADD COLUMN audio_url VARCHAR(1024)")

    finally:"""

new_str = """            cursor.execute("SHOW COLUMNS FROM zakuska LIKE 'audio_url'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE zakuska ADD COLUMN audio_url VARCHAR(1024)")

            # Table for MCP Bot API keys
            cursor.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS bot_api_keys (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    api_key VARCHAR(255) NOT NULL UNIQUE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_email) REFERENCES rurussian_users(email) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            \"\"\")

            # Table for MCP Usage Logs
            cursor.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS mcp_usage_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    api_key VARCHAR(255) NOT NULL,
                    endpoint VARCHAR(255) NOT NULL,
                    user_agent VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (api_key) REFERENCES bot_api_keys(api_key) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            \"\"\")

    finally:"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(rds_storage_path, 'w') as f:
        f.write(content)
    print("Patched rds_storage.py tables successfully.")
else:
    print("Could not find the target string in rds_storage.py.")
