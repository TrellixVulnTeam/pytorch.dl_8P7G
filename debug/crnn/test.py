import cv2

from dl.data.txtrecog import datasets
from dl.models import CRNN

if __name__ == '__main__':
    model = CRNN(class_labels=datasets.Alphanumeric_with_blank_labels, input_shape=(32, 100, 1)).cuda()
    model.eval()
    model.load_weights('../../weights/crnn-synthtext/e-0000007_checkpoints20200814.pth')
    print(model)

    image = cv2.cvtColor(cv2.imread('../../scripts/crnn/assets/test.jpg'), cv2.COLOR_BGR2GRAY)
    #image = cv2.cvtColor(cv2.imread('../../scripts/crnn/assets/demo.png'), cv2.COLOR_BGR2GRAY)
    cv2.imshow('test image', cv2.resize(image, (100, 32)))
    cv2.waitKey()
    _, raws, outs = model.infer(image, toNorm=True)
    for raw, out in zip(raws, outs):
        print('{} -> {}'.format(raw, out))