import json
import re
from difflib import SequenceMatcher
from typing import Tuple, Optional


# To be run on workflows /POST
def check_json_similarity_with_warning(
    user_input: str, similarity_threshold: float = 0.95
) -> Tuple[float, Optional[str]]:
    try:
        # Parse JSON strings into Python dictionaries
        regex_pattern = re.compile(f".*{re.escape(user_input)}.*", re.IGNORECASE)
        json_obj1 = mongo.workflows.find({"info.title": {"$regex": regex_pattern}})
        json_obj2 = json.loads(user_input)

        # Convert dictionaries to JSON strings
        json_str1 = json.dumps(json_obj1, sort_keys=True)
        json_str2 = json.dumps(json_obj2, sort_keys=True)

        # Use SequenceMatcher to find the similarity ratio
        similarity = SequenceMatcher(None, json_str1, json_str2).ratio()

        if similarity > similarity_threshold:
            warning_message = "Warning: High similarity detected."
        else:
            warning_message = None

        return similarity, warning_message
    except json.JSONDecodeError:
        # Handle JSON parsing errors if necessary
        return 0.0, "Error: JSON parsing failed."
