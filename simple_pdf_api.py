import requests

def generate_pdf(folder_name):
    requests.post("http://127.0.0.1:5000/api/analyze", json={"folder": folder_name})
    pdf = requests.get("http://127.0.0.1:5000/api/export_pdf")

    with open(f"{folder_name}.pdf", 'wb') as f:
        f.write(pdf.content)

    print(f"PDF saved: {folder_name}.pdf")

# Usage: generate_pdf("your_folder_name")