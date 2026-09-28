#!/usr/bin/env python3
"""Head-down timeline from face landmarks (OpenCV YuNet).

ratio = (nose_y - eyes_y) / (mouth_y - eyes_y); head down when ratio >= 0.60 or no face found.
  headpose.py VIDEO OUT.json [--every 6] [--model yunet.onnx]
Output: [[t, ratio|null, score], ...]. The YuNet model is downloaded next to OUT if missing.
Lib: head_down_frac(pose, a, b) -> share of samples in [a, b] that are head-down.
"""
import argparse, bisect, json, os, urllib.request

YUNET = 'https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx'


def head_down_frac(pose, a, b, thr=0.60):
    ts = [x[0] for x in pose]
    sel = pose[bisect.bisect_left(ts, a):bisect.bisect_right(ts, b)]
    return sum(1 for x in sel if x[1] is None or x[1] >= thr) / len(sel) if sel else 0.0


if __name__ == '__main__':
    import cv2
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video'); ap.add_argument('out')
    ap.add_argument('--every', type=int, default=6, help='analyse one frame out of N')
    ap.add_argument('--model')
    a = ap.parse_args()
    model = a.model or os.path.join(os.path.dirname(os.path.abspath(a.out)), 'yunet.onnx')
    if not os.path.exists(model):
        urllib.request.urlretrieve(YUNET, model)
    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    det = cv2.FaceDetectorYN.create(model, '', (960, 540), 0.6)
    res, i = [], 0
    while cap.grab():
        if i % a.every == 0:
            ok, f = cap.retrieve()
            h, w = f.shape[:2]
            det.setInputSize((960, round(960 * h / w)))
            _, faces = det.detect(cv2.resize(f, (960, round(960 * h / w))))
            t = round(i / fps, 2)
            if faces is None:
                res.append((t, None, 0))
            else:
                fc = max(faces, key=lambda r: r[2] * r[3])
                ey = (fc[5] + fc[7]) / 2; my = (fc[11] + fc[13]) / 2
                res.append((t, round(float((fc[9] - ey) / max(1, my - ey)), 3), round(float(fc[14]), 2)))
        i += 1
    json.dump(res, open(a.out, 'w'))
    print(len(res), 'samples ->', a.out)
