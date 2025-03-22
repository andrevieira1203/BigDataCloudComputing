import webbrowser
import requests
import json
import os

# Endpoint dictionary organized by table
endpoints = {
    # USERS Endpoints
    "Users": {
        "1": {"name": "Get Patient Details", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "GET"},
        "3": {"name": "Get Patients with Longest Stays", "url": "http://127.0.0.1:8080/rest/patients/longest_stays", "method": "GET"},
        "4": {"name": "Create a New Patient", "url": "http://127.0.0.1:8080/rest/patients", "method": "POST"},
        "6": {"name": "Update Patient Details", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "PUT"},
        "7": {"name": "Delete a Patient", "url": "http://127.0.0.1:8080/rest/patients/{}", "method": "DELETE"},
        "9": {"name": "List All Patients", "url": "http://127.0.0.1:8080/rest/patients", "method": "GET"},
    },
    
    # Admissions Endpoints
    "Admissions": {
        "2": {"name": "Get Admissions for a Patient", "url": "http://127.0.0.1:8080/rest/admissions/{}", "method": "GET"},
        "5": {"name": "Create a New Admission", "url": "http://127.0.0.1:8080/rest/admissions", "method": "POST"},
        "8": {"name": "Delete an Admission", "url": "http://127.0.0.1:8080/rest/admissions/{}", "method": "DELETE"},
    },
    
    # Media Endpoints
    "Media": {
        "12": {"name": "Upload Image", "url": "http://127.0.0.1:8080/rest/upload_image", "method": "POST"},
        "13": {"name": "Download Image", "url": "http://127.0.0.1:8080/rest/media/{}", "method": "GET"},
        "14": {"name": "List All Images", "url": "http://127.0.0.1:8080/rest/media", "method": "GET"},
    },

    # Progress Endpoints
    "Progress": {
        "15": {"name": "Create Progress Record", "url": "http://127.0.0.1:8080/rest/progress", "method": "POST"},
        "16": {"name": "List Progress Records for a Patient", "url": "http://127.0.0.1:8080/rest/patients/{}/progress", "method": "GET"},
    },

    # Questions Endpoints
    "Questions": {
        "10": {"name": "Create a Question", "url": "http://127.0.0.1:8080/rest/patients/{}/question", "method": "POST"},
        "11": {"name": "List Questions for a Patient", "url": "http://127.0.0.1:8080/rest/patients/{}/questions", "method": "GET"},
    }
}

