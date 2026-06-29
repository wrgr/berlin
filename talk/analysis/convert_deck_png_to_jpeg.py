"""Shrink a deck by recompressing large PHOTO PNGs to JPEG (q88), losslessly-invisible at ~288 DPI.
ZIP-level surgery (not python-pptx shape API) so the old PNG parts are truly removed — no orphans:
  - convert ppt/media/*.png > THRESH bytes to JPEG (skip images with real transparency: charts/logos)
  - rename the media part .png -> .jpg, rewrite every .rels Target, add a jpg Default content-type
Charts/logos (small or transparent PNGs) are left untouched. Reversible: originals in git history.
Usage: python convert_deck_png_to_jpeg.py [in.pptx] [out.pptx]   (default: berlin_deck_v14 in place)
"""
import sys, io, zipfile, os
from pathlib import Path
from PIL import Image as PILImage

TALK=Path(__file__).resolve().parent.parent
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else TALK/"berlin_deck_v14.pptx"
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else SRC
THRESH=800_000; Q=88

zin=zipfile.ZipFile(str(SRC))
raw={n:zin.read(n) for n in zin.namelist()}; zin.close()
conv={}            # old media name -> new media name
out={}             # final name -> bytes
before=after=0
for n,data in raw.items():
    if n.startswith("ppt/media/") and n.lower().endswith(".png") and len(data)>THRESH:
        before+=len(data)
        im=PILImage.open(io.BytesIO(data)); rgba=im.convert("RGBA"); a=rgba.getchannel("A")
        frac=sum(a.histogram()[:250])/float(im.width*im.height)   # fraction meaningfully transparent
        if frac>0.02:   # >2% transparent => load-bearing (cut-out) -> keep PNG
            out[n]=data; after+=len(data); print("  keep PNG (%.1f%% transparent): %s"%(100*frac,n.split('/')[-1])); continue
        bg=PILImage.new("RGB",im.size,(255,255,255)); bg.paste(rgba,mask=a)   # flatten near-opaque on white
        buf=io.BytesIO(); bg.save(buf,"JPEG",quality=Q,optimize=True); jb=buf.getvalue()
        if len(jb)<len(data):
            new=n[:-4]+".jpg"; conv[n]=new; out[new]=jb; after+=len(jb)
            print("  %s %.2f->%.2f MB"%(n.split('/')[-1],len(data)/1e6,len(jb)/1e6))
        else:
            out[n]=data; after+=len(data)
    else:
        out[n]=data

# rewrite every .rels Target that points at a converted media file
for n in list(out):
    if n.endswith(".rels"):
        t=out[n].decode("utf-8")
        for old,new in conv.items():
            t=t.replace(old.split('/')[-1]+'"', new.split('/')[-1]+'"')
        out[n]=t.encode("utf-8")
# ensure a jpg Default content-type exists
ct=out["[Content_Types].xml"].decode("utf-8")
if conv and 'Extension="jpg"' not in ct and "Extension='jpg'" not in ct:
    ct=ct.replace("</Types>", '<Default Extension="jpg" ContentType="image/jpeg"/></Types>')
    out["[Content_Types].xml"]=ct.encode("utf-8")

tmp=str(OUT)+".tmp"
zo=zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED)
for n,data in out.items():
    if n in conv: continue          # old png name dropped (new .jpg written instead)
    zo.writestr(n,data)
zo.close(); os.replace(tmp,str(OUT))
print("\nconverted %d photo PNGs -> JPEG; those parts %.1f -> %.1f MB"%(len(conv),before/1e6,after/1e6))
print("deck file: %.1f MB  ->  %s"%(os.path.getsize(OUT)/1e6,OUT))
