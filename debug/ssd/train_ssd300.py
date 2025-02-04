from dl.data.objdetn import datasets, utils, target_transforms, augmentations
from dl.data import transforms
from dl.loss.ssd import SSDLoss
from dl.models.ssd import SSD300
from dl.optim.scheduler import IterStepLR
from dl.log import *

#from torchvision import transforms > not import!!
from torch.utils.data import DataLoader
from torch.optim.sgd import SGD

if __name__ == '__main__':
    """
    augmentation = augmentations.Compose(
        []
    )"""
    augmentation = augmentations.AugmentationOriginal()
    #augmentation = None

    transform = transforms.Compose(
        [transforms.Resize((300, 300)),
         transforms.ToTensor(),
         transforms.Normalize(rgb_means=(0.485, 0.456, 0.406), rgb_stds=(0.229, 0.224, 0.225))]
    )
    target_transform = target_transforms.Compose(
        [target_transforms.Corners2Centroids(),
         target_transforms.OneHot(class_nums=datasets.VOC_class_nums, add_background=True),
         target_transforms.ToTensor()]
    )

    train_dataset = datasets.Compose(datasets=(datasets.VOC2007Dataset,), #datasets.VOC2012_TrainValDataset),
                                     ignore=target_transforms.Ignore(difficult=True), transform=transform, target_transform=target_transform, augmentation=augmentation)
    val_dataset = datasets.VOC2007_TestDataset(ignore=target_transforms.Ignore(difficult=True), transform=transform, target_transform=target_transform)

    #train_dataset = datasets.VOC2007Dataset(transform=transform)
    train_loader = DataLoader(train_dataset,
                              batch_size=32,
                              shuffle=True,
                              collate_fn=utils.batch_ind_fn,
                              num_workers=4,
                              pin_memory=True)

    model = SSD300(class_labels=train_dataset.class_labels, batch_norm=False).cuda()
    model.load_vgg_weights()
    #model = build_ssd('train')
    print(model)
    """
    imgs, targets = utils.batch_ind_fn((train_dataset[2000],))
    p, d = model(imgs)
    from dl.modules.boxes import matching_strategy
    matching_strategy(targets, d, batch_num=1)
    """
    optimizer = SGD(model.parameters(), lr=1e-3, momentum=0.9, weight_decay=5e-4)
    #optimizer = Adam(model.parameters(), lr=1e-3, weight_decay=5e-4)
    #iter_sheduler = IterMultiStepLR(optimizer, milestones=(10, 20, 30), gamma=0.1, verbose=True)
    iter_sheduler = IterStepLR(optimizer, step_size=60000, gamma=0.1, verbose=True)
    """
    save_manager = SaveManager(modelname='ssd300', interval=10, max_checkpoints=3)
    log_manager = LogManager(interval=10, save_manager=save_manager, loss_interval=10, live_graph=None)
    trainer = TrainLogger(model, loss_func=SSDLoss(), optimizer=optimizer, scheduler=iter_sheduler, log_manager=log_manager, gpu=True)

    trainer.train(30, train_loader)
    """
    #save_manager = SaveManager(modelname='ssd300', interval=100, max_checkpoints=3, plot_interval=10)

    #trainer = TrainObjectDetectionConsoleLogger(SSDLoss(), model, optimizer, iter_sheduler)
    #trainer.train_iter(save_manager, 80000, train_loader)

    save_manager = SaveManager(modelname='ssd300', interval=1, max_checkpoints=3, plot_interval=10)

    trainer = TrainObjectDetectionConsoleLogger(SSDLoss(), model, optimizer, iter_sheduler)
    trainer.train_epoch(save_manager, 2, train_loader)