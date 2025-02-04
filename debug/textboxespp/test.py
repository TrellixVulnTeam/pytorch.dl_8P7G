from dl.data.txtdetn import datasets, target_transforms, transforms, augmentations
from dl.models import TextBoxesPP
from dl.data.utils.converter import toVisualizeQuadsLabelRGBimg

#from torchvision import transforms > not import!!
from torch.utils.data import DataLoader
import cv2
import torch

if __name__ == '__main__':

    augmentation = augmentations.RandomSampled()
    #augmentation = None
    size = (764, 764)
    transform = transforms.Compose(
        [transforms.Resize((764, 764)),
         transforms.ToTensor(),
         transforms.Normalize(rgb_means=(0.485, 0.456, 0.406), rgb_stds=(0.229, 0.224, 0.225))]
    )
    target_transform = target_transforms.Compose(
        [target_transforms.Corners2Centroids(),
         #target_transforms.ToQuadrilateral(),
         target_transforms.OneHot(class_nums=datasets.COCOText_class_nums, add_background=True),
         target_transforms.ToTensor()]
    )

    #train_dataset = datasets.COCO2014Text_Dataset(ignore=target_transforms.Ignore(illegible=True), transform=transform, target_transform=target_transform, augmentation=None)
    test_dataset = datasets.SynthTextDetectionDataset(ignore=None, transform=transform, target_transform=target_transform, augmentation=augmentation)

    model = TextBoxesPP(input_shape=(size[0], size[1], 3)).cuda()
    print(model)
    model.load_weights('../../weights/icdar2015/train-icdar2015-stage2-batch16_i-16000.pth')
    #model.load_weights('../../weights/synthtext/pretrained-synthtext_i-60000.pth')
    #model.load_weights('../../weights/train-all-stage2-batch8_i-24000.pth')
    model.eval()

    image = cv2.cvtColor(cv2.imread('../../scripts/textboxes++/assets/test.png'), cv2.COLOR_BGR2RGB)
    infers, imgs, orig_imgs = model.infer(image, visualize=True, toNorm=True)
    for i, img in enumerate(imgs):
        cv2.imshow('result', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        cv2.waitKey()

    images = [test_dataset[i][0] for i in range(20)]
    inf, ret_imgs, orig_imgs = model.infer(images, visualize=True, toNorm=False)
    for img in ret_imgs:
        cv2.imshow('result', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        cv2.waitKey()
