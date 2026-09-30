# 권리 및 외부 자료

이 저장소는 비공식 한국어 패치의 제작 소스·번역·검증 자료 공개용입니다. 원작 게임 「ウルトラマン Fighting Evolution 3」와 그 텍스트·이미지·음성·영상·실행 코드의 권리는 원 권리자(円谷プロ, BANPRESTO 등)에게 있습니다. 원본 게임, 패치 적용 게임, 게임에서 추출한 실행파일·텍스처·동영상·음성은 배포하지 않으며, 릴리즈에는 원본 디스크 이미지가 있어야만 쓸 수 있는 차분 파일(xdelta)만 첨부합니다.

저장소 공개 자체가 모든 파일에 동일한 오픈소스 라이선스를 부여한다는 뜻은 아닙니다. 자체 제작 코드·번역 전체에 대한 별도 포괄 라이선스는 현재 지정하지 않았습니다.

번역 데이터(`translation/img/`)에는 한국어 번역문과 배치 좌표만 들어 있습니다. 용어집(`translation/glossary.md`)에는 대조를 위해 일부 고유명사·기술명의 일본어 표기가 함께 들어 있으며, 그 권리 역시 원 권리자에게 있습니다.

게임 안 한글은 NanumSquare Neo(Bold·ExtraBold·Heavy)로 그렸습니다. NanumSquare Neo 는 SIL Open Font License 1.1 을 따르며 전문을 `LICENSES/NanumSquareNeo-OFL-1.1.txt` 에 보존했습니다. 글꼴 파일 자체는 포함하지 않습니다(`docs/FONT_CREDITS.md`).

xdelta, PCSX2, Python 라이브러리(numpy, Pillow, OpenCV, SciPy, capstone, pycdlib) 등 외부 도구는 각 프로젝트의 라이선스를 따르며 바이너리를 재배포하지 않습니다. `tools/isopatch.py`, `tools/emu.py`, `tools/mips.py` 는 같은 제작자의 질 올 인피니트 한글패치에서 가져와 이 게임에 맞게 고친 것입니다. 게임 코드의 디스어셈블 결과물은 넣지 않았고, 해석한 내용만 `docs/TECHNICAL.md` 에 정리했습니다.
