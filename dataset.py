import os
import torchvision

from PIL import Image
from torch.utils.data import Dataset

def f2l(label_file):
    with open(label_file, 'r') as f:
        lines = f.readlines()
    return {line.split(',')[0].strip(): line.split(',')[1].strip() for line in lines}

class CaptchaDataset(Dataset):
    def __init__(self, data_dir, label_file, mode='train'):
        self.data_dir = data_dir

        self.transform = torchvision.transforms.Compose([
            torchvision.transforms.Resize((224, 224)),
            torchvision.transforms.ToTensor()
        ])

        self.imgs = [x for x in os.listdir(data_dir) if x.endswith('.png')]
        self.f2l = f2l(label_file)

    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, idx):
        img_path = os.path.join(self.data_dir, self.imgs[idx])
        img = Image.open(img_path)
        img = img.convert('RGB')

        if self.transform:
            img = self.transform(img)

        label = int(self.f2l[self.imgs[idx]])
        return img, label
