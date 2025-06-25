import json

from flask import current_app, request, jsonify, g

from Main.database import User, Project, DetectionData
from Main.utils.commons import login_required
from Main.utils.response_code import RET
from . import index


@index.route('/project', methods=['GET'])
@login_required
def get_project():
    try:
        user = User.query.get(g.user_id)
    except Exception as e:
        current_app.logger.error(f"Database query failed: {e}")
        return jsonify(re_code=RET.DBERR, msg='Database query failed')

    if not user:
        return jsonify(re_code=RET.NODATA, msg='User does not exist')

    projects = []
    for project in user.projects:
        project_info = {
            'project_name': project.project_name,
            'created_at': project.created_at,
            'source_path': project.source_path,
        }
        projects.append(project_info)

    return jsonify(re_code=RET.OK, msg='Query successful', projects=projects)


@index.route('/project/details', methods=['POST'])
@login_required
def get_project_details():
    data = request.get_json()
    if not data or 'project_name' not in data:
        current_app.logger.error('Project name is required')
        return jsonify(re_code=RET.PARAMERR, msg='Project name is required')
    project_name = data['project_name']

    try:
        user = User.query.get(g.user_id)
    except Exception as e:
        current_app.logger.error(f"Database query failed: {e}")
        return jsonify(re_code=RET.DBERR, msg='Database query failed')

    if not user:
        current_app.logger.error('User does not exist')
        return jsonify(re_code=RET.NODATA, msg='User does not exist')

    project = Project.query.filter_by(project_name=project_name, user_id=g.user_id).first()
    if not project:
        current_app.logger.error('Project does not exist')
        return jsonify(re_code=RET.NODATA, msg='Project does not exist')

    detection_data = DetectionData.query.filter_by(project_id=project.project_id).all()
    detection_results = []
    for data in detection_data:
        detection_results.append(data.results)

    result = {
        'project_name': project.project_name,
        'created_at': project.created_at,
        'scenario': project.scenario,
        'scale': project.scale,
        'conf_threshold': project.conf_threshold,
        'source_path': project.source_path,
        'result_path': project.result_path,
        'detection_data': detection_results,
    }
    # print(json.dumps(result, indent=4, ensure_ascii=False))

    return jsonify(re_code=RET.OK, msg='Query successful', result=result)
