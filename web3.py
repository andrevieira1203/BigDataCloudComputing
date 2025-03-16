import webbrowser
import requests
import json
import os

# Dicionário de endpoints
endpoints = {
    "1": {"name": "Get Patient Details", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "GET"},
    "2": {"name": "Get Admissions for a Patient", "url": "http://127.0.0.1:8080/rest/admissions/{}", "method": "GET"},
    "3": {"name": "Get Patients with Longest Stays", "url": "http://127.0.0.1:8080/rest/patients/longest_stays", "method": "GET"},
    "4": {"name": "Create a New Patient", "url": "http://127.0.0.1:8080/rest/patients", "method": "POST"},
    "5": {"name": "Create a New Admission", "url": "http://127.0.0.1:8080/rest/admissions", "method": "POST"},
    "6": {"name": "Update Patient Details", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "PUT"},
    "7": {"name": "Delete a Patient", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "DELETE"},
    "8": {"name": "Delete an Admission", "url": "http://127.0.0.1:8080/rest/admissions/{}", "method": "DELETE"},
    "9": {"name": "List All Patients", "url": "http://127.0.0.1:8080/rest/patients", "method": "GET"},
    "10": {"name": "Create a Question", "url": "http://127.0.0.1:8080/rest/patients/{}/question", "method": "POST"},
    "11": {"name": "List Questions for a Patient", "url": "http://127.0.0.1:8080/rest/patients/{}/questions", "method": "GET"},
    "12": {"name": "Upload Image", "url": "http://127.0.0.1:8080/rest/upload_image", "method": "POST"},
    "13": {"name": "Download Image", "url": "http://127.0.0.1:8080/rest/media/{}", "method": "GET"},
    "14": {"name": "List All Images", "url": "http://127.0.0.1:8080/rest/media", "method": "GET"}

}

