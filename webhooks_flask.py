from flask import Flask, request, jsonify
import os
from shotgun_api3 import Shotgun

app = Flask(__name__)

# Shotgun API 설정
URL = "https://4thacademy.shotgrid.autodesk.com"
SCRIPT_NAME = "test_hyo"
API_KEY = "ljbgffxqg@cejveci5dQebhdx"
SECRET_TOKEN = "your_webhook_secret_token"  # 웹훅 시크릿 토큰

base_path = "/home/rapa/YUMMY"

def connect_sg():
    """Shotgun (ShotGrid) API에 연결합니다."""
    return Shotgun(URL, SCRIPT_NAME, API_KEY)

def get_user_by_email(sg, email):
    """이메일로 사용자 정보를 검색합니다."""
    filters = [["email", "is", email]]
    fields = ["id", "name", "email"]
    users = sg.find("HumanUser", filters=filters, fields=fields)
    return users[0] if users else None

def get_tasks_by_user(sg, user_id):
    """사용자 ID로 작업을 검색합니다."""
    filters = [["task_assignees", "is", {"type": "HumanUser", "id": user_id}]]
    fields = ["project", "entity", "step", "content"]
    return sg.find("Task", filters=filters, fields=fields)

def get_project_names_from_tasks(sg, tasks):
    """작업 목록으로부터 프로젝트 이름을 가져옵니다."""
    project_ids = {task.get("project", {}).get("id") for task in tasks if task.get("project")}
    if not project_ids:
        return {}
    
    filters = [["id", "in", list(project_ids)]]
    fields = ["name"]
    projects = sg.find("Project", filters=filters, fields=fields)
    return {proj.get("id"): proj.get("name") for proj in projects if proj.get("id") and proj.get("name")}

def get_shots_and_steps_from_tasks(tasks):
    """작업 목록으로부터 샷과 스텝 정보를 가져옵니다."""
    shot_steps = {}
    for task in tasks:
        entity = task.get("entity")
        step = task.get("step")
        content = task.get("content")
        if entity and entity.get("type") == "Shot":
            shot_code = entity.get("name")
            step_name = step.get("name")
            if shot_code not in shot_steps:
                shot_steps[shot_code] = []
            shot_steps[shot_code].append({"step": step_name, "task": content})
    return shot_steps

def get_sequences_from_projects(sg, project_ids):
    """프로젝트 ID 목록으로부터 시퀀스를 가져옵니다."""
    project_sequences = {}
    for project_id in project_ids:
        filters = [["project", "is", {"type": "Project", "id": project_id}]]
        fields = ["id", "code", "shots"]
        sequences = sg.find("Sequence", filters=filters, fields=fields)
        seq_data = [{"id": seq.get("id"), "code": seq.get("code"), "shots": seq.get("shots", [])} for seq in sequences]
        project_sequences[project_id] = seq_data
    return project_sequences

def get_shot_codes_for_sequences(sequences):
    """시퀀스 목록으로부터 샷 코드를 가져옵니다."""
    seq_shot_codes = {}
    for sequence in sequences:
        seq_code = sequence.get("code")
        if seq_code:
            shots = sequence.get("shots", [])
            shot_codes = [shot.get("name") for shot in shots if shot.get("name")]
            seq_shot_codes[seq_code] = shot_codes
    return seq_shot_codes

def get_asset_types_from_projects(sg, project_ids):
    """프로젝트 ID 목록으로부터 자산 유형을 가져옵니다."""
    project_asset_types = {}
    for project_id in project_ids:
        filters = [["project", "is", {"type": "Project", "id": project_id}]]
        fields = ["id", "code", "sg_asset_type"]
        assets = sg.find("Asset", filters=filters, fields=fields)
        asset_types = {asset.get("sg_asset_type") for asset in assets if asset.get("sg_asset_type")}
        project_asset_types[project_id] = list(asset_types)
    return project_asset_types

