class StringManipulator:
    # Provides string manipulation utilities
    
    @staticmethod  # Now we define a method for our to_lower function
    def to_lower(string):
        lower_str = ""
        for letter in string:
            if 65 <= ord(letter) <= 90:
                lower_str += chr(ord(letter) + 32)
            else:
                lower_str += letter
        return lower_str

def main():
    input_str = input("Enter text to be converted to lowercase: ")  # Prompt for input
    result = StringManipulator.to_lower(input_str) # Call the to_lower method of the StringManipulator class
    print("Your text has been converted:\n" + result) # Print the output

# Ensures the main function runs only when the script is executed directly
if __name__ == "__main__":
    main()