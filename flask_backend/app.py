from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
import csv

app = Flask(__name__)

@app.route('/allocate', methods=['GET'])
def allocate_rooms():
    group_file_path = request.args.get('groupFilePath')
    hostel_file_path = request.args.get('hostelFilePath')

    if not group_file_path or not hostel_file_path:
        return jsonify({"error": "Missing file paths"}), 400

    groups = pd.read_csv(group_file_path)
    hostels = pd.read_csv(hostel_file_path)

    allocation_results = []
    hostel_dict = {}
    
    for _, row in hostels.iterrows():
        if row['Hostel Name'] not in hostel_dict:
            hostel_dict[row['Hostel Name']] = []
        hostel_dict[row['Hostel Name']].append({
            'Room Number': row['Room Number'],
            'Capacity': row['Capacity'],
            'Gender': row['Gender'],
            'Occupied': 0
        })

    for _, group in groups.iterrows():
        group_id = group['Group ID']
        members = group['Members']
        gender = group['Gender']
        
        allocated = False
        for hostel_name, rooms in hostel_dict.items():
            if allocated:
                break
            for room in rooms:
                if room['Gender'] == gender and room['Occupied'] + members <= room['Capacity']:
                    allocation_results.append({
                        'groupId': group_id,
                        'hostelName': hostel_name,
                        'roomNumber': room['Room Number'],
                        'membersAllocated': members
                    })
                    room['Occupied'] += members
                    allocated = True
                    break

    allocation_file_path = 'uploads/allocation_results.csv'
    with open(allocation_file_path, 'w', newline='') as csvfile:
        fieldnames = ['groupId', 'hostelName', 'roomNumber', 'membersAllocated']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in allocation_results:
            writer.writerow(result)

    return jsonify({"allocationResults": allocation_results, "filePath": allocation_file_path})

@app.route('/download', methods=['GET'])
def download_file():
    file_path = request.args.get('filePath')
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
