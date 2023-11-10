import json
import os
import shutil
import subprocess
import tempfile
import sys

class DesktopFileOrganizer:
    def __init__(self):
        # Configuración inicial
        self.custom_categories = self.load_categories()
        self.setup_default_categories()

    def load_categories(self, file_path="categories.json"):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_categories(self, categories, file_path="categories.json"):
        with open(file_path, "w") as file:
            json.dump(categories, file, indent=2)

    def setup_default_categories(self, file_path="categories.json", default_input=None):
        if not self.custom_categories:
            print("Setting up Default Categories:")
            default_categories = {"Images": {"path": "", "extensions": ["jpg", "png", "gif"]},
                                  "Videos": {"path": "", "extensions": ["mp4", "avi", "mkv"]},
                                  "Documents": {"path": "", "extensions": ["pdf", "docx", "txt"]}}

            for category, details in default_categories.items():
                if default_input is not None:
                    path = default_input.get(category, {}).get("path", "")
                    extensions = default_input.get(category, {}).get("extensions", details["extensions"])
                else:
                    path = input(f"Enter the path for {category} category: ")
                    extensions = input(f"Enter file extensions to be organized (comma-separated, press Enter to use defaults): ").strip()
                
                    if extensions:
                        extensions = [ext.strip() for ext in extensions.split(",")]
                    else:
                        extensions = details["extensions"]

                details["path"] = path
                details["extensions"] = extensions

            self.custom_categories = default_categories
            self.save_categories(self.custom_categories, file_path)
            print("Default categories set up successfully!\n")

    def show_default_categories(self):
        print("Default Categories:")
        for category, details in self.custom_categories.items():
            print(f"{category}: {details['path']} (Extensions: {', '.join(details['extensions'])})")
        print("\n")

    def list_set_directories(self, is_default=False):
        print("Set Directories:")
        for category, details in self.custom_categories.items():
            print(f"{category}: {details['path']} (Extensions: {', '.join(details['extensions'])})")
        print("\n")
      
    def customize_categories(self, user_input=None):
        while True:
            print("Customize Categories:")
            print("1. Add a category")
            print("2. List set directories")
            print("3. Execute immediate cleanup")
            print("4. Schedule cleanup")
            print("5. Exit")

            choice = user_input if user_input is not None else input("Enter your choice (1/2/3/4): ")

            if choice == "1":
                self.add_category(user_input=user_input)
            elif choice == "2":
                self.list_set_directories()
            elif choice == "3":
                self.execute_immediate_cleanup()
            elif choice == "4":
                self.configure_schedule()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.\n")

    def execute_immediate_cleanup(self):
        print("Executing immediate cleanup:")
        desktop_path = os.path.expanduser("~/Desktop")
        downloads_path = os.path.expanduser("~/Downloads")

        for category, details in self.custom_categories.items():
            folder_path = os.path.join(details["path"], details["extensions"][0])  # Usamos la primera extensión como carpeta

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            source_folders = [desktop_path, downloads_path]

            for source_folder in source_folders:
                for file_name in os.listdir(source_folder):
                    source_path = os.path.join(source_folder, file_name)
                    
                    for ext in details["extensions"]:
                        if file_name.lower().endswith(ext.lower()):
                            destination_path = os.path.join(folder_path, file_name)
                            shutil.move(source_path, destination_path)
                            print(f"Moved '{file_name}' to '{category}' category.")

        print("Immediate cleanup completed!\n")

    def move_files_to_folder(self, source_folder, destination_folder, extensions):
        os.makedirs(destination_folder, exist_ok=True)
        for file_name in os.listdir(source_folder):
            if file_name.endswith(tuple(extensions)):
                source_path = os.path.join(source_folder, file_name)
                destination_path = os.path.join(destination_folder, file_name)
                shutil.move(source_path, destination_path)

    
    def add_category(self, user_input=None):
        while True:
            category_name = user_input if user_input is not None else input("Enter the name of the category: ")
            path = user_input if user_input is not None else input(f"Enter the path for {category_name} category: ")
            extensions = user_input if user_input is not None else input(f"Enter file extensions to be organized (comma-separated): ").strip()

            if category_name and path and extensions:
                break
            else:
                print("Please enter all details for the category.")

        if extensions:
            extensions = [ext.strip() for ext in extensions.split(",")]
        else:
            extensions = self.custom_categories.get(category_name, {}).get("extensions", [])

        self.custom_categories[category_name] = {"path": path, "extensions": extensions}
        self.save_categories(self.custom_categories)  # Guardar las categorías después de cada modificación

        print(f"Category '{category_name}' added successfully!\n")

    def configure_schedule(self):
        print("Configure Schedule:")
        self.print_cron_format_reference()
        schedule_time = input("Enter the schedule time for cleanup (in cron format): ")

        current_directory = os.getcwd()
        cron_command = f'/opt/homebrew/bin/python3 {current_directory}/organizer.py exec 3'
        cron_entry = f'{schedule_time} {cron_command}'

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(cron_entry)

        try:
            subprocess.run(["crontab", temp_file.name], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Schedule configured successfully!\n")
        except subprocess.CalledProcessError as e:
            print(f"Error configuring schedule: {e.output}")
        finally:
            os.remove(temp_file.name)
        
    def print_cron_format_reference(self):
        print("Cron Format Reference:")
        print("┌───────────── Minuto (0 - 59)")
        print("│ ┌───────────── Hora (0 - 23)")
        print("│ │ ┌───────────── Día del mes (1 - 31)")
        print("│ │ │ ┌───────────── Mes (1 - 12)")
        print("│ │ │ │ ┌───────────── Día de la semana (0 - 6) (Domingo a Sábado)")
        print("│ │ │ │ │")
        print("│ │ │ │ │")
        print("* * * * *")
        print("\n")

    def run(self):
        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == 'exec' and len(sys.argv) > 2:
                option = sys.argv[2]
                if option == '3':
                    self.execute_immediate_cleanup()
                else:
                    print("Invalid option. Please use 'python3 organizer.py exec 3' to execute immediate cleanup.")
            else:
                print("Invalid command. Please use 'python3 organizer.py exec 3' to execute immediate cleanup.")
        else:
            self.customize_categories()

if __name__ == "__main__":
    organizer = DesktopFileOrganizer()
    organizer.run()
