import re
import pandas as pd

class TextExtractor():
    def __init__(self, text):
        self.__text = text
        self.__data = {
            "AI Use Case": [],
            "Use Case Description": [],
            "AI Process Used": [],
            "Type of Models Used": [],
        }

    def set_use_cases(self):
        self.__text = self.__text.replace("*", "").replace("#", "")

        # Regular expressions to extract sections
        use_case_pattern = r"AI Use Case:\s*(.+?)\s*(?:\n)"
        description_pattern = r"(?:Use Case Description:)\s*(.+?)\s*(?:\n\n|AI Process Used:)"
        process_pattern = r"(?:AI Process Used:)\s*(.+?)\s*(?:\n\n|Type of Models Used:)"
        models_pattern = r"(?:Type of Models Used:)\s*(.+?)\s*(?:\n\n|\n---|$)"

        # Extracting data
        use_cases = re.findall(use_case_pattern, self.__text, re.DOTALL)
        descriptions = re.findall(description_pattern, self.__text, re.DOTALL)
        processes = re.findall(process_pattern, self.__text, re.DOTALL)
        models = re.findall(models_pattern, self.__text, re.DOTALL)

        # Adding data to dictionary
        for i in range(len(use_cases)):
            self.__data["AI Use Case"].append(use_cases[i])
            self.__data["Use Case Description"].append(descriptions[i])
            self.__data["AI Process Used"].append(processes[i])
            self.__data["Type of Models Used"].append(models[i])

    def get_use_cases(self) -> pd.DataFrame:
        df = pd.DataFrame(self.__data)
        return df

        