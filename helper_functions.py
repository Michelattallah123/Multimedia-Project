import cv2
import matplotlib.pyplot as plt
import numpy as np
import io
import os
import shutil
from Katna.video import Video
from Katna.writer import KeyFrameDiskWriter
from gabor import Gabor
file_directory = os.getenv('FILE_PATH')
frame_number = 3

#Histogram
def compare_histo(histo1, histo2):
    diff = [cv2.compareHist(histo1[0], histo2['histogram_r'], cv2.HISTCMP_CORREL),
            cv2.compareHist(histo1[1], histo2['histogram_g'], cv2.HISTCMP_CORREL),
            cv2.compareHist(histo1[2], histo2['histogram_b'], cv2.HISTCMP_CORREL)]
    return diff

def comparing_using_histo(histogram, histograms):
    list_of_similar_images = []
    score = 0
    for histo in histograms:
        diffs = compare_histo(histogram, histo)
        for diff in diffs:
            if diff*100 > 30:
                score += 1
        if score > 1:
            list_of_similar_images.append(histo)
        score = 0
    return list_of_similar_images

#Mean color
def comparing_using_mean_color(mean_color, mean_colors):
    list_of_similar_images = []
    score = 0
    for mean in mean_colors:
        diffs = compare_mean_color(mean_color, mean)
        for diff in diffs:
            if diff < 50:
                score += 1
        if score > 2:
            list_of_similar_images.append(mean)
        score = 0
    return list_of_similar_images

def mean_color(img):
    red_channel = img[:, :, 2]
    blue_channel = img[:, :, 0]
    green_channel = img[:, :, 1]
    img_size = len(img[:, 0]) * len(img[0, :])
    R_mean = sum(map(sum, red_channel)) / img_size
    B_mean = sum(map(sum, blue_channel)) / img_size
    G_mean = sum(map(sum, green_channel)) / img_size
    meancolor = [R_mean, B_mean, G_mean]
    #print(meancolor)
    return meancolor


def compare_mean_color(mean1, mean2):
    diff = [abs(mean1[0] - mean2['mean_color'][0]), abs(mean1[1] - mean2['mean_color'][1]), abs(mean1[2] - mean2['mean_color'][2])]
    return diff

#Gabor
def compare_gabor_histo(histo1, histo2):
    diff = cv2.compareHist(histo1, histo2['gabor_histogram'], cv2.HISTCMP_CORREL)
            
    return diff

def comparing_using_gabor_histo(histogram, histograms):
    list_of_similar_images = []
    score = 0
    for histo in histograms:
        diffs = compare_gabor_histo(histogram, histo)
        if diffs*100 > 20:
            score = 1
        if score ==1:
            list_of_similar_images.append(histo)
        score = 0
    return list_of_similar_images

#Video
def key_frame_extraction(video_path, destination, no_of_frames_to_returned):
    vd = Video()
    no_of_frames_to_returned = int(no_of_frames_to_returned)
    diskwriter = KeyFrameDiskWriter(location=destination)
    video_file_path = os.path.join(video_path)
    vd.extract_video_keyframes(
        no_of_frames=no_of_frames_to_returned, file_path=video_file_path,
        writer=diskwriter
    )


def compare_keyframe_with_other_keyframes(list_of_histograms, key_frames):
    score = 0
    for histogram in list_of_histograms:
        for histogram1 in key_frames:
            if len(comparing_using_histo_video(histogram, histogram1)) > 0:
                 score += 1
                 break
    if (score / frame_number) > 0.5:
        return True
    else:
        return False

def comparing_using_histo_video(histogram, histograms):
    list_of_similar_images = []
    score = 0
    diffs = compare_histo(histogram, histograms)
    for diff in diffs:
        if diff*100 > 20:
            score += 1
    if score > 1:
        list_of_similar_images.append(histograms)
    score = 0
    return list_of_similar_images

#Helper functions
def histo(image):
    hist = []
    for i in range(3):
      hist.append( cv2.calcHist([image],[i],None,[256],[0,256]))
    return hist

