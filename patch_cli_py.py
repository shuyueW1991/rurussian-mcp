import sys

cli_path = '/home/wangshuyue/litelanglearn_repo/dev/litelanglearn/backend/cli.py'
with open(cli_path, 'r') as f:
    content = f.read()

old_str = """    elif command == "create_checkout_session":
        return BackendService.create_checkout_session(data)"""

new_str = """    elif command == "create_checkout_session":
        return BackendService.create_checkout_session(data)
    elif command == "validate_bot_api_key":
        return BackendService.validate_bot_api_key(data)"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(cli_path, 'w') as f:
        f.write(content)
    print("Patched cli.py successfully.")
else:
    print("Could not find the target string in cli.py.")
