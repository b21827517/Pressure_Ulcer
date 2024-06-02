from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
import torchvision.models as models

vgg16_model = models.vgg16(pretrained=True)
vgg16_model.classifier[6] = nn.Linear(4096, 4) # 4 types of outputs
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
vgg16_model.load_state_dict(torch.load('/Users/efekalayci/Sondeneme/vgg16_best_model.pt', map_location=DEVICE))
pil_image = Image.open("/Users/efekalayci/Sondeneme/uploads/image.jpg").convert('RGB')

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                      std=[0.229, 0.224, 0.225])
image_transforms = transforms.Compose([transforms.Resize(256),transforms.CenterCrop(224),transforms.ToTensor(),normalize])
processed_image = image_transforms(pil_image)
processed_image = processed_image.unsqueeze_(0)
processed_image = processed_image.float()

with torch.no_grad():
        output = vgg16_model.forward(processed_image)
processed_image = image_transforms(pil_image)
probabilities = torch.nn.functional.softmax(output[0], dim=0)
predicted_class = torch.argmax(probabilities).item()
predictions_dict = {
        "predicted_class": predicted_class,
        "probabilities": {class_idx: prob.item() for class_idx, prob in enumerate(probabilities)}
    }
predictions = []
predictions.append(predictions_dict)
print(predictions)
