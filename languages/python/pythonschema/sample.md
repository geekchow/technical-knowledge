# `pythonschema` could do json schema validation 

```python 
import jsonschema
import re

# Define the JSON schema for the JSON array of complex objects with embedded schema
json_array_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "pattern": "^([a-zA-Z]+-)*[a-zA-Z]+$"
            },
            # Add other properties and their validations as needed
            # Example: "age": {"type": "integer", "minimum": 0, "maximum": 150},
        },
        "required": ["name"],
        "additionalProperties": False
    }
}

def validate_json_array(json_data):
    try:
        jsonschema.validate(instance=json_data, schema=json_array_schema)
        print("Validation successful.")
    except jsonschema.ValidationError as e:
        print(f"Validation failed: {e}")

# Example JSON array for testing
example_json_array = [
    {"name": "item-1"},
    {"name": "item-2"},
    # Add more items as needed
]

# Validate the example JSON array
validate_json_array(example_json_array)

```

> Caution: you have to bear in mind, for "pattern" property you must match the whole string with ^ and & symbol to match the whole string, otherwise, once it matches any part it passes the validation. 