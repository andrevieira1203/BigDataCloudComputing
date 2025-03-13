import webbrowser
import requests
import json

# Dicionário de endpoints
endpoints = {
    "1": {"name": "Get Patient Details", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "GET"},
    "2": {"name": "Get Admissions for a Patient", "url": "http://127.0.0.1:8080/rest/admissions/{}", "method": "GET"},
    "3": {"name": "Get Patients with Longest Stays", "url": "http://127.0.0.1:8080/rest/patients/longest_stays", "method": "GET"},
    "4": {"name": "Create a New Patient", "url": "http://127.0.0.1:8080/rest/patients", "method": "POST"},
    "5": {"name": "Create a New Admission", "url": "http://127.0.0.1:8080/rest/admissions", "method": "POST"},
    "6": {"name": "Update Patient Details", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "PUT"},
    "7": {"name": "Delete a Patient", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "DELETE"},
    "8": {"name": "Delete a Admission", "url": "http://127.0.0.1:8080/rest/admissions/{}", "method": "DELETE"},
    "9": {"name": "List All Patients", "url": "http://127.0.0.1:8080/rest/patients", "method": "GET"}
}

def send_request(method, url, data=None):
    """Envia requisições HTTP e imprime a resposta."""
    try:
        headers = {"Content-Type": "application/json"}  # Garante JSON válido

        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        print("\n✅ HTTP Status Code:", response.status_code)
        print("✅ Raw Response Text:", response.text)

        if "application/json" in response.headers.get("Content-Type", ""):
            response_json = response.json()
            print("\n✅ Parsed JSON Response:")
            print(json.dumps(response_json, indent=4))
        else:
            print("\n❌ Error: Response is not valid JSON!")
            print("👉 Possible HTML or empty response received.")

    except json.decoder.JSONDecodeError:
        print("\n❌ Error: API did not return valid JSON!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def get_user_choice():
    for key, value in endpoints.items():
        print(f"{key}. [{value['method']}] {value['name']}")

    choice = input("\nEnter the number of the endpoint you want to use: ")

    if choice in endpoints:
        url_template = endpoints[choice]["url"]
        method = endpoints[choice]["method"]
        url = url_template
        data = None

        if "{}" in url_template and choice not in ["6", "7", "8"]:
            subject_id = input("Enter Subject ID: ")
            url = url_template.format(subject_id)

        elif choice == "4":  # Criar paciente
            subject_id = input("Enter Subject ID: ")
            gender = input("Enter Gender (M/F): ").strip().upper()
            dob = input("Enter Date of Birth (YYYY-MM-DD): ").strip()
            data = {"subject_id": int(subject_id), "gender": gender, "dob": dob}

        elif choice == "5":  # Criar admissão
            subject_id = input("Enter Subject ID: ")
            hadm_id = input("Enter Admission ID: ")
            admittime = input("Enter Admission Time (YYYY-MM-DD HH:MM:SS): ").strip()
            dischtime = input("Enter Discharge Time (YYYY-MM-DD HH:MM:SS): ").strip()
            diagnosis = input("Enter Diagnosis: ").strip()
            data = { "subject_id": int(subject_id), "hadm_id": int(hadm_id), "admittime": admittime, "dischtime": dischtime, "diagnosis": diagnosis}

        elif choice == "6":  # Atualizar paciente
            subject_id = input("Enter Subject ID: ")
            data = {}

            if input("Update Gender? (Y/N): ").strip().lower() == "y":
                data["gender"] = input("Enter New Gender (M/F): ").strip().upper()

            if input("Update Date of Birth? (Y/N): ").strip().lower() == "y":
                data["dob"] = input("Enter New Date of Birth (YYYY-MM-DD): ").strip() + " 00:00:00"

            if data:
                url = f"http://127.0.0.1:8080/rest/patients/{subject_id}"
            else:
                print("No updates provided.")
                return

        elif choice == "7":  # Delete paciente
            subject_id = input("Enter the ID of the patient to delete: ")
            url = url_template.format(subject_id)
            if input(f"⚠ Confirm deletion of patient {subject_id}? (yes/no): ").strip().lower() != "yes":
                print("❌ Operation cancelled.")
                return
            
        elif choice == "8":  # Delete admission
            hadm_id = input("Enter the ID of the admission to delete: ")
            url = url_template.format(hadm_id)
            if input(f"⚠ Confirm deletion of patient {hadm_id}? (yes/no): ").strip().lower() != "yes":
                print("❌ Operation cancelled.")
                return

        # Enviar requisição
        if method in ["POST", "PUT", "DELETE"]:
            send_request(method, url, data)
        else:
            print(f"\nOpening: {url}")
            webbrowser.open_new_tab(url)
    else:
        print("❌ Invalid choice.")

while True:
    get_user_choice()
    if input("\nTest another endpoint? (y/n): ").strip().lower() != "y":
        print("Exiting...")
        break
