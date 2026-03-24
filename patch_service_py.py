import sys

service_path = '/home/wangshuyue/litelanglearn_repo/dev/litelanglearn/backend/service.py'
with open(service_path, 'r') as f:
    content = f.read()

# We need to import the new functions from rds_storage.py
import_old = """try:
    from .rds_storage import (
        get_cached_sentence, get_cached_sentences_for_forms, save_cached_sentence, get_user_by_email, 
        create_or_update_user, update_subscription, ensure_database_and_table,
        add_saved_word, remove_saved_word, get_saved_words, 
        add_saved_sentence, remove_saved_sentence, get_saved_sentences, 
        remove_saved_sentence_by_text, get_saved_sentence_analysis, update_saved_sentence_analysis,
        add_zakuska, get_zakuskas, get_today_zakuska_count,
        get_zakuska_by_id, update_zakuska_audio,
        vote_sentence, get_user_sentence_votes
    )"""

import_new = """try:
    from .rds_storage import (
        get_cached_sentence, get_cached_sentences_for_forms, save_cached_sentence, get_user_by_email, 
        create_or_update_user, update_subscription, ensure_database_and_table,
        add_saved_word, remove_saved_word, get_saved_words, 
        add_saved_sentence, remove_saved_sentence, get_saved_sentences, 
        remove_saved_sentence_by_text, get_saved_sentence_analysis, update_saved_sentence_analysis,
        add_zakuska, get_zakuskas, get_today_zakuska_count,
        get_zakuska_by_id, update_zakuska_audio,
        vote_sentence, get_user_sentence_votes,
        get_user_by_api_key, log_mcp_usage
    )"""

fallback_import_old = """except ImportError:
    from rds_storage import (
        get_cached_sentence, get_cached_sentences_for_forms, save_cached_sentence, get_user_by_email, 
        create_or_update_user, update_subscription, ensure_database_and_table,
        add_saved_word, remove_saved_word, get_saved_words, 
        add_saved_sentence, remove_saved_sentence, get_saved_sentences, 
        remove_saved_sentence_by_text, get_saved_sentence_analysis, update_saved_sentence_analysis,
        add_zakuska, get_zakuskas, get_today_zakuska_count,
        get_zakuska_by_id, update_zakuska_audio,
        vote_sentence, get_user_sentence_votes
    )"""

fallback_import_new = """except ImportError:
    from rds_storage import (
        get_cached_sentence, get_cached_sentences_for_forms, save_cached_sentence, get_user_by_email, 
        create_or_update_user, update_subscription, ensure_database_and_table,
        add_saved_word, remove_saved_word, get_saved_words, 
        add_saved_sentence, remove_saved_sentence, get_saved_sentences, 
        remove_saved_sentence_by_text, get_saved_sentence_analysis, update_saved_sentence_analysis,
        add_zakuska, get_zakuskas, get_today_zakuska_count,
        get_zakuska_by_id, update_zakuska_audio,
        vote_sentence, get_user_sentence_votes,
        get_user_by_api_key, log_mcp_usage
    )"""

if import_old in content:
    content = content.replace(import_old, import_new)
if fallback_import_old in content:
    content = content.replace(fallback_import_old, fallback_import_new)

# Add validate_bot_api_key to BackendService
service_class_start = """class BackendService:"""
service_class_new = """class BackendService:
    @staticmethod
    def validate_bot_api_key(data: Dict):
        api_key = data.get("api_key")
        endpoint = data.get("endpoint", "unknown")
        user_agent = data.get("user_agent", "unknown")
        
        if not api_key:
            return {"error": "Missing API key", "status_code": 401}
            
        user = get_user_by_api_key(api_key)
        if not user:
            return {"error": "Invalid API key", "status_code": 401}
            
        if user.get("subscription_status") != "active":
            return {"error": "Active subscription required", "status_code": 403}
            
        log_mcp_usage(api_key, endpoint, user_agent)
        return {"valid": True, "user_email": user.get("email")}
"""

if service_class_start in content and "def validate_bot_api_key" not in content:
    content = content.replace(service_class_start, service_class_new)

with open(service_path, 'w') as f:
    f.write(content)

print("Patched service.py successfully.")