def create_folders(base_path, project_names, project_asset_types, project_sequences, seq_shot_codes, shot_steps):
    """폴더를 생성합니다."""
    folders = []

    for project_id, project_name in project_names.items():
        folders.extend([
            f"project/{project_name}/I_O/input/plate/exr",
            f"project/{project_name}/I_O/input/plate/mov",
            f"project/{project_name}/I_O/output/plate/exr",
            f"project/{project_name}/I_O/output/plate/mov",
            f"project/{project_name}/template/asset",
            f"project/{project_name}/template/shot/clip_lib",
            f"project/{project_name}/template/shot/node_tem",
            "pipeline/scripts"
        ])

        asset_types = project_asset_types.get(project_id, [])
        for asset_type in asset_types:
            asset_type_path = f"project/{project_name}/asset/{asset_type}"
            folders.append(asset_type_path)
            mod_path = os.path.join(asset_type_path, "mod")
            rig_path = os.path.join(asset_type_path, "rig")
            folders.extend([mod_path, rig_path])
            folders.extend([
                os.path.join(mod_path, "dev"),
                os.path.join(mod_path, "pub"),
                os.path.join(rig_path, "dev"),
                os.path.join(rig_path, "pub")
            ])

        sequences = project_sequences.get(project_id, [])
        for sequence in sequences:
            seq_code = sequence.get("code")
            if seq_code:
                seq_path = f"project/{project_name}/seq/{seq_code}"
                folders.append(seq_path)
                shot_codes = seq_shot_codes.get(seq_code, [])
                for shot_code in shot_codes:
                    shot_path = os.path.join(seq_path, shot_code)
                    folders.append(shot_path)
                    steps_for_shot = shot_steps.get(shot_code, [])
                    for step_info in steps_for_shot:
                        step_name = step_info.get("step")
                        if step_name:
                            step_path = os.path.join(shot_path, step_name)
                            folders.append(step_path)
                            folders.extend([
                                os.path.join(step_path, "dev"),
                                os.path.join(step_path, "pub"),
                                os.path.join(step_path, "dev/exr"),
                                os.path.join(step_path, "dev/mov"),
                                os.path.join(step_path, "dev/work")
                            ])

    for folder in folders:
        path = os.path.join(base_path, folder)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"{path} 폴더가 생성되었습니다.")
        else:
            print(f"{path} 폴더가 이미 존재합니다.")
    
    return folders

@app.route('/webhook', methods=['POST'])
def webhook():
    """웹훅 요청을 처리합니다."""
    token = request.headers.get('X-Hub-Signature')
    if token != SECRET_TOKEN:
        return jsonify({'status': 'failure', 'message': 'Invalid token'}), 403

    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'status': 'failure', 'message': 'Email not found in payload'}), 400
    
    try:
        sg = connect_sg()
        user = get_user_by_email(sg, email)
        
        if user:
            user_id = user.get("id")
            if user_id:
                tasks = get_tasks_by_user(sg, user_id)
                project_names = get_project_names_from_tasks(sg, tasks)
                project_ids = list(project_names.keys())
                project_sequences = get_sequences_from_projects(sg, project_ids)
                all_sequences = [seq for sequences in project_sequences.values() for seq in sequences]
                seq_shot_codes = get_shot_codes_for_sequences(all_sequences)
                project_asset_types = get_asset_types_from_projects(sg, project_ids)
                shot_steps = get_shots_and_steps_from_tasks(tasks)
                create_folders(base_path, project_names, project_asset_types, project_sequences, seq_shot_codes, shot_steps)
                return jsonify({'status': 'success', 'message': 'Folders created successfully'}), 200
            else:
                return jsonify({'status': 'failure', 'message': 'User ID not found'}), 404
        else:
            return jsonify({'status': 'failure', 'message': 'User not found'}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'failure', 'message': 'An error occurred'}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
