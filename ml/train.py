from pathlib import Path
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split
from .model import DualShieldNet
from .dataset import DualShieldDataset

WEIGHTS_DIR = Path(__file__).parent / "weights"
WEIGHTS_DIR.mkdir(exist_ok=True)

def train(epochs=10, batch_size=32, lr=1e-4, device=None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device}")
    dataset = DualShieldDataset()
    val_size = max(int(0.15 * len(dataset)), 1)
    train_ds, val_ds = random_split(dataset, [len(dataset)-val_size, val_size])
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    model = DualShieldNet().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-5)
    for epoch in range(1, epochs+1):
        model.train()
        total_loss = 0
        for imgs, labels, severities in train_loader:
            imgs, labels, severities = imgs.to(device), labels.to(device), severities.to(device)
            out  = model(imgs)
            loss = F.cross_entropy(out["logits"], labels) + 0.3 * F.mse_loss(out["severity"].squeeze(-1), severities)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch}/{epochs}  loss={total_loss/len(train_loader):.4f}")
    torch.save({"model_state": model.state_dict()}, WEIGHTS_DIR/"dualshield_v1.pt")
    print("Saved weights!")
    return model

if __name__ == "__main__":
    train()
