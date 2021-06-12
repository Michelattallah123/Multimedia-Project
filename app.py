from flask import Flask,request,render_template
from flask_sqlalchemy import SQLAlchemy
from helper_functions import *
from sqlalchemy import ForeignKey
import os
import numpy as np
import cv2
import io
import json
import numpy as np
file_directory = os.getenv('FILE_PATH')
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/multimedia'

#============================#
#====== Database Setup ======#
#============================#

db = SQLAlchemy(app)
class Images(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    histogram_r = db.Column(db.Text)
    histogram_g = db.Column(db.Text)
    histogram_b = db.Column(db.Text)
    gabor_histogram = db.Column(db.Text)
    mean_color = db.Column(db.String(100))
    name = db.Column(db.String(40))
    
    def serialize(self):
        return {
                'id' : self.id,
                'name': self.name,
                'histogram_r' : self.histogram_r,
                'histogram_g' : self.histogram_g,
                'histogram_b' : self.histogram_b,
                'gabor_histogram' : self.gabor_histogram,
                'mean_color': self.mean_color
            }

    def insert(self):
        db.session.add(self)
        db.session.commit()

class Videos(db.Model):
    __tablename__ = "videos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    def serialize(self):
        return {
            'id' : self.id,
            'name': self.name
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

class KeyFrames(db.Model):
    __tablename__ = "key_frames"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer,ForeignKey('videos.id', ondelete='CASCADE', onupdate="CASCADE"))
    histogram_r = db.Column(db.Text)
    histogram_g = db.Column(db.Text)
    histogram_b = db.Column(db.Text)

    def serialize(self):
        return {
                'id' : self.id,
                'video_id': self.video_id,
                'histogram_r' : self.histogram_r,
                'histogram_g' : self.histogram_g,
                'histogram_b' : self.histogram_b,
            }

    def insert(self):
        db.session.add(self)
        db.session.commit()
    

db.create_all()


#============================#
#========== Routes ==========#
#============================#

@app.route('/upload_image', methods=['POST'])
def upload_image():
    # image formatting to numpy array
    image = request.files['file']
    image_name = image.filename
    #convert image to numpy
    numpy_image = convert_image_numpy(image)
    #calculate all params
    data = calculate_all_params(numpy_image)
    # storing image in database
    save_image(numpy_image,data,image_name,Images)
    return render_template('index.html',file_type="Image")

@app.route('/histogram',methods=['POST'])
def compare_histogram():
    # image formatting to numpy array
    image = request.files['file']
    image_name = image.filename
    #convert image to numpy
    numpy_image = convert_image_numpy(image)
    # calculate all params
    data = calculate_all_params(numpy_image)
    # compare histogram
    histograms = Images.query.all()
    histograms_formatted = []
    for hist in histograms:
        hist = hist.serialize()
        if('e' in hist['histogram_r']):
            hist['histogram_r'] = np.array([np.array(x) for x in json.loads(hist['histogram_r'].replace("'", '"'))],dtype="float32")
        else:
            hist['histogram_r'] = np.array([np.array(x) for x in json.loads(hist['histogram_r'].replace("'", '"').replace('.','.0'))],dtype="float32")
        if('e' in ['histogram_g']):
            hist['histogram_g'] = np.array([np.array(x) for x in json.loads(hist['histogram_g'].replace("'", '"'))],dtype="float32")
        else:
            hist['histogram_g'] = np.array([np.array(x) for x in json.loads(hist['histogram_g'].replace("'", '"').replace('.','.0'))],dtype="float32")
        if('e' in ['histogram_b']):
            hist['histogram_b'] = np.array([np.array(x) for x in json.loads(hist['histogram_b'].replace("'", '"'))],dtype="float32")
        else:
            hist['histogram_b'] = np.array([np.array(x) for x in json.loads(hist['histogram_b'].replace("'", '"').replace('.','.0'))],dtype="float32")
        histograms_formatted.append(hist)
    list_of_similar_images = comparing_using_histo(data['histogram'],histograms_formatted)
    list_of_similar_images_filtered = []
    for index in list_of_similar_images:
        img_id = str(index['id'])
        file_type=index['name'].split('.')[1]
        list_of_similar_images_filtered.append(f"{img_id}.{file_type}")
    # storing image in database
    save_image(numpy_image,data,image_name,Images)
    return(render_template('results.html',data=list_of_similar_images_filtered,file_type="Image"))

@app.route('/mean_color',methods=['POST'])
def compare_mean_color():
    # image formatting to numpy array
    image = request.files['file']
    image_name = image.filename
    #convert image to numpy
    numpy_image = convert_image_numpy(image)
    #calculate all params
    data = calculate_all_params(numpy_image)
    mean_colors = Images.query.all()
    mean_colors_formatted = []
    for mean_color in mean_colors:
        mean_color = mean_color.serialize()
        mean_color['mean_color'] = np.array(json.loads(mean_color['mean_color']),dtype="float32")
        mean_colors_formatted.append(mean_color)
    list_of_similar_images= comparing_using_mean_color(data['mean_color'],mean_colors_formatted)
    list_of_similar_images_filtered = []
    for index in list_of_similar_images:
        img_id = str(index['id'])
        file_type=index['name'].split('.')[1]
        list_of_similar_images_filtered.append(f"{img_id}.{file_type}")

    save_image(numpy_image,data,image_name,Images)
    return(render_template('results.html',data=list_of_similar_images_filtered,file_type="Image"))

@app.route('/seed_videos',methods=['POST'])
def seed():
    seed = video_seed("C:/Users/3/Downloads",Videos,KeyFrames)
    return {"Seed posted successfuly."}

@app.route('/compare_videos',methods=['POST'])
def compare_videos():
    video = request.files['file']
    video_name= video.filename.split('.')[0]
    video_extension= video.filename.split('.')[1]
    all_videos = Videos.query.all()
    video_data = save_video(Videos,KeyFrames,video_name,video_extension,video)
    similar_videos = []
    histograms_formatted = []
    list_of_similar_videos_filtered=[]
    for vid in all_videos:
        vid = vid.serialize()
        all_key_frames = KeyFrames.query.filter(KeyFrames.video_id==vid['id']).all()
        all_key_frames = [key_frame.serialize() for key_frame in all_key_frames]
        for hist in all_key_frames:
            if('e' in hist['histogram_r']):
                hist['histogram_r'] = np.array([np.array(x) for x in json.loads(hist['histogram_r'].replace("'", '"'))],dtype="float32")
            else:
                hist['histogram_r'] = np.array([np.array(x) for x in json.loads(hist['histogram_r'].replace("'", '"').replace('.','.0'))],dtype="float32")
            if('e' in ['histogram_g']):
                hist['histogram_g'] = np.array([np.array(x) for x in json.loads(hist['histogram_g'].replace("'", '"'))],dtype="float32")
            else:
                hist['histogram_g'] = np.array([np.array(x) for x in json.loads(hist['histogram_g'].replace("'", '"').replace('.','.0'))],dtype="float32")
            if('e' in ['histogram_b']):
                hist['histogram_b'] = np.array([np.array(x) for x in json.loads(hist['histogram_b'].replace("'", '"'))],dtype="float32")
            else:
                hist['histogram_b'] = np.array([np.array(x) for x in json.loads(hist['histogram_b'].replace("'", '"').replace('.','.0'))],dtype="float32")
            histograms_formatted.append(hist)
        if(compare_keyframe_with_other_keyframes(video_data['list_of_histograms'], histograms_formatted)):
            vid_id = str(vid['id'])
            file_type=vid['name'].split('.')[1]
            list_of_similar_videos_filtered.append(f"{vid_id}.{file_type}")
            similar_videos.append(f"{vid_id}.{file_type}")
    return(render_template('results.html',data=list_of_similar_videos_filtered,file_type="Video"))
    

@app.route('/upload_video',methods=['POST'])
def upload_video():
    video = request.files['file']
    video_name= video.filename.split('.')[0]
    video_extension= video.filename.split('.')[1]
    all_videos = Videos.query.all()
    video_data = save_video(Videos,KeyFrames,video_name,video_extension,video)
    return render_template('index.html',file_type="Video")

@app.route('/compare_gabor',methods=['POST'])
def compare_gabor():
    # image formatting to numpy array
    image = request.files['file']
    image_name = image.filename
    #convert image to numpy
    numpy_image = convert_image_numpy(image)
    # calculate all params
    data = calculate_all_params(numpy_image)
    # compare histogram
    histograms = Images.query.all()
    histograms_formatted = []
    for hist in histograms:
        hist = hist.serialize()
        if('e' in hist['gabor_histogram']):
            hist['gabor_histogram'] = np.array([np.array(x) for x in json.loads(hist['gabor_histogram'].replace("'", '"'))],dtype="float32")
        else:
            hist['gabor_histogram'] = np.array([np.array(x) for x in json.loads(hist['gabor_histogram'].replace("'", '"').replace('.','.0'))],dtype="float32")
        histograms_formatted.append(hist)
    list_of_similar_images = comparing_using_gabor_histo(data['gabor_histogram'],histograms_formatted)
    list_of_similar_images_filtered = []
    for index in list_of_similar_images:
        img_id = str(index['id'])
        file_type=index['name'].split('.')[1]
        list_of_similar_images_filtered.append(f"{img_id}.{file_type}")
    # storing image in database
    save_image(numpy_image,data,image_name,Images)
    return(render_template('results.html',data=list_of_similar_images_filtered,file_type="Image"))

@app.route("/",methods=['GET'])
def index_page():
    return render_template('index.html')
    
@app.route("/results",methods=['GET'])
def results_page():
    return render_template('results.html')

if __name__ == "__main__":
    app.run(debug=True)

