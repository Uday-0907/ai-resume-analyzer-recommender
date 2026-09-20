import re

def clean_text(text: str) -> str:
    """
    Converts text to lowercase, removes unwanted characters while keeping
    essential technical symbols like C++, C#, and .NET.
    """
    if not text:
        return ""
    
    # Lowercase text
    text = text.lower()
    
    # Protect special terms temporarily
    replacements = {
        'c++': ' cpp_token ',
        'c#': ' csharp_token ',
        '.net': ' dotnet_token '
    }
    
    for key, value in replacements.items():
        text = text.replace(key, value)
        
    # Remove symbols except letters, digits, whitespace, and underscores
    text = re.sub(r'[^a-z0-9\s_]', ' ', text)
    
    # Restore special terms
    text = text.replace('cpp_token', 'c++')
    text = text.replace('csharp_token', 'c#')
    text = text.replace('dotnet_token', '.net')
    
    # Normalize extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text