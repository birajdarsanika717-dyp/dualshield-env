import torch
import torch.nn as nn
import torch.nn.functional as F

class FrequencyBranch(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn1   = nn.BatchNorm2d(32)
        self.bn2   = nn.BatchNorm2d(64)
        self.pool  = nn.AdaptiveAvgPool2d((8, 8))
        self.fc    = nn.Linear(64 * 8 * 8, 256)
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        return F.relu(self.fc(self.pool(x).flatten(1)))

class SpatialBranch(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 5, padding=2)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn1   = nn.BatchNorm2d(32)
        self.bn2   = nn.BatchNorm2d(64)
        self.pool  = nn.AdaptiveAvgPool2d((8, 8))
        self.fc    = nn.Linear(64 * 8 * 8, 256)
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        return F.relu(self.fc(self.pool(x).flatten(1)))

class DualShieldNet(nn.Module):
    NUM_CLASSES = 6
    CLASS_NAMES = ["none","face_swap","background_edit","metadata_strip","color_grade","composite"]
    def __init__(self):
        super().__init__()
        self.freq_branch    = FrequencyBranch()
        self.spatial_branch = SpatialBranch()
        self.trunk = nn.Sequential(
            nn.Linear(512, 256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256, 128), nn.ReLU()
        )
        self.cls_head      = nn.Linear(128, self.NUM_CLASSES)
        self.severity_head = nn.Sequential(nn.Linear(128,64), nn.ReLU(), nn.Linear(64,1), nn.Sigmoid())
    def forward(self, x):
        fused  = torch.cat([self.freq_branch(x), self.spatial_branch(x)], dim=1)
        h      = self.trunk(fused)
        logits = self.cls_head(h)
        probs  = F.softmax(logits, dim=1)
        return {"logits": logits, "probs": probs, "severity": self.severity_head(h),
                "confidence": probs.max(dim=1).values, "pred_class": probs.argmax(dim=1)}
    @torch.no_grad()
    def predict(self, x):
        self.eval()
        out = self.forward(x)
        return {"label": [self.CLASS_NAMES[i] for i in out["pred_class"].tolist()],
                "confidence": out["confidence"].tolist(),
                "severity": out["severity"].squeeze(-1).tolist()}
