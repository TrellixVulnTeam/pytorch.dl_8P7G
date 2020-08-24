import logging, torch, cv2
import numpy as np

from ..._utils import _check_ins
from ..objdetn.target_transforms import (
    Compose,
    Corners2Centroids,
    Corners2MinMax,
    Centroids2Corners,
    Centroids2MinMax,
    MinMax2Corners,
    MinMax2Centroids,
    OneHot
)
from ..objdetn.target_transforms import _IgnoreBase
from ..txtrecog.target_transforms import Text2Number as _Text2Number
from ..utils.boxes import  shrink_quads_numpy

class Text2Number(object):
    def __init__(self, class_labels, blankIndex=None, ignore_nolabel=True, toLower=True):
        self._text2number = _Text2Number(class_labels, blankIndex, ignore_nolabel, toLower=toLower)

    def __call__(self, bboxes, labels, flags, quads, texts):
        ret_texts = []
        for txt in texts:
            txt, = self._text2number(txt)
            ret_texts += [np.array(txt)]
        return (bboxes, labels, flags, quads, ret_texts)

class Ignore(_IgnoreBase):
    supported_key = ['illegible', 'difficult', 'strange']

    def __init__(self, **kwargs):
        """
        :param kwargs: if true, specific keyword will be ignored
        """
        self.ignore_key = []
        self.ignore_strange = False
        for key, val in kwargs.items():
            if key in Ignore.supported_key:
                val = _check_ins(key, val, bool)
                if not val:
                    logging.warning('No meaning: {}=False'.format(key))
                elif key == 'strange':
                    self.ignore_strange = True
                else:
                    self.ignore_key += [key]
            else:
                logging.warning('Unsupported arguments: {}'.format(key))

    def __call__(self, labels, bboxes, flags, quads, texts):
        ret_bboxes = []
        ret_labels = []
        ret_flags = []
        ret_quads = []
        ret_texts = []

        for label, bbox, flag, quad, text in zip(labels, bboxes, flags, quads, texts):
            flag_keys = list(flag.keys())
            ig_flag = [flag[ig_key] if ig_key in flag_keys else False for ig_key in self.ignore_key]
            if any(ig_flag):
                continue
            """
            isIgnore = False
            for key, value in self.kwargs.items():
                if value and key in flag and flag[key]:
                    isIgnore = True
                    break
            if isIgnore:
                continue
            #if self._ignore_partial and flag['partial']:
            #    continue
            """
            _, size, _ = cv2.minAreaRect(quad.reshape((4, 2)))
            # bbox = [xmin, ymin, xmax, ymax]
            if self.ignore_strange and\
                    ((bbox[0] == bbox[2] or bbox[1] == bbox[3]) or (size[0] == 0 or size[1] == 0)):
                # ignore strange bounding box (xmin == xmax or ymin == ymax)
                # ignore strange quad,
                # e.g. [0.01231165 0.61663795 0.01231165 0.61663795 0.0123784  0.75113 0.0123784  0.75113   ]
                continue


            ret_bboxes += [bbox]
            ret_labels += [label]
            ret_flags += [flag]
            ret_quads += [quad]
            ret_texts += [text]
        if len(ret_bboxes) == 0:
            logging.warning("No labels!!\nAll labels may have been ignored.")
        ret_bboxes = np.array(ret_bboxes, dtype=np.float32)
        ret_labels = np.array(ret_labels, dtype=np.float32)
        ret_quads = np.array(ret_quads, dtype=np.float32)

        return (ret_labels, ret_bboxes, ret_flags, ret_quads, ret_texts)

class ToTensor(object):
    def __init__(self, textTensor=False):
        self.textTensor = textTensor

    def __call__(self, labels, bboxes, flags, quads, texts):
        """
        :param bboxes:
        :param labels:
        :param flags:
        :param args:
            quads
            texts
        :return:
        """
        texts = [torch.from_numpy(txt) for txt in texts] if self.textTensor else texts
        return (torch.from_numpy(labels), torch.from_numpy(bboxes), flags, torch.from_numpy(quads), texts)


class ToQuadrilateral(object):
    def __call__(self, labels, bboxes, flags, quads, texts):
        # Note that bboxes must be [cx, cy, w, h]
        assert quads.shape[1] == 8, '4th arguments must be quadrilateral points'

        # b=(xmin,ymin), (xmax,ymin), (xmax,ymax), (xmin,ymax)
        # b's shape = (*, 4, 2=(top left, top right, bottom right, bottom left)=(x,y))
        box_num = bboxes.shape[0]
        b = np.zeros(shape=(box_num, 4, 2), dtype=np.float32)
        b[:, 0, :] = bboxes[:, :2]  # top left
        b[:, 1, :] = bboxes[:, np.array((2, 1))]
        b[:, 2, :] = bboxes[:, 2:]
        b[:, 3, :] = bboxes[:, np.array((0, 3))]

        # convert shape to (*, 4, 2)
        quads = quads.reshape((-1, 4, 2))

        """
        dist formula is below;
        b[0] - q[0-3], b[1] - q[1-3,0], b[2] - q[2-3,0-1], b[3] - q[3,0-2]
        """

        dist = np.zeros(shape=(box_num, 4, 4))
        #trans = [[0,1,2,3],[1,2,3,0],[2,3,0,1],[3,0,1,2]]
        trans = np.arange(4)
        for i in range(4):
            _b = np.expand_dims(b[:, i, :], axis=1)
            _q = quads[:, np.roll(trans, i), :]# shape = (?, 4, 2)
            dist[:, i, :] = np.linalg.norm(_b - _q, axis=-1)

        inds = np.argmin(dist.sum(axis=1), axis=-1)

        # update
        for b in range(box_num):
            quads[b] = quads[b, np.roll(trans, inds[b])]

        return (labels, bboxes, flags, quads.reshape((-1, 8)), texts)
