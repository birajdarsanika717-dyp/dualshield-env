import random, torch
from torch.utils.data import Dataset
from pathlib import Path
import torchvision.transforms as T

LABEL_MAP = {"none":0,"face_swap":1,"background_edit":2,"metadata_strip":3,"color_grade":4,"composite":5}

class DualShieldDataset(Dataset):
    def __init__(self, data_dir="data/images", split="train", image_size=(224,224), synthetic_size=500):
        self.image_size = image_size
        self.samples = []
        self.synthetic = False
        root = Path(data_dir)
        if root.exists():
            for cls_name, label in LABEL_MAP.items():
                for img_path in list((root/cls_name).glob("*.jpg")) + list((root/cls_name).glob("*.png")):
                    self.samples.append((str(img_path), label, label/5.0))
        if not self.samples:
            self.synthetic = True
            self.samples = [(None, random.randint(0,5), random.random()) for _ in range(synthetic_size)]
        self.transform = T.Compose([T.Resize(image_size), T.ToTensor(),
                                    T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
    def __len__(self): return len(self.samples)
    def __getitem__(self, idx):
        path, label, severity = self.samples[idx]
        img = torch.randn(3, *self.image_size) if self.synthetic else self.transform(
            __import__("PIL").Image.open(path).convert("RGB"))
        return img, torch.tensor(label, dtype=torch.long), torch.tensor(severity, dtype=torch.float32)
