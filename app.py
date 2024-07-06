from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from tensorflow import keras
import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import Color, HexColor, black
import datetime

app = Flask(__name__)

# Load the pre-trained model
model_path = os.path.join(os.path.dirname(__file__), 'Brain_Tumor_Model (2).h5')
model = keras.models.load_model(model_path)

# Define the upload folder
UPLOAD_FOLDER = os.path.join(app.root_path, 'frontend', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_pdf_report(name, gender, age, image_path, result_label):
    # Specify the absolute path for the PDF file
    pdf_path = os.path.join(UPLOAD_FOLDER, 'report.pdf')

    # Get current date
    current_date = datetime.datetime.now().strftime("%B %d, %Y")

    # Create a new PDF document
    pdf = Canvas(pdf_path, pagesize=letter)

    # Define colors
    title_color = HexColor("#1f77b4")  # Dark blue color for title
    text_color = black  # Black color for text
    description_color = HexColor("#6C926D")  # green color for description

    # Add content to the PDF
    pdf.setFillColor(title_color)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(300, 750, "Medical Report")
    pdf.setFillColor(black)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 720, "-------------------------------------------------------------------------------------------------------------------------------------")
    pdf.drawString(50, 690, f"Name: {name}")
    pdf.drawString(50, 670, f"Gender: {gender}")
    pdf.drawString(50, 650, f"Age: {age}")
    pdf.drawString(50, 630, f"Date: {current_date}")
    pdf.drawString(50, 610, f"Result: {result_label}")

    # If the result is brain tumor, include a description of the disease
    if result_label.lower() == 'glioma':
        pdf.setFillColor(description_color)
        pdf.drawString(50, 580, "Glioma Detected")
        pdf.drawString(50, 560, "Description of Glioma:")
        pdf.drawString(50, 540, "- Glioma is a type of brain tumor that arises from glial cells.")
        pdf.drawString(50, 520, "- Headaches,nausea and vomiting,changes in vision or hearing,cognitive changes.")
        pdf.drawString(50, 500, "- Treatment options include surgery, radiation,targeted and chemotherapy.")
    elif result_label.lower() == 'meningioma':
        pdf.setFillColor(description_color)
        pdf.drawString(50, 580, "Meningioma Detected")
        pdf.drawString(50, 560, "Description of Meningioma:")
        pdf.drawString(50, 540, "- Meningioma is a common, usually slow-growing tumor that forms in the meninges.")
        pdf.drawString(50, 520, "- Symptoms of meningioma include limb weakness,vision changes,hearing loss.")
        pdf.drawString(50, 500, "- Treatment options depend on the size and location of the tumor.")
    elif result_label.lower() == 'pituitary':
        pdf.setFillColor(description_color)
        pdf.drawString(50, 580, "Pituitary Tumor Detected")
        pdf.drawString(50, 560, "Description of Pituitary Tumor:")
        pdf.drawString(50, 540, "- Pituitary tumors are growths that develop in the pituitary gland.")
        pdf.drawString(50, 520, "- Symptoms may include vision changes, headaches, and hormonal imbalances.")
        pdf.drawString(50, 500, "- Treatment options include medication, surgery, and radiation therapy.")
    elif result_label.lower() == 'notumor':
        pdf.setFillColor(description_color)
        pdf.drawString(50, 580, "No Tumor Detected")
        pdf.drawString(50, 560, "No significant findings related to brain tumors.")
        pdf.drawString(50, 540, "Regular follow-up may be recommended for monitoring.")

    # Add the image to the PDF below the text
    pdf.drawImage(image_path, x=100, y=100, width=300, height=300)

    # Save the PDF file
    pdf.save()

    return pdf_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Capture user details
    name = request.form['name']
    gender = request.form['gender']
    age = request.form['age']
    
    # Check if the file is present in the request
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    # Check if a file is selected
    if file.filename == '':
        return redirect(request.url)

    # Check if the file has an allowed extension
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the file to the upload folder
        file.save(file_path)

        try:
            # Preprocess the image
            img = Image.open(file_path)
            img = img.resize((512, 512))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Make prediction
            predictions = model.predict(img_array)

            # Get the predicted class
            predicted_class = np.argmax(predictions)
            image_types = ["glioma", "meningioma", "notumor", "pituitary"]
            predicted_label = image_types[predicted_class]

            # Construct result message
            result_message = f'The model predicts: {predicted_label}'
            print(f'Predicted label: {predicted_label}')
            print(f'Filename: {filename}')

            # Generate PDF report
            pdf_path = generate_pdf_report(name, gender, age, file_path, predicted_label)

            # Render result page with result message
            result_image_path = os.path.join('static', 'result.jpg')  # Update with your result image path
            return render_template('result.html', result_message=result_message, name=name, gender=gender, age=age, result_image=result_image_path, pdf_path=pdf_path)

        except Exception as e:
            # Handle any exceptions
            print(f'Error processing image: {str(e)}')
            return render_template('index.html', message=f'Error processing image: {str(e)}')

    else:
        # Handle invalid file format
        return render_template('index.html', message='Invalid file format')

@app.route('/download_report')
def download_report():
    # Specify the path to the PDF report
    pdf_path = request.args.get('pdf_path')
    
    # Send the PDF file for download
    return send_from_directory(os.path.dirname(pdf_path), os.path.basename(pdf_path), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
