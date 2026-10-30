"""Build an offline, self-contained spherical panorama tour from model renders.

Usage: python tools/build_vr_tour.py --config 07_renders/vr-tour-v01/tour-config.json
Only the requested output directory is written. Model files are read-only.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "09_delivery/vr-tour-v01"
TEMPLATE = OUT / "viewer.template.html"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "07_renders/vr-tour-v01/tour-config.json")
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(ROOT.resolve()), "Delivery stays inside the project"
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    scenes = config.get("panoramas", [])
    assert {s["id"] for s in scenes} == {"entry", "dining", "living", "balcony"}, "Four required panoramas"
    assert len(scenes) == 4
    geometry_path = Path(config.get("geometry", "02_geometry/geometry-master-v12.json"))
    if not geometry_path.is_absolute():
        geometry_path = ROOT / geometry_path
    geom = json.loads(geometry_path.read_text(encoding="utf-8"))
    config["geometrySha256"] = sha(geometry_path)
    assert geom["revision"] == config.get("revision", geom["revision"]), "Geometry revision must match the panorama configuration"
    model_path = None
    if config.get("model"):
        model_path = Path(config["model"])
        if not model_path.is_absolute():
            model_path = ROOT / model_path
        actual_model_sha = sha(model_path)
        assert not config.get("modelSha256") or actual_model_sha == config["modelSha256"], "Source model has changed since rendering"
        config["modelSha256"] = actual_model_sha
    config["floor"] = geom["floor"]
    config["mapWalls"] = [dict(x=p["x"], z=p["z"], w=p["w"], d=p["d"]) for p in geom["walls"] if p.get("y", 0) < 1000]
    manifest = dict(schemaVersion=1, title=config.get("title", "餐厅·门厅·客厅·阳台 360°漫游"),
                    modelRevision=config.get("revision", 12), sourceConfig=str(args.config),
                    sourceConfigSha256=sha(args.config), projection="monoscopic equirectangular 360×180",
                    geometry=str(geometry_path), geometrySha256=sha(geometry_path),
                    model=str(model_path) if model_path else None, modelSha256=config.get("modelSha256"),
                    viewer="offline WebGL spherical perspective; no network dependencies", panoramas=[])
    out.mkdir(parents=True, exist_ok=True)
    (out / "全景原图").mkdir(exist_ok=True)
    for scene in scenes:
        source = Path(scene["image"])
        if not source.is_absolute():
            source = ROOT / source
        with Image.open(source) as im:
            im.verify()
        with Image.open(source) as im:
            width, height = im.size
        assert width == height * 2, f"{scene['id']}: equirectangular panorama must be 2:1"
        assert width >= 2048, f"{scene['id']}: insufficient resolution"
        mime = "image/jpeg" if source.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        scene["imageData"] = "data:" + mime + ";base64," + base64.b64encode(source.read_bytes()).decode("ascii")
        scene["imageWidth"], scene["imageHeight"] = width, height
        relative = Path("全景原图") / (scene["id"] + "-day" + source.suffix.lower())
        shutil.copy2(source, out / relative)
        scene["downloadName"] = scene.get("label", scene["id"]) + "-360全景" + source.suffix.lower()
        manifest["panoramas"].append(dict(id=scene["id"], label=scene.get("label"), source=str(source),
                                          file=str(relative), width=width, height=height, sha256=sha(source),
                                          positionPlanMm=scene.get("positionPlanMm"),
                                          headingAtImageCenterDeg=scene.get("headingAtImageCenterDeg", 0)))
    payload = json.dumps(config, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    template = args.template.read_text(encoding="utf-8")
    assert template.count("__TOUR_DATA__") == 1
    html = template.replace("__TOUR_DATA__", payload)
    html_path = out / "打开360全景漫游.html"
    html_path.write_text(html, encoding="utf-8")
    # A sidecar is useful for auditing without embedding the image bytes again.
    slim = {**config, "panoramas": [{k: v for k, v in s.items() if k != "imageData"} for s in scenes]}
    (out / "漫游机位与来源.json").write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["html"] = dict(path=str(html_path), sha256=sha(html_path), bytes=html_path.stat().st_size)
    (out / "viewer-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "使用说明.txt").write_text(
        "双击「打开360全景漫游.html」，用电脑浏览器离线打开即可。\n"
        "鼠标拖动环顾，滚轮缩放；方向键环顾，＋／－缩放，Home回到当前机位初始方向。\n"
        "手机可以单指拖动、双指缩放。点击下方区域名、画面圆点或平面图切换机位。\n"
        "「全屏」按钮视浏览器支持而定；手机部分浏览器不提供全屏API。\n"
        "四个固定观察点的单眼360×180全景，可看前后左右及天花、地面。\n"
        "这是当前模型渲染的360影像，并非现场摄影；不支持自由行走、家具编辑或双眼立体视差。\n"
        "未声称已在VR头显上实测。原始2:1全景图保存在「全景原图」文件夹。\n"
        "页面与图片全部包含于本机文件，无网络服务、外链、账号或追踪。\n",
        encoding="utf-8")
    print(json.dumps(dict(status="VR_VIEWER_BUILT", html=str(html_path), panoramas=manifest["panoramas"]), ensure_ascii=False))


if __name__ == "__main__":
    main()
