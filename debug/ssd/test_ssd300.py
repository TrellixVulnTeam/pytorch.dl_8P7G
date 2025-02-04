from dl.data.objdetn import datasets, utils, target_transforms
from dl.data import transforms

from dl.models.ssd.ssd300 import SSD300
from dl.data.utils.converter import toVisualizeRectLabelRGBimg
from torch.utils.data import DataLoader
import cv2

if __name__ == '__main__':
    augmentation = None

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
    test_dataset = datasets.VOC2007_TestDataset(transform=transform, target_transform=target_transform, augmentation=augmentation)

    test_loader = DataLoader(test_dataset,
                             batch_size=32,
                             shuffle=True,
                             collate_fn=utils.batch_ind_fn,
                             num_workers=4,
                             pin_memory=False)

    model = SSD300(class_labels=datasets.VOC_class_labels, batch_norm=False)
    model.load_weights('../../weights/ssd300-voc2007+12+coco/ssd300-voc2007+2012+coco_i-0025000_checkpoints20200611.pth')
    #model.load_for_finetune('./weights/ssd300-voc2007+12+coco/ssd300-voc2007+2012+coco_i-30000.pth')
    model.eval()
    print(model)

    #evaluator = VOC2007Evaluator(test_loader, iteration_interval=5000)
    #ap = evaluator(model)
    #print(ap)
    image = cv2.cvtColor(cv2.imread('../../scripts/ssd/assets/coco_testimg.jpg'), cv2.COLOR_BGR2RGB)
    infers, imgs, orig_imgs = model.infer(image, visualize=True, toNorm=True)
    for i, img in enumerate(imgs):
        cv2.imshow('result', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        cv2.waitKey()

    images = [test_dataset[i][0] for i in range(20)]
    inf, ret_imgs, orig_imgs = model.infer(images, visualize=True, toNorm=False)
    for img in ret_imgs:
        cv2.imshow('result', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        cv2.waitKey()