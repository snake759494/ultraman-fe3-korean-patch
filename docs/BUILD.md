# 재빌드 방법

필요한 것: Python 3.10+ (numpy, Pillow, opencv-python, scipy, pycdlib, capstone), xdelta3 3.1.0.

## 준비

저장소 루트에 다음 파일을 둡니다(저장소에는 포함되지 않음).

- `Ultraman - Fighting Evolution 3 (Japan).iso` — 해시가 README 표와 일치하는 원본
- `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-dEb.ttf`, `NanumSquareNeo-eHv.ttf` — 네이버 나눔스퀘어 네오

```
python tools/extract.py      # -> work/SLPS_254.41, work/ext/NNNN.bin
```

## 그림 한글화

각 묶음 스크립트가 `translation/img/*.json` 을 읽어 `work/patched/*.pom` 을 만들고 `work/preview/` 에 미리보기를 남깁니다.

```
python tools/g_hint.py
python tools/g_mdetail.py
python tools/g_mtitle.py
python tools/g_profile.py
python tools/g_movelist.py
python tools/g_list.py
python tools/g_hudname.py
python tools/g_help.py
python tools/g_zimaku.py
python tools/g_burst.py
python tools/g_missionbar.py
python tools/g_notice.py
python tools/g_tuto.py
python tools/g_waza.py
python tools/g_auto.py
python tools/g_rows.py mcard
python tools/g_rows.py misc_rows
python tools/g_boxes.py
python tools/g_custom.py     # g_boxes.py 다음에 (커스텀 타입 목록 라벨)
python tools/g_menu.py       # 타이틀 메뉴 (팔레트 2개 동시 양자화)
```

## 디스크 이미지

```
python tools/build.py      # -> Ultraman - Fighting Evolution 3 (Japan) (Korean).iso
xdelta3 -e -9 -S none -A -s "Ultraman - Fighting Evolution 3 (Japan).iso" "Ultraman - Fighting Evolution 3 (Japan) (Korean).iso" UltramanFE3_PS2_KO_v1.0.1.xdelta
```

`tools/emu.py` 는 휴대용 PCSX2(`UFE3_EMU` 환경변수 또는 저장소 옆 `pcsx2/`)를 띄워 화면을 캡처하는 검증 도구입니다.
