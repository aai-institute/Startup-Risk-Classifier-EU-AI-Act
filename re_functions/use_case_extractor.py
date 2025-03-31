import itertools
import re


def generate_tag_variants(tag):
        """Generate all variants by replacing spaces with '', '-' or keeping space."""
        parts = tag.split(" ")
        combinations = list(itertools.product(["", "-", " "], repeat=len(parts)-1))
        variants = set()

        for combo in combinations:
            variant = parts[0]
            for sep, part in zip(combo, parts[1:]):
                variant += sep + part
            variants.add(variant)
        return variants

def extract_use_cases(use_case, classification_string):
    """Input: use_case (dict) - Dictionary containing use case information."""
    """Output: List of dictionaries with extracted use case information."""

    target_tags = [
        "AI Use Case",
        "Use Case Description",
        "Risk Classification",
        "Reason",
        "Requires Additional Information",
        "What additional Information"
    ]

    # Map correct tags to all possible variants
    tag_variants = {tag: generate_tag_variants(tag) for tag in target_tags}


    # === Step 3: Normalize headers with optional leading whitespace ===
    for correct, variants in tag_variants.items():
        for variant in variants:
            if variant == correct:
                continue
            classification_string = re.sub(
                rf"^[ \t]*{re.escape(variant)}\s*:", f"{correct}:", classification_string, flags=re.MULTILINE
            )

    # === Step 4: Extract use case blocks ===
    use_case_blocks = re.split(r"########END OF USE CASE########", classification_string.strip())

    # === Step 5: Extract relevant fields ===
    split_pattern = re.compile(
        rf"^[ \t]*({'|'.join(re.escape(tag) for tag in target_tags)})\s*:",
        flags=re.MULTILINE
    )

    results = []

    for block in use_case_blocks:
        block = block.strip()

        if not re.search(r"^AI Use Case:", block, flags=re.MULTILINE):
            continue  # Skip invalid blocks

        chunks = split_pattern.split(block)

        data = {
            "AI Use Case": use_case["use_case_name"],
            "Use Case Description": use_case["use_case_description"],
            "Risk Classification": "",
            "Reason": "",
            "Requires Additional Information": "No",
            "What additional Information": ""
        }

        for i in range(1, len(chunks), 2):
            tag = chunks[i].strip()
            value = chunks[i + 1].strip()
            if tag in data:
                data[tag] = value

        if data["Requires Additional Information"].lower() == "no":
            data["What additional Information"] = ""

        results.append(data)


    return results