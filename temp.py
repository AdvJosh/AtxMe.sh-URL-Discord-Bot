from functools import reduce  # Tool to simplify recursion

def to_lower(str_1, str_2):
    # if str_2 is uppercase, char is the letter in lowercase. Otherwise, char == str_2
    char = chr(ord(str_2) + 32) if 65 <= ord(str_2) <= 90 else str_2
    print(f"str_1 = {str_1} | str_2 = {str_2} | char = {char}") # Just printing to show recursion
    return str_1 + char

def main():
    input_str = input("Enter text to be converted to lowercase: ")  # Prompt for input
    result = reduce(to_lower, input_str, "") # Use reduce to run the to_lower function recursively
    print("Your text has been converted:\n" + result) # Print the output

if __name__ == "__main__":  # Standard way to run main function when script is called
    main()
