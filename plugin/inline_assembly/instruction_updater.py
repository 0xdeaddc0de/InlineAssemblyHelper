import os
import platform
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from ida_kernwin import get_kernel_version
from idaapi import get_user_idadir

def retrieve_IDA_path():
    os_name = platform.system()
    if os_name == "Linux:
        ida_path : str = get_user_idadir().replace(".","") + "-" + get_kernel_version() 
        return os.path.join(ida_path, "plugins","inline_assembly","instruction.py")
    else os_name == "Windows":
        ida_path : str = get_user_idadir()
        return os.path.join(ida_path, "plugins","inline_assembly","instruction.py")

    

def scrape_instructions(url="https://www.felixcloutier.com/x86/"):
    file_path = retrieve_IDA_path()
    if os.path.exists(file_path):
        last_modified_time = os.path.getmtime(file_path)
        current_time = time.time()
        two_weeks_ago = current_time - (7 * 4 * 24 * 60 * 60) 

        if last_modified_time > two_weeks_ago:
            print(f"[InlineAssembly] The file '{file_path}' was updated in the last two weeks. Skipping scraping.")
            return
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        instructions_dict = {}

        sections = ["Core Instructions", "SGX Instructions", "VMX Instructions", "Xeon Phi™ Instructions", "SMX Instructions"]

        for section in sections:
            section_heading = soup.find('h2', text=section)

            if section_heading:
                table = section_heading.find_next('table')

                if table:
                    rows = table.find_all('tr')[1:]

                    for row in rows:
                        columns = row.find_all('td')
                        mnemonic = columns[0].text.strip().lower()
                        definition = columns[1].text.strip()

                        mnemonic = mnemonic.replace("'", ' ')
                        definition = definition.replace("'", ' ')

                        instructions_dict[mnemonic] = definition

                else:
                    print(f"[InlineAssembly] able not found after '{section}' heading.")

            else:
                print(f"[InlineAssembly] Heading '{section}' not found on the page.")

        with open(file_path, "w",encoding="utf-8") as file:
            file.write("instruction_dict = {\n")
            for mnemonic, definition in instructions_dict.items():
                file.write(f'    "{mnemonic}": "{definition}",\n')
            file.write("}\n")

        print("[InlineAssembly] Instructions written to instructions.py")

    else:
        print(f"InlineAssembly] Failed to retrieve the page. Status code: {response.status_code}")

if __name__ == "__main__":
    scrape_instructions()
