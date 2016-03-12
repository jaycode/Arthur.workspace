class ArthurContextProperty(ArthurContext):
    """
    Question: We want to find out which context a given word is part of.
    Possible calculations:
    1. Calculate levenshtein distance of given word with all val_samples, then
       return key of the val_sample with smallest levenshtein distance.
    2. If given text follows a certain regex, adds its relevancy score with regex_weight.
       regex_weight defaults at 0.5, and can be set up manually below.
    3. If we have information of text found in pdf right before given word, we can
       perhaps give weight to associated key, but this is not 100%.

    Maybe we can try with #1 first and when improvement is needed we can try #2 and #3.

    For example, consider following ArthurDocumentElements in pdf (subtle differences are intentional):

    - Community features:
    - private settings, southern exposures.

    As levensthein distance is closest when compared with "appliances included", that is the
    value that will be returned.

    Different languages may have different rules. We can expand our project by creating other
    contexts.

    ## Complications:

    **1. Key and value could be stored in one line, for example: "View: ocean view".**

    To deal with this, maybe we can imitate a method used in DNA string comparison,
    where values found before and after search string are not penalized (see Smith-
        Waterman algorithm).


"""

    ### Return json text of context.
    def value():
        return """
        {
            "address": {
                "val_regex": "[,-a-zA-Z0-9 ]",
                "val_samples": ["3150 Rutland Rd, Victoria, British Columbia V8R4R8"]
            },
            "total_rooms": {
                "key_location": "right",
                "key_samples": [{"type": "image", "path": ""}],
                "val_regex": "[0-9]"
            },
            "total_bathrooms": {
                "key_location": "right",
                "key_samples": [{"type": "image", "path": ""}],
                "val_regex": "[0-9]"
            },
            "property_type": {
                "key_samples": ["property type"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": [
                    "single family"
                ]
            },
            "land_size": {
                "key_samples": ["land size"],
                "val_regex": "^[0-9][.0-9a-z ]+",
                "regex_weight": 0.8,
                "val_samples": ["0.9065 hec"]
            },
            "building_type": {
                "key_samples": ["building type"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": ["house"]
            },
            "built_in": {
                "key_samples": ["built in"],
                "val_regex": "[0-9]{4}",
                "regex_weight": 0.8,
                "val_samples": ["1914"]
            },
            "title": {
                "key_samples": ["title"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": [
                    "freehold"
                ]
            },
            "appliances_included": {
                "key_samples": ["appliances included"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": [
                    "hot tub",
                    "water softener",
                    "central vacuum"
                ]
            },
            "community_features": {
                "key_samples": ["community features"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": [
                    "quiet area"
                ]
            },
            "features": {
                "key_samples": ["features"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": [
                    "cul-de-sac",
                    "private setting",
                    "southern exposure",
                    "wheelchair access"
                ]
            },
            "view": {
                "key_samples": ["view"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": [
                    "view of water",
                    "mountain view",
                    "city view",
                    "ocean view",
                    "lake view"
                ]
            },
            "parking_type": {
                "key_samples": ["parking type"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": [
                    "garage"
                ]
            },
            "waterfront": {
                "key_samples": ["waterfront"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": ["waterfront on ocean"]
            },
            "zoning_id": {
                "key_samples": ["zoning id"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": ["residential"]
            },
            "description": {
                "key_samples": ["description"],
                "val_regex": "."
            },
            "floor_space": {
                "key_samples": ["floor space"],
                "val_regex": "^[0-9][.0-9a-z ]+",
                "regex_weight": 0.8,
                "val_samples": ["1025.742 m2"]
            },
            "style": {
                "key_samples": ["style"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": ["detached"]
            },
            "walk_score": {
                "key_samples": ["walk score"],
                "val_regex": "[0-9]",
                "regex_weight": 0.8,
                "val_samples": [6]
            },
            "walk_score_detail": {
                "key_samples": ["walk score"],
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": ["car-dependent"]
            },
            "agent_name": {
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": ["Sylvia", "Therrien"],
            },
            "agent_job_desc": {
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": ["personal real estate corporation"],
            },
            "agent_company_name": {
                "val_regex": "[-a-zA-Z0-9 ]",
                "val_samples": ["newport realty"],
            },
            "agent_company_address": {
                "val_regex": "[,-a-zA-Z0-9 ]",
                "val_samples": ["1286 Fairfield Rd", "Victoria, BC V8V4W3"]
            },
            "agent_company_phone": {
                "key_samples": [{"type": "image", "path": ""}],
                "val_regex": "[-0-9]",
                "val_samples": ["250-385-2033"]
            },
            "agent_company_fax": {
                "key_samples": ["fax:"],
                "val_regex": "[-0-9]",
                "val_samples": ["250-385-3763"]
            }
        }
        """
