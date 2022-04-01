from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
from tqdm import tqdm
import pdfplumber
import json
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Uploads')
CONVERTED_TO_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Converted_To_Txt')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_TO_TXT, exist_ok=True)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_TO_TXT'] = CONVERTED_TO_TXT

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
	""" 
	The function will check if the file has valid extentions that are in the ALLOWED_EXTENSIONS which is a set of allowed extensions. 

	Parameters
	----------
		filename: str 
			The file that you send will be passed here.

	Returns
	-------
        str:
            Splits the filename provided, and check if the extension is valid or not
    
    """
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
	"""
    This is a text conversion API. Call this API by posting a PDF file , which gets converted to text file
    and gets you back the file in .txt format. 
    
    Parameters:
    ----------
        POST:
            Upload the file on the client side and it will check if the filename is true according to the extensions allowed.
            And will convert the PDF format to the TXT format. Then it will go further by taking the text generated and will assign
            the NER tags according to the entities, by using the spacy ner en model i.e. en_core_web_md  
    Returns:
    -------

		json:
			If key "file" is not given properly, it will give back you the message saying 'No file provided/Check the key, spelling or any space after or in the key.'.
		json:
			If key "file" is empty, it will give back you the message saying 'No file selected.'.
		json:
		    If the vaule of key is not in pdf format, it will give back you the message saying 'file not allowed. Please send pdf format only.'.
		json:
			It will get you the data in txt format.  

	"""

	if request.method == 'POST':
		if 'file' not in request.files:
			return jsonify({"message": 'No file provided/Check the key, spelling or any space after or in the key.'})
		file = request.files['file']
		if file.filename == '':
			return jsonify({"message": 'No file selected.'})
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		else:
			return jsonify({"message": f'{file.filename} not allowed. Please send pdf format only.'})
	pages = {}
	text = pdfplumber.open(os.path.join(UPLOAD_FOLDER, file.filename))
	file_name = os.path.join(CONVERTED_TO_TXT, file.filename.replace('.pdf', '.txt'))
	if os.path.isfile(file_name):
		os.remove(file_name)
	txt_file = open(file_name, 'w', encoding='utf-8')
	for page in tqdm(text.pages):
		pages[f'page {page.page_number}'] = page.extract_text()
		txt_file.write(page.extract_text())
		txt_file.write('\n')
		txt_file.write('*' * 45)
		txt_file.write('\n')
	txt_file.close()
	with open(f'./{file.filename.replace(".pdf", ".json")}', 'w') as f:
		json.dump(pages, f)
	# print(pages['page 1'])
	return jsonify({"message": f'successfully uploaded', "contents": pages})

if __name__ == '__main__':
	app.run(port=5003, debug=True)

