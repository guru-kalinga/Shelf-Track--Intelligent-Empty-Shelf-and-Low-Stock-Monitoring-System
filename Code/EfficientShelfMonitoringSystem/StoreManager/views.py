from django.shortcuts import render , redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Owner.models import Employee_Enrol
from django.core.files.storage import FileSystemStorage
import cv2
import os
import numpy as np
from skimage.feature import blob_dog
import matplotlib.pyplot as plt

# Create your views here.
#########################################################################
def StoreManager_Login(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['pass']
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                return redirect('StoreManagerHome')
            else:
               messages.error(request, 'Invalid username or password')
               return render(request, 'StoreManagerLogin.html')
        except User.DoesNotExist:
            messages.error(request, 'something went wrong')
    return render(request , 'StoreManagerLogin.html')

#########################################################################

def StoreManagerHome(request):
    return render(request, 'StoreManager/StoreManagerHome.html')


###########################################################################

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from skimage.feature import blob_dog
from skimage.util import img_as_float  # Import for correct image conversion

def upload_image(request):
    if request.method == 'POST':
        image = request.FILES['file-upload']
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        fs.save(image.name, image)
        file_url = fs.url(image.name)

        # Define the base directory for processing images
        base_dir = os.path.join(settings.MEDIA_ROOT, 'retail_images')

        def get_foreground(img_path):
            h_kernel = np.ones((5, 3), np.uint8)
            # Read the image in color format
            color = cv2.imread(img_path)

            # Check if the image was loaded correctly
            if color is None:
                raise ValueError(f"Error reading the image file: {img_path}")

            gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
            gray = gray.astype(np.uint8)

            # Threshold the image using Otsu
            ret3, th3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Create the minimum and maximum threshold values for Canny Edge detection
            hist_eq = cv2.equalizeHist(gray)
            min_thresh = 0.66 * np.median(hist_eq)
            max_thresh = 1.33 * np.median(hist_eq)

            # Perform Canny edge detection
            edge_1 = cv2.Canny(gray, int(min_thresh), int(max_thresh))

            # Dilate the edges to make them more visible
            edge_2 = cv2.dilate(edge_1, None, iterations=1)
            image_th_inv = cv2.bitwise_not(cv2.dilate(edge_2, h_kernel, iterations=2))

            image_th_inv = image_th_inv.astype(np.uint8)

            return image_th_inv, gray, ret3

        def combine_bounding_boxes(upp_th, blob_list_sorted):
            i = 0
            while i < len(blob_list_sorted):
                j = i + 1
                while j < len(blob_list_sorted):
                    x1, y1, r1 = map(float, blob_list_sorted[i])
                    x2, y2, r2 = map(float, blob_list_sorted[j])
                    if max([abs(x - y) for x, y in zip([x1, y1], [x2, y2])]) < upp_th:
                        new_box = [min(x1, x2), min(y1, y2), max(x1 + r1, x2 + r2) - min(x1, x2)]
                        blob_list_sorted[i] = new_box
                        del blob_list_sorted[j]
                    else:
                        j += 1
                i += 1
            return blob_list_sorted

        def show_segmentation(img_path, _image):
            original = cv2.imread(img_path)
            if original is None:
                raise ValueError(f"Error reading the image file: {img_path}")

            image_th_inv, gray, th = get_foreground(img_path)

            image_th_inv = np.where(image_th_inv > th, 255, 0).astype(np.uint8)
            _image = cv2.erode(image_th_inv, np.ones((3, 3), np.uint8), iterations=1)

            fig, axes = plt.subplots(1, 2, figsize=(12, 6))
            ax = axes.ravel()
            ax[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
            ax[1].imshow(_image, cmap='gray')
            plt.show()

            output_path = os.path.join("CV2_Segmentation", os.path.basename(img_path))
            cv2.imwrite(output_path, _image)
            return _image

        def process_image(image_filename):
            img_path = os.path.join(base_dir, image_filename)
            original = cv2.imread(img_path)
            if original is None:
                raise ValueError(f"Error reading the image file: {img_path}")

            upp_th = 0.00392
            count = 0
            _image = cv2.imread(img_path, 0)
            if _image is None:
                raise ValueError(f"Error reading the image file: {img_path}")

            _image_float = img_as_float(_image)
            blobs_dog = blob_dog(_image_float, max_sigma=40, threshold=.10)

            blob_list_sorted = sorted([[int(blob[0]), int(blob[1]), int(blob[2])] for blob in blobs_dog])
            blob_list_sorted = combine_bounding_boxes(upp_th, blob_list_sorted)

            results_cv2 = {"img_name": [], "bbox": [], "coords": []}
            filtered = []
            contours_ = []

            for blob in blob_list_sorted:
                y, x, r = blob
                if r > 6:
                    original = cv2.rectangle(original, (int(x), int(y)), (int(x + r), int(y + r)), (255, 0, 0), 2)
                    count += 1
                    results_cv2["img_name"].append(str(image_filename.split(".")[0]))
                    results_cv2["bbox"].append(count)
                    results_cv2["coords"].append([x, y, x + r, y + r])

            fig, axes = plt.subplots(1, 2, figsize=(15, 10))
            ax = axes.ravel()
            ax[0].imshow(original)

            contours, _ = cv2.findContours(_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            objects = np.zeros([original.shape[0], original.shape[1], 3], 'uint8')

            for c in contours:
                if cv2.contourArea(c) < (_image.shape[0] * _image.shape[1]) * .10:
                    x = [int(val[0][0]) for val in c]
                    y = [int(val[0][1]) for val in c]
                    filtered.append([x, y])
                    contours_.append(c)
                    cv2.drawContours(original, [c], -1, (255, 0, 0), -1)

            ax[1].imshow(original)
            plt.show()

            output_path = os.path.join("Identified_empty_spaces", os.path.basename(img_path))
            cv2.imwrite(output_path, original)

            return results_cv2, blob_list_sorted, filtered, contours_

        image_filename = image.name
        results_cv2, blob_list_sorted, filtered, contours_ = process_image(image_filename)

    return render(request, 'StoreManager/UploadImage.html')
