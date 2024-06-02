import cv2
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
import torchvision.models as models

def get_contour_coordinates(image_path,original_image_path):
    # Görüntüyü oku
    image = cv2.imread(image_path)

    # Görüntüyü gri tonlamalıya çevir
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Konturları bul
    contours, _ = cv2.findContours(gray_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest_contour = max(contours, key=cv2.contourArea)

    # Son konturun sınırlayıcı dikdörtgen koordinatlarını yazdır
    x, y, w, h = cv2.boundingRect(largest_contour)
    original_image = cv2.imread(original_image_path)
    cropped_segment = original_image[y:y+h, x:x+w]
    cv2.imwrite("/Users/efekalayci/Sondeneme/" + '_cropped.jpg', cropped_segment)

    #print(f"Son Segment Koordinatları: Sol: {x}, Üst: {y}, Sağ: {x+w}, Alt: {y+h}")
    print(x,y,w,h)
    return x,y,w,h

#x,y,w,h = get_contour_coordinates("/Users/efekalayci/Sondeneme/predicted_mask_1.png","/Users/efekalayci/Sondeneme/uploads/image.jpg")
vgg16_model = models.vgg16(pretrained=True)
vgg16_model.classifier[6] = nn.Linear(4096, 4) # 4 types of outputs
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
vgg16_model.load_state_dict(torch.load('/Users/efekalayci/Sondeneme/vgg16_best_model.pt', map_location=DEVICE))

def predictWithVGG16WithRoi(image_path, vgg16, device,segmented):

  # Extracting RoI coordinates
  x, y, w, h = get_contour_coordinates(segmented,image_path)

  # Loading and preprocessing test image
  img = Image.open(image_path).convert('RGB')
  img2 = Image.open(image_path).convert('RGB')

  img_cropped = img.crop((x, y, x + w, y + h))
  #img_cropped.save("cropped_image.png")
  normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                    std=[0.229, 0.224, 0.225])
  transform = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
        normalize,
  ])

  img_preprocessed = transform(img_cropped).unsqueeze(0).to(device)
  img_preprocessed2 = transform(img2).unsqueeze(0).to(device)

  # Making prediction with VGG-16 model
  with torch.no_grad():
    output = vgg16(img_preprocessed)
    output1 = vgg16(img_preprocessed2)
  probabilities = torch.nn.functional.softmax(output[0], dim=0)
  probabilities2 = torch.nn.functional.softmax(output1[0], dim=0)
  print(probabilities2)
  print(probabilities)
  predicted_class = torch.argmax(probabilities).item()
  probabilities[0] = probabilities2[0]*0.8 + probabilities[0]*0.2
  probabilities[1] = probabilities2[1]*0.8 + probabilities[1]*0.2
  probabilities[2] = probabilities2[2]*0.8 + probabilities[2]*0.2
  probabilities[3] = probabilities2[3]*0.8 + probabilities[3]*0.2
  print(probabilities)
  return f"{probabilities[0]:.2%}", f"{probabilities[1]:.2%}", f"{probabilities[2]:.2%}", f"{probabilities[3]:.2%}", f"{probabilities2[0]:.2%}", f"{probabilities2[1]:.2%}", f"{probabilities2[2]:.2%}", f"{probabilities2[3]:.2%}"
  print(f"Probability: {probabilities[predicted_class]:.2%}")
#predictWithVGG16WithRoi("/Users/efekalayci/Sondeneme/uploads/image.jpg",vgg16_model,DEVICE,"/Users/efekalayci/Sondeneme/predicted_mask_2.png")