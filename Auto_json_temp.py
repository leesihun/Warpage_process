import requests
import time
import os
from datetime import datetime, timedelta

def generate_pdf(folder_name):
    try:
        analyze_response = requests.post(
            "http://127.0.0.1:5001/api/analyze",
            json={"folder": folder_name},
            timeout=300
        )

        if analyze_response.status_code != 200:
            print(f"Analysis failed for {folder_name}. Status code: {analyze_response.status_code}")
            return False

        pdf_response = requests.get("http://127.0.0.1:5001/api/export_pdf", timeout=300)

        if pdf_response.status_code != 200:
            print(f"Failed to generate PDF for {folder_name}. Status code: {pdf_response.status_code}")
            return False

        pdf_path = f"{folder_name}.pdf"
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"PDF saved: {pdf_path}")

        stats_filename = f"{folder_name}_stats.json"
        json_response = requests.get(
            "http://127.0.0.1:5001/api/export_stats_json",
            params={"filename": stats_filename},
            timeout=300
        )

        if json_response.status_code != 200:
            print(f"Failed to generate statistics JSON for {folder_name}. Status code: {json_response.status_code}")
            return False

        with open(stats_filename, 'wb') as json_file:
            json_file.write(json_response.content)
        print(f"Statistics JSON saved: {stats_filename}")

        return True

    except Exception as e:
        print(f"Error generating reports for {folder_name}: {e}")
        return False

def get_previous_day_folder():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def daily_pdf_generator():
    while True:
        try:
            if True:
                # Move the folders in same directory to data folder
                start_time = time.time()
                previous_day_folder = './data/20250923'

                success = generate_pdf(previous_day_folder)
                if success:
                    print(f"Successfully generated reports for {previous_day_folder}")

                    # Ensure destination directory exists
                    os.makedirs(f"data/{previous_day_folder}", exist_ok=True)

                    # Move the PDF to the previous day's folder
                    pdf_src = f"{previous_day_folder}.pdf"
                    pdf_dest = f"data/{previous_day_folder}/{previous_day_folder}.pdf"
                    if os.path.exists(pdf_src):
                        if os.path.exists(pdf_dest):
                            os.remove(pdf_dest)
                        os.rename(pdf_src, pdf_dest)
                        print(f"PDF moved to: {pdf_dest}")

                    # Move the statistics JSON to the previous day's folder
                    json_src = f"{previous_day_folder}_stats.json"
                    json_dest = f"data/{previous_day_folder}/{previous_day_folder}_stats.json"
                    if os.path.exists(json_src):
                        if os.path.exists(json_dest):
                            os.remove(json_dest)
                        os.rename(json_src, json_dest)
                        print(f"Statistics JSON moved to: {json_dest}")

                    # Elapsed time
                    print(f"Elapsed time: {time.time() - start_time} seconds")
                else:
                    print(f"Failed to generate reports for {previous_day_folder}")
                time.sleep(60)

        except Exception as e:
            print(f"Error in daily_pdf_generator loop: {e}")
            time.sleep(60)

        time.sleep(30)

if __name__ == "__main__":
    print("Starting daily PDF generator...")
    print("Will generate PDF every day at 20:00 for previous day's data")
    daily_pdf_generator()
    
