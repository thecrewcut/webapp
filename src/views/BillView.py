#/src/views/BillView.py
from datetime import date
from flask import request, Blueprint, json, Response
from haikunator import Haikunator
from werkzeug.utils import secure_filename
from ..models.BillModel import BillModel, BillSchema
from ..models.UserModel import UserModel, UserSchema
from ..models.FileModel import FileModel, FileSchema
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
import hashlib, os, urllib.request, uuid

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

bill_api = Blueprint('bill_api', __name__)
user_schema = UserSchema()
bill_schema = BillSchema()
file_schema = FileSchema()
auth = HTTPBasicAuth()

@bill_api.route('/', methods=['POST'])
def create():
  """
  Create Bill Function
  """
  req_data = request.get_json(force = True)
  bill_data = bill_schema.load(req_data)
  new_uuid = uuid.uuid4()
  bill_data.update({'id': str(new_uuid)})
  email_address_in_auth_header = request.authorization.username
  user_object = UserModel.get_user_by_email(email_address_in_auth_header)
  user_id = user_object.id
  bill_data.update({'owner_id': user_id})
  bill_object = BillModel(bill_data)
  bill_object.save()
  ser_data = bill_schema.dump(bill_object)
  return custom_response(ser_data, 201)

@bill_api.route('/<string:bill_id>/file', methods=['POST'])
# @auth.login_required
def upload_file(bill_id):
  """
  Create File Function
  """
  # First check if bill id attempted to be attached to exists and belongs to user
  bill = BillModel.get_one_bill(bill_id)
  if not bill:
      return custom_response({'error': 'Bill Not Found'}, 404)
  email_address_in_auth_header = request.authorization.username
  user_object = UserModel.get_user_by_email(email_address_in_auth_header)
  user_id = user_object.id
  if (user_id != bill.owner_id):
      return custom_response({'error': 'Unauthorized Access to Bill'}, 401)

  # bill exists and belongs to user attempting to post file
  bill_data = bill_schema.dump(bill)

  # check if the post request has an attached file
  if 'file' not in request.files:
      custom_response({'error': 'No file part in the request'}, 400)

  file = request.files['file']

  if file.filename == '':
      custom_response({'error': 'No file selected for uploading'}, 400)

  if file and allowed_file(file.filename):

      result = File.select_file_by_bill_id(bill_id)
                print(result)
                if result:
                    return custom_http_code("file already exists with bill delete first",400)
                filename = secure_filename(file.filename)
                id=str(uuid.uuid4().hex)

	  filename = secure_filename(file.filename)
	  s3_url = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	  resp = jsonify({'message': 'File successfully uploaded', 'url': Haikunator().haikunate(delimiter = '.', token_hex = True, token_length = 6), 'hash_digest': hashlib.md5(file.stream.read()).hexdigest(), 'file_size': os.stat(filename).st_size, 'id':  uuid.uuid4(), 'upload_date': str(date.today()), 'file_name': filename, 'file_origin': str(os.path.abspath(filename))})
	  resp.status_code = 201
	  return resp

  else:
	  resp = jsonify({'message' : 'Allowed file types are pdf, png, jpg, jpeg'})
	  resp.status_code = 400
	  return resp





  new_uuid = uuid.uuid4()
  file_data.update({'id': str(new_uuid)})


  bill_data.update({'owner_id': user_id})
  bill_object = BillModel(bill_data)
  bill_object.save()
  ser_data = bill_schema.dump(bill_object)
  return custom_response(ser_data, 201)


@bill_api.route('/', methods=['GET'])
@auth.login_required
def get_all():
  """
  Get All Bills
  """
  email_address_in_auth_header = request.authorization.username
  user_object = UserModel.get_user_by_email(email_address_in_auth_header)
  user_id = user_object.id
  bills = BillModel.get_bills_by_owner_id(user_id)
  data = bill_schema.dump(bills, many = True)
  return custom_response(data, 200)

@bill_api.route('/<string:bill_id>', methods=['GET'])
@auth.login_required
def get_one(bill_id):
  """
  Get Authorized Bill
  """
  bill = BillModel.get_one_bill(bill_id)
  if not bill:
    return custom_response({'error': 'Bill Not Found'}, 404)
  email_address_in_auth_header = request.authorization.username
  user_object = UserModel.get_user_by_email(email_address_in_auth_header)
  user_id = user_object.id
  if (user_id != bill.owner_id):
      return custom_response({'error': 'Unauthorized Access to Bill'}, 401)
  data = bill_schema.dump(bill)
  return custom_response(data, 200)

@bill_api.route('/<string:bill_id>', methods=['PUT'])
@auth.login_required
def update(bill_id):
  """
  Update An Authorized Bill
  """
  req_data = request.get_json(force = True)
  bill = BillModel.get_one_bill(bill_id)
  if not bill:
    return custom_response({'error': 'Bill Not Found'}, 404)
  data = bill_schema.dump(bill)
  email_address_in_auth_header = request.authorization.username
  user_object = UserModel.get_user_by_email(email_address_in_auth_header)
  user_id = user_object.id
  if (data.get('owner_id') != user_id):
    return custom_response({'error': 'Permission Denied'}, 400)
  data_to_be_updated = bill_schema.load(req_data, partial = True)
  bill.update(data_to_be_updated)
  updated_date = bill_schema.dump(bill)
  return custom_response(updated_date, 200)

@bill_api.route('/<string:bill_id>', methods=['DELETE'])
@auth.login_required
def delete(bill_id):
  """
  Delete An Authorized Bill
  """
  bill = BillModel.get_one_bill(bill_id)
  if not bill:
    return custom_response({'error': 'Bill Not Found'}, 404)
  data = bill_schema.dump(bill)
  email_address_in_auth_header = request.authorization.username
  user_object = UserModel.get_user_by_email(email_address_in_auth_header)
  user_id = user_object.id
  if (data.get('owner_id') != user_id):
    return custom_response({'error': 'Unauthorized to Delete Bill'}, 401)
  bill.delete()
  return custom_response({'message': 'Deleted Successfully'}, 204)

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype = "application/json",
    response = json.dumps(res),
    status = status_code
  )

@auth.verify_password
def authenticate(username, password):
    if username and password:
        user_object = UserModel.get_user_by_email(username)
        authorized_boolean = user_object.check_hash(password)
        if not authorized_boolean:
            return False
        else:
            ser_user = user_schema.dump(user_object)
            return custom_response(ser_user, 200)
    return False
