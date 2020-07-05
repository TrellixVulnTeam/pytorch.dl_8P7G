from dl.data.text import datasets, target_transforms, transforms
from dl.data.text.utils import batch_ind_fn_droptexts

from dl.models.crnn import CRNN

if __name__ == '__main__':
    augmentation = None

    ignore = target_transforms.Ignore(difficult=True)

    transform = transforms.Compose(
        [transforms.Resize((32, 100)),
         transforms.ToTensor(),
         #transforms.Normalize(rgb_means=(0.485, 0.456, 0.406), rgb_stds=(0.229, 0.224, 0.225))
         ]
    )
    target_transform = target_transforms.Compose(
        [target_transforms.Corners2Centroids(),
         # target_transforms.ToQuadrilateral(),
         target_transforms.OneHot(class_nums=datasets.COCOText_class_nums, add_background=True),
         target_transforms.ToTensor()]
    )

    print(CRNN())