def calculate_all_params(image):
    histogram = histo(image)
    mean = mean_color(image)
    new_gabor = Gabor()
    gabor_histo = new_gabor.gabor_histogram(image)
    return {
        'histogram': histogram,
        'mean_color':mean,
        'gabor_histogram':gabor_histo
    }

def save_image(image,data,image_name,Images):
    Images.insert(Images(
            name= image_name,
            histogram_r=str(data['histogram'][0]).replace('\n',','),
            histogram_g=str(data['histogram'][1]).replace('\n',','),
            histogram_b=str(data['histogram'][2]).replace('\n',','),
            gabor_histogram=str(data['gabor_histogram']).replace('\n',','),
            mean_color=str(data['mean_color']).replace('\n',',')
        )
    )
    img_id = Images.query.order_by(Images.id.desc()).first().id
    file_path = os.path.join(f"{file_directory}/images/")
    if not os.path.exists(file_path):
                os.makedirs(file_path)
    file_path = os.path.join(file_path,str(img_id)+'.'+image_name.split('.')[1])
    cv2.imwrite(file_path,image)
    
def filter_extension(extension):
    return extension['video_extension'] == 'mp4' or extension['video_extension'] == 'mng'    

def save_video(Videos,KeyFrames,video_name,video_extension,video):
    Videos.insert(Videos(name=f'{video_name}.{video_extension}'))
    video_id = Videos.query.order_by(Videos.id.desc()).first().id
    target_path = f'{file_directory}/videos/{video_id}'
    if not os.path.exists(target_path):
            os.makedirs(target_path)
    
    video.save(os.path.join(target_path,f'{video_id}.{video_extension}'))
    key_frames_path = f'{file_directory}/videos/{video_id}/key_frames'
    if not os.path.exists(key_frames_path):
            os.makedirs(key_frames_path)
    target_path += f'/{video_id}.{video_extension}'
    key_frame_extraction(target_path,key_frames_path,frame_number)   
    key_frames = os.listdir(key_frames_path)
    list_of_histograms = []
    for key_frame in key_frames:
        img = cv2.imread(os.path.join(key_frames_path,key_frame))
        histogram = histo(img)
        list_of_histograms.append(histogram)
        save_key_frame(histogram,KeyFrames,video_id)
    return {'video_id':video_id,'list_of_histograms':list_of_histograms,'video_extension':video_extension}

def save_key_frame(data,KeyFrames,video_id):
    KeyFrames.insert(KeyFrames(
            video_id = video_id,
            histogram_r=str(data[0]).replace('\n',','),
            histogram_g=str(data[1]).replace('\n',','),
            histogram_b=str(data[2]).replace('\n',','),
        )
    )


def convert_image_numpy(image):
    in_memory_file = io.BytesIO()
    image.save(in_memory_file)
    data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
    color_image_flag = 1
    img = cv2.imdecode(data, color_image_flag)
    return img

def video_seed(location,Videos,KeyFrames):
    files =  os.listdir(location)
    
    files_formatted = []
    files_filtered = []
    for file in files:
        files_formatted.append({'video_name':file.split('.')[0],'video_extension':file.split('.')[1]})
    files_filtered = list(filter(filter_extension ,files_formatted))
    for file in files_filtered:    
        Videos.insert(Videos(name=file['video_name']))
        video_id = Videos.query.order_by(Videos.id.desc()).first().id
        original_path = 'C:/Users/3/Downloads/'+file['video_name']+'.'+file['video_extension']
        target_path = f'{file_directory}/videos/{video_id}'
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        target_path += f'/{file["video_name"]}.{file["video_extension"]}'
        shutil.copyfile(original_path, target_path)
        key_frames_path = f'{file_directory}/videos/{video_id}/key_frames'
        if not os.path.exists(key_frames_path):
            os.makedirs(key_frames_path)
        key_frame_extraction(target_path,key_frames_path,frame_number)
        key_frames = os.listdir(key_frames_path)
        for key_frame in key_frames:
            img = cv2.imread(os.path.join(key_frames_path,key_frame))
            histogram = histo(img)
            save_key_frame(histogram,KeyFrames,video_id)




