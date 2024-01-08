import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(
    "/Users/adityarana/Documents/Sayge/Softwares/Saasify/Configurations/saasify-de974-firebase-adminsdk-q7lul-676812efed.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def master_config():
    modules = {
        "HRMS": {
            "name": "HRMS",
            "baseCost": 2000,
        },
        "POS": {
            "name": "POS",
            "baseCost": 1000,
        },
        "Inventory Management": {
            "name": "Inventory Management",
            "baseCost": 1000,
        },
        "Finance": {
            "name": "Finance",
            "baseCost": 500,
        },
    }

    for module_id, module_data in modules.items():
        module_ref = db.collection("modules").document(module_id)
        module_ref.set(module_data)

    print("Master configuration successfully created in Firestore!")


def add_firebase_client(clientId: str):
    new_client_ref = db.collection("clients").document(clientId)
    client_data = {}
    selected_modules = ["HRMS", "POS"]

    for module_id in selected_modules:
        module_ref = db.collection("modules").document(module_id)
        module_data = module_ref.get().to_dict()
        if module_data:
            client_data[module_id] = {
                "name": module_data.get("name", ""),
                "baseCost": module_data.get("baseCost", 0)}

    new_client_ref.set(client_data)
