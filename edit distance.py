import nltk
from nltk.metrics import edit_distance
import re

# List of variants
silver_oak_variants = [
    "Silver Oak University", "Silver Oak Univ", "Silver Oak Uni", "Silvar Oak University",
    "Silvar Of University", "Silvar Oak University", "SOU", "silchar university",
    "silver oak college", "silver oak", "Silver Oak Univrsty", "Silver Oak Unversity",
    "Silver Ok University", "Silver Oke University", "Silver Oak Univercity",
    "Silvar Oak Univrsty", "Silvar Oak Univrsity", "Silvar Ok University", "Silvar Oke University",
    "Silvar Oak Univercity", "Silvar Oke Univercity", "Siver Oak University", "Siver Oak Univ",
    "Siver Oak Uni", "Silver Ock University", "Silver Ok Univ", "Silver Oke Univ",
    "Silver Oc University", "Silver Oak Unversty", "Silver Oak Unversity", "S O University",
    "S O Univ", "S O Uni", "Silvr Oak University", "Silvr Oak Univ", "Silvr Oak Uni",
    "Silvr Oak Univrsity", "Silvr Ok University", "Silvr Oke University", "Silvr Oak Univercity",
    "Silver Oak Universtiy", "Silvar Oak Universtiy", "Silver Oak Unitversity", "SOUK",
    "Silver Ock Univ", "Silvar Oc University", "Silvar Ock Univ", "Silvar Oak Univerity",
    "Silver Ok Unv", "Silver Oak Uinversity", "Silver Oak Universty", "Silver Oak Unvsty",
    "Silver Oak Univty", "Silver Oak Unvty", "Silver Oak Universtity", "Silvr Oak Unversty", "SOU", "sou"
]

# Target name
target = "Silver Oak University"

# Function to find the closest match
def find_closest_match(word, variants):
    distances = [(variant, edit_distance(word.lower(), variant.lower())) for variant in variants]
    closest_match = min(distances, key=lambda x: x[1])
    return closest_match[0]

# Function to replace variants in the text
def replace_variants_in_text(text, variants, target):
    words = text.split()
    corrected_words = []
    
    for word in words:
        # Remove any punctuation for matching
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word:
            closest_match = find_closest_match(clean_word, variants)
            if edit_distance(clean_word.lower(), closest_match.lower()) <= 3:  # threshold can be adjusted
                corrected_words.append(target)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)
    
    return ' '.join(corrected_words)

# Example text
text = "Welcome to Silver Oke University. We hope you enjoy your time at Silver Oak Univrsty."

# Replace variants in the text
corrected_text = replace_variants_in_text(text, silver_oak_variants, target)
print("Corrected text:", corrected_text)
