import requests
import time
import os
from datetime import datetime, timedelta

def generate_pdf(folder_name):
    try:
        requests.post("http://127.0.0.1:5001/api/analyze", json={"folder": folder_name})
        pdf = requests.get("http://127.0.0.1:5001/api/export_pdf")

        if pdf.status_code == 200:
            with open(f"{folder_name}.pdf", 'wb') as f:
                f.write(pdf.content)
            print(f"PDF saved: {folder_name}.pdf")
            return True
        else:
            print(f"Failed to generate PDF for {folder_name}. Status code: {pdf.status_code}")
            return False
    except Exception as e:
        print(f"Error generating PDF for {folder_name}: {e}")
        return False

def get_previous_day_folder():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def daily_pdf_generator():
    while True:
        now = datetime.now()

        if now.hour == 14 and now.minute == 40:
            # Move the folders in same directory to data folder
            start_time = time.time()
            print(f"Starting daily PDF generation at {now.strftime('%Y-%m-%d %H:%M:%S')}")

            previous_day_folder = get_previous_day_folder()
            print(f"Generating PDF for previous day: {previous_day_folder}")
            previous_day_folder = previous_day_folder.replace('-', '')

            print(f"Moving folder: {previous_day_folder}")
            os.rename(previous_day_folder, f"data/{previous_day_folder}")

            print(f"Using folder: {'data/' + previous_day_folder}")

            success = generate_pdf(previous_day_folder)
            if success:
                print(f"Successfully generated PDF for {previous_day_folder}")

                # Move the PDF to the previous day's folder
                os.rename(f"{previous_day_folder}.pdf", f"data/{previous_day_folder}/{previous_day_folder}.pdf")
                # Elapsed time
                print(f"Elapsed time: {time.time() - start_time} seconds")
            else:
                print(f"Failed to generate PDF for {previous_day_folder}")
            time.sleep(60)

        time.sleep(30)

if __name__ == "__main__":
    print("Starting daily PDF generator...")
    print("Will generate PDF every day at 20:00 for previous day's data")
    daily_pdf_generator()
    