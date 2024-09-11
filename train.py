import os
import torch
import torchvision
import torch.nn as nn

import logging

from tensorboardX import SummaryWriter
from torch.utils.data import DataLoader
from dataset import CaptchaDataset

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.environ['CUDA_VISIBLE_DEVICES'] = '3'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def accuracy(output, target, topk=(1,)):
    acc = (output == target).sum().item()

    return acc / len(target)

def train(model, dataloader, loss_fn, optimizer, epoch, lr_scheduler):
    model.train()

    total_loss = 0
    total_acc = 0
    for i, (data, label) in enumerate(dataloader):
        data, label = data.to(device), label.to(device)

        optimizer.zero_grad()
        output = model(data)
        pred_label = output.argmax(dim=1)
        
        loss = loss_fn(output, label)
        loss.backward()
        optimizer.step()
        lr_scheduler.step()

        acc = accuracy(pred_label, label)
        total_loss += loss.item()
        total_acc += acc

    total_loss = total_loss / len(dataloader)
    total_acc = total_acc / len(dataloader)
    logging.info(f"[TRAIN] Epoch {epoch} Loss {total_loss} Acc {total_acc}")

    return total_loss, total_acc

def val(model, dataloader, loss_fn, epoch):
    model.eval()

    total_loss = 0
    total_acc = 0

    with torch.no_grad():
        for i, (data, label) in enumerate(dataloader):
            data, label = data.to(device), label.to(device)

            output = model(data)
            pred_label = output.argmax(dim=1)

            loss = loss_fn(output, label)
            acc = accuracy(pred_label, label)

            total_loss += loss.item()
            total_acc += acc
    
    total_loss = total_loss / len(dataloader)
    total_acc = total_acc / len(dataloader)
    logging.info(f"[VALIDATE] Epoch {epoch} Loss {total_loss} Acc {total_acc}")

    return total_loss, total_acc

def save_checkpoint(model, optimizer, epoch, path='resnet18_captcha_checkpoint.pth'):
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict()
    }, path)

if '__main__' == __name__:
    num_classes = 281
    batch_size = 32
    epochs = 100

    # load datasets
    train_dataset_dir = './datasets/images/train'
    val_dataset_dir = './datasets/images/val'

    train_dataset_list = './datasets/train_datasets.csv'
    val_dataset_lsit = './datasets/val_dataset.csv'

    train_dataset = CaptchaDataset(train_dataset_dir, train_dataset_list, mode='train')
    test_dataset = CaptchaDataset(val_dataset_dir, val_dataset_lsit, mode='val')

    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    logging.info(f"[DATASET] Train dataset size {len(train_dataset)}")
    logging.info(f"[DATASET] Test dataset size {len(test_dataset)}")

    # load model
    model = torchvision.models.resnet18()
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    model = model.to(device)

    # freeze the model 
    # for param in model.parameters():
    #     param.requires_grad = False

    # for param in model.fc.parameters():
    #     param.requires_grad = True

    lr = 1e-4
    weight_decay = 1e-4
    momentum = 0.9

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), 
                                 lr=lr, 
                                 weight_decay=weight_decay)
    lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=20)

    writer = SummaryWriter("runs_captcha/resnet18")

    best_acc = 0
    for epoch in range(epochs):
        train_loss, train_acc = train(model, train_dataloader, loss_fn, optimizer, epoch, lr_scheduler)
        val_loss, val_acc = val(model, test_dataloader, loss_fn, epoch)

        writer.add_scalar("Loss/train", train_loss, epoch)
        writer.add_scalar("Acc/train", train_acc, epoch)
        writer.add_scalar("Loss/val", val_loss, epoch)
        writer.add_scalar("Acc/val", val_acc, epoch)
        
        if val_acc > best_acc:
            best_acc = val_acc
            save_checkpoint(model, optimizer, epoch)

