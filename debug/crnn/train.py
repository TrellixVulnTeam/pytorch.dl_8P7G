from dl.data.txtrecog import datasets, target_transforms, transforms
#from dl.data.text.utils import batch_ind_fn_droptexts

from dl.models.crnn import CRNN

if __name__ == '__main__':
    augmentation = None

    #ignore = target_transforms.TextDetectionIgnore(difficult=True)

    transform = transforms.Compose(
        [transforms.Resize((100, 32)),
         #transforms.Grayscale(last_dims=1),
         #transforms.ToTensor(),
         #transforms.Normalize(rgb_means=(0.485, 0.456, 0.406), rgb_stds=(0.229, 0.224, 0.225))
         # normalize 0.5, 0.5?: https://github.com/pytorch/vision/issues/288
         ]
    )
    target_transform = target_transforms.Compose(
        [#target_transforms.Text2Number(class_labels=datasets.ALPHABET_LABELS),
         #target_transforms.OneHot(class_nums=datasets.ALPHABET_NUMBERS, add_nolabel=False),
         #target_transforms.ToTensor()
         ]
    )

    train_dataset = datasets.SynthTextRecognitionDataset(transform=transform, target_transform=target_transform, augmentation=augmentation)
    img, text = train_dataset[0]
    #import cv2
    #cv2.imshow(''.join(text), img)
    #cv2.waitKey()

    print(CRNN())