def send_request(method, url, data=None):
    """Endpoint dictionary organized by table."""
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
    print("Select a category of endpoints:")
    
    # Display categories
    categories = list(endpoints.keys())
    for idx, category in enumerate(categories, 1):
        print(f"{idx}. {category}")

    choice = input("\nEnter the number of the category you want to use: ").strip()

    # If choice is valid, proceed
    if choice.isdigit() and 1 <= int(choice) <= len(categories):
        selected_category = categories[int(choice) - 1]
        print(f"\nYou have selected the {selected_category} category.")
        
        # Show endpoints of the selected category
        print("\nSelect an endpoint:")
        category_endpoints = endpoints[selected_category]
        for key, value in category_endpoints.items():
            print(f"{key}. {value['name']}")

        endpoint_choice = input("\nEnter the number of the endpoint you want to use: ").strip()

        # Find selected endpoint
        if endpoint_choice in category_endpoints:
            url_template = category_endpoints[endpoint_choice]["url"]
            method = category_endpoints[endpoint_choice]["method"]
            url = url_template
            data = None

            # Input logic for specific endpoint
            if "{}" in url_template and endpoint_choice not in ["8","10", "16"]:
                subject_id = input("Enter Subject ID: ")
                url = url_template.format(subject_id)

            # Handle the logic for the required data depending on the endpoint
            if endpoint_choice == "4":  # Create Patient
                subject_id = input("Enter Subject ID: ")
                gender = input("Enter Gender (M/F): ").strip().upper()
                dob = input("Enter Date of Birth (YYYY-MM-DD): ").strip()
                data = {"subject_id": int(subject_id), "gender": gender, "dob": dob}
                
            elif endpoint_choice == "6":  # Update Patient
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
                
            elif endpoint_choice == "8":  # Delete Admission
                hadm_id = input("Enter the ID of the admission to delete: ")
                url = url_template.format(hadm_id)
                if input(f"⚠ Confirm deletion of admission {hadm_id}? (yes/no): ").strip().lower() != "yes":
                    print("❌ Operation cancelled.")
                    return

            elif endpoint_choice == "5":  # Create Admission
                subject_id = input("Enter Subject ID: ")
                hadm_id = input("Enter Admission ID: ")
                admittime = input("Enter Admission Time (YYYY-MM-DD HH:MM:SS): ").strip()
                dischtime = input("Enter Discharge Time (YYYY-MM-DD HH:MM:SS): ").strip()
                diagnosis = input("Enter Diagnosis: ").strip()
                data = {"subject_id": int(subject_id), "hadm_id": int(hadm_id), "admittime": admittime,
                        "dischtime": dischtime, "diagnosis": diagnosis}
                
            elif endpoint_choice == "10":  # Create Question
                subject_id = input("Enter Subject ID: ")
                user_name = input("Enter Your Name: ").strip()
                question_text = input("Enter Your Question: ").strip()

                data = {
                    "subject_id": int(subject_id),
                    "user_name": user_name,
                    "question_text": question_text
                }

                # Send POST request to Flask
                url = f"http://127.0.0.1:8080/rest/patients/{subject_id}/question"  # The endpoint to create the issue
                
            elif endpoint_choice == "12":  # Upload Image
                subject_id = input("Enter Subject ID: ").strip()
                file_path = input("Enter the full path to the image file: ").strip().strip('"') 

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
                
            elif endpoint_choice == "13":  # Image Download
                image_name = input("Enter the name of the image to download (e.g., xray1.jpg): ").strip()

                if not image_name:
                    print("❌ Image name is required!")
                else:
                    # Using the provided authenticated link
                    signed_url = f"https://storage.cloud.google.com/bdcc-imagebucket25/{image_name}"

                    # Send the request to download the image
                    response = requests.get(signed_url, stream=True)

                    if response.status_code == 200:
                        # Path where the image will be saved (on the desktop)
                        desktop_path = os.path.join(os.path.expanduser("~/Desktop"), image_name)

                        # Ensure the directory exists
                        os.makedirs(os.path.dirname(desktop_path), exist_ok=True)

                        # Save the image to your desktop
                        with open(desktop_path, "wb") as file:
                            for chunk in response.iter_content(1024):
                                file.write(chunk)

                        print(f"✅ Image downloaded successfully! Saved at: {desktop_path}")
                    else:
                        print(f"❌ Failed to download image. Status code: {response.status_code}")
                
            elif endpoint_choice == "14":  # List All Images
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

            elif endpoint_choice == "15":  # Create Progress
                subject_id = input("Enter Subject ID: ")
                hadm_id = input("Enter Admission ID: ")
                itemid = input("Enter Item ID: ")
                starttime = input("Enter Start Time (YYYY-MM-DD HH:MM:SS): ").strip()
                endtime = input("Enter End Time (YYYY-MM-DD HH:MM:SS): ").strip()
                amount = input("Enter Amount: ").strip()
                amountuom = input("Enter Amount Unit of Measure: ").strip()
                statusdescription = input("Enter Status Description: ").strip()
                cgid = input("Enter Caregiver ID: ").strip()

                data = {
                    "subject_id": int(subject_id),
                    "hadm_id": int(hadm_id),
                    "itemid": int(itemid),
                    "starttime": starttime,
                    "endtime": endtime,
                    "amount": float(amount),
                    "amountuom": amountuom,
                    "cgid": int(cgid),
                    "statusdescription": statusdescription
                }

            elif endpoint_choice == "16":  # List Progress for Patient
                subject_id = input("Enter Subject ID: ")
                url = url_template.format(subject_id)

            # Send the request based on the method
            if method in ["POST", "PUT", "DELETE"]:
                send_request(method, url, data)
            else:
                print(f"\nOpening: {url}")
                webbrowser.open_new_tab(url)
        else:
            print("❌ Invalid endpoint choice.")
    else:
        print("❌ Invalid category choice.")


while True:
    get_user_choice()
    if input("\nTest another endpoint? (y/n): ").strip().lower() != "y":
        print("Exiting...")
        break
