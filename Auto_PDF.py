import requests
import time
import os
from datetime import datetime, timedelta

def generate_pdf(folder_name):
    try:
        analyze_response = requests.post("http://127.0.0.1:5001/api/analyze", json={"folder": folder_name}, timeout=300)

        if analyze_response.status_code != 200:
            print(f"Analysis failed for {folder_name}. Status code: {analyze_response.status_code}")
            return False

        pdf = requests.get("http://127.0.0.1:5001/api/export_pdf", timeout=300)

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
        try:
            now = datetime.now()

            if now.hour == 20 and now.minute == 00:
                # Move the folders in same directory to data folder
                start_time = time.time()
                print(f"Starting daily PDF generation at {now.strftime('%Y-%m-%d %H:%M:%S')}")

                previous_day_folder = get_previous_day_folder()
                print(f"Generating PDF for previous day: {previous_day_folder}")
                previous_day_folder = previous_day_folder.replace('-', '')

                # Move folder to data directory
                print(f"Moving folder: {previous_day_folder}")
                if os.path.exists(previous_day_folder):
                    dest_path = f"data/{previous_day_folder}"
                    if os.path.exists(dest_path):
                        print(f"Destination folder already exists: {dest_path}")
                    else:
                        os.rename(previous_day_folder, dest_path)
                        print(f"Folder moved to: {dest_path}")
                else:
                    print(f"Source folder does not exist: {previous_day_folder}")

                print(f"Using folder: {'data/' + previous_day_folder}")

                success = generate_pdf(previous_day_folder)
                if success:
                    print(f"Successfully generated PDF for {previous_day_folder}")

                    # Move the PDF to the previous day's folder
                    pdf_src = f"{previous_day_folder}.pdf"
                    pdf_dest = f"data/{previous_day_folder}/{previous_day_folder}.pdf"
                    if os.path.exists(pdf_src):
                        os.makedirs(f"data/{previous_day_folder}", exist_ok=True)
                        if os.path.exists(pdf_dest):
                            os.remove(pdf_dest)
                        os.rename(pdf_src, pdf_dest)
                        print(f"PDF moved to: {pdf_dest}")
                    # Elapsed time
                    print(f"Elapsed time: {time.time() - start_time} seconds")
                else:
                    print(f"Failed to generate PDF for {previous_day_folder}")
                time.sleep(60)

        except Exception as e:
            print(f"Error in daily_pdf_generator loop: {e}")
            time.sleep(60)

        time.sleep(30)

if __name__ == "__main__":
    print("Starting daily PDF generator...")
    print("Will generate PDF every day at 20:00 for previous day's data")
    daily_pdf_generator()
    