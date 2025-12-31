import os
import struct

def decrypt_cfg(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()

    if not data.startswith(b'HDR2'):
        print("Error: Not a HDR2 file")
        return

    header = data[:8]
    body = data[8:]
    
    # Header format: 4 bytes profile, 3 bytes size, 1 byte randkey
    # Note: Size is little endian 3 bytes
    
    randkey = header[7]
    print(f"Decryption Key (Randkey): {randkey}")
    
    decrypted_data = bytearray()
    for b in body:
        # Algorithm: decoded = (0xFF - (encrypted - randkey)) & 0xFF
        # Equivalent to: (255 + randkey - b) & 0xFF
        decoded_byte = (0xFF + randkey - b) & 0xFF
        decrypted_data.append(decoded_byte)

    # Convert to text, replacing nulls and control chars with newlines
    text_output = []
    
    # Try to decode as utf-8, falling back to replace
    # We want to format it as key=value lines
    
    # It seems to be null separated or control-char separated.
    # scan for strings
    
    current_string = []
    
    # We'll treat any sequence of printable chars as a token.
    # Chars < 32 or > 126 are separators
    
    cleaned_content = ""
    
    # Simple replacement of 0x00, 0x0D, 0x0E with \n
    # And other control chars
    
    for b in decrypted_data:
        if 32 <= b <= 126:
            cleaned_content += chr(b)
        elif b == 10 or b == 13: # \n or \r
            cleaned_content += '\n'
        else:
            # Separator
            if cleaned_content and not cleaned_content.endswith('\n'):
                cleaned_content += '\n'
                
    # Remove empty lines
    lines = [line for line in cleaned_content.split('\n') if line.strip()]
    final_text = '\n'.join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
        
    print(f"Decrypted content saved to {output_path}")
    print(f"Extracted {len(lines)} lines.")

def search_keys(filepath):
    key_search = "pass"
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        print(f"Read {len(lines)} lines.")
        key_search = input(f"Enter key to search (default: '{key_search}'): ").strip() or key_search
        print(f"\n--- Searching for {key_search} ---")
        for i, line in enumerate(lines):
            if key_search in line.lower():
                print(f"\nLine {i+1}: \033[32m{line.strip()}\033[0m\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_file = input("ASUS .cfg file name: ").strip()
    output_file = input("Decrypted file name (default: 'Decrypted_ASUS_cfg.txt'): ").strip() or "Decrypted_ASUS_cfg.txt"
    decrypt_cfg(input_file, output_file)
    search_keys(output_file)