def send_request(method, url, data=None):
    """Envia requisições HTTP e imprime a resposta."""
    try:
        headers = {"Content-Type": "application/json"}

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
    """Handles user input and executes API calls accordingly."""
    for key, value in endpoints.items():
        print(f"{key}. [{value['method']}] {value['name']}")

    choice = input("\nEnter the number of the endpoint you want to use: ").strip()

    #print(f"👉 DEBUG: User chose option [{choice}]")  # 🛠️ Debugging print

    if choice in endpoints:
        #print(f"✅ DEBUG: Recognized option [{choice}] - {endpoints[choice]['name']}")
        url_template = endpoints[choice]["url"]
        method = endpoints[choice]["method"]
        url = url_template
        data = None

        if "{}" in url_template and choice not in ["6", "7", "8", "10", "11", "13"]:
            subject_id = input("Enter Subject ID: ")
            url = url_template.format(subject_id)

        elif choice == "4":  # Create Patient
            subject_id = input("Enter Subject ID: ")
            gender = input("Enter Gender (M/F): ").strip().upper()
            dob = input("Enter Date of Birth (YYYY-MM-DD): ").strip()
            data = {"subject_id": int(subject_id), "gender": gender, "dob": dob}

        elif choice == "5":  # Create Admission
            subject_id = input("Enter Subject ID: ")
            hadm_id = input("Enter Admission ID: ")
            admittime = input("Enter Admission Time (YYYY-MM-DD HH:MM:SS): ").strip()
            dischtime = input("Enter Discharge Time (YYYY-MM-DD HH:MM:SS): ").strip()
            diagnosis = input("Enter Diagnosis: ").strip()
            data = {"subject_id": int(subject_id), "hadm_id": int(hadm_id), "admittime": admittime,
                    "dischtime": dischtime, "diagnosis": diagnosis}

        elif choice == "6":  # Update Patient
            subject_id = input("Enter Subject ID: ")
            data = {}

            if input("Update Gender? (Y/N): ").strip().lower() == "y":
                data["gender"] = input("Enter New Gender (M/F): ").strip().upper()

            if input("Update Date of Birth? (Y/N): ").strip().lower() == "y":
                data["dob"] = input("Enter New Date of Birth (YYYY-MM-DD): ").strip() 

            if data:
                url = f"http://127.0.0.1:8080/rest/patients/{subject_id}"
            else:
                print("No updates provided.")
                return

        elif choice == "7":  # Delete Patient
            subject_id = input("Enter the ID of the patient to delete: ")
            url = url_template.format(subject_id)
            if input(f"⚠ Confirm deletion of patient {subject_id}? (yes/no): ").strip().lower() != "yes":
                print("❌ Operation cancelled.")
                return

        elif choice == "8":  # Delete Admission
            hadm_id = input("Enter the ID of the admission to delete: ")
            url = url_template.format(hadm_id)
            if input(f"⚠ Confirm deletion of admission {hadm_id}? (yes/no): ").strip().lower() != "yes":
                print("❌ Operation cancelled.")
                return
            
        elif choice == "10":  # Create Question
            subject_id = input("Enter Subject ID: ")
            user_name = input("Enter Your Name: ").strip()
            question_text = input("Enter Your Question: ").strip()

            data = {
                "subject_id": int(subject_id),
                "user_name": user_name,
                "question_text": question_text
            }

            # Enviar requisição POST para o Flask
            url = f"http://127.0.0.1:8080/rest/patients/{subject_id}/question"  # O endpoint para criar a questão
            
        elif choice == "11":  # Listar questões de um paciente
            subject_id = input("Enter Subject ID: ")
            url = url_template.format(subject_id)

        elif choice == "12":  # Upload Image
            subject_id = input("Enter Subject ID: ").strip()
            file_path = input("Enter the full path to the image file: ").strip().strip('"')  # Remove surrounding quotes

            try:
                with open(file_path, "rb") as image_file:
                    files = {"image": image_file}
                    data = {"subject_id": subject_id}
                    response = requests.post(url, files=files, data=data)

                print("\n✅ HTTP Status Code:", response.status_code)
                print("✅ Response:", response.json())

            except FileNotFoundError:
                print("\n❌ Error: File not found. Check the file path and try again.")
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                
        elif choice == "13":  # Image Download
            image_name = input("Enter the name of the image to download (e.g., xray1.jpg): ").strip()

            if not image_name:
                print("❌ Image name is required!")
            else:
                # Usando o link autenticado fornecido
                signed_url = f"https://storage.cloud.google.com/bdcc-imagebucket25/{image_name}"

                # Enviar a solicitação para baixar a imagem
                response = requests.get(signed_url, stream=True)

                if response.status_code == 200:
                    # Caminho onde a imagem será salva (na área de trabalho)
                    desktop_path = os.path.join(os.path.expanduser("~/Desktop"), image_name)

                    # Garantir que o diretório exista
                    os.makedirs(os.path.dirname(desktop_path), exist_ok=True)

                    # Salvar a imagem na área de trabalho
                    with open(desktop_path, "wb") as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)

                    print(f"✅ Image downloaded successfully! Saved at: {desktop_path}")
                else:
                    print(f"❌ Failed to download image. Status code: {response.status_code}")


        elif choice == "14":  # List All Images
            url = "http://127.0.0.1:8080/rest/images"

            response = requests.get(url)

            print("\n✅ HTTP Status Code:", response.status_code)
            print("✅ Raw Response Text:", response.text)

            if response.status_code == 200:
                try:
                    images = response.json()
                    if images:
                        print("\n📸 Uploaded Images:")
                        for img in images:
                            print(
                                f"🆔 Subject ID: {img['subject_id']} | 🖼 Image Name: {img['image_name']} | 🌍 URL: {img['image_url']}")
                    else:
                        print("\n⚠ No images found.")
                except json.decoder.JSONDecodeError:
                    print("\n❌ Error: Response is not valid JSON!")
            else:
                print("\n❌ Error retrieving images.")
                
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
