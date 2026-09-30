# 울트라맨 파이팅 에볼루션 3 PS2 한글패치

PS2 일본판 **ウルトラマン Fighting Evolution 3 (SLPS-25441)** 용 비공식 한국어 패치입니다. 이 게임은 화면의 일본어가 모두 그림(텍스처)으로 들어 있어, 일본어가 그려진 그림 **493장**을 전수 조사해 한글로 다시 그렸습니다. 현재 배포판은 **v1.0 (2026-09-30)** 입니다.

[패치 다운로드](https://github.com/snake759494/ultraman-fe3-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 **UltramanFE3_PS2_KO_v1.0.xdelta 하나**입니다. 저장소에는 제작 소스·번역·검증 자료만 공개합니다. 원본 및 완성 디스크 이미지, 추출한 실행파일·텍스처, 글꼴 파일, 외부 실행 파일은 포함하지 않습니다. GitHub 가 자동 생성하는 Source code ZIP/TAR 는 저장소 소스의 압축본이며 게임 파일이 아닙니다.

> ⚠️ `translation/` 폴더에는 울트라 모드의 미션 설명·이벤트 자막·해금 알림 등 번역문 전체가 들어 있어 **스포일러**가 포함됩니다. 이 README 에는 줄거리 내용을 적지 않았습니다.

## 게임 소개 및 대상 버전

「ウルトラマン Fighting Evolution 3」는 반프레스토가 2004년 PS2로 낸 울트라맨 시리즈 3D 대전 격투 게임입니다. 쇼와부터 헤이세이까지의 울트라 전사와 괴수가 등장하며, 원작 명장면을 재현하는 울트라 모드와 배틀·VS·커스텀·튜토리얼 모드 등이 있습니다.

이 패치는 **PS2 일본판 SLPS-25441 의 DVD ISO (2,048 바이트 섹터)** 에만 적용합니다. 파일 이름보다 아래 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 게임 ID | SLPS-25441 |
| 원본 형식 | 수정되지 않은 일본판 DVD 이미지, ISO (2,048 바이트 섹터) |
| 원본 ISO 크기 | 2,811,789,312 바이트 |
| **원본 ISO MD5** | `a4c445b0455658b1bfbd96ff8e7fe5ab` |
| 원본 ISO SHA-1 | `69fb796ecc226724557ff67c670b483889bde82e` |
| 원본 ISO SHA-256 | `54b801de3fb5d0185c822bfadd47d49d19c9fdba7d9ca8246a8a1eb8f3ae57bd` |
| xdelta 파일 크기 | 3,364,937 바이트 |
| xdelta SHA-256 | `8337162036c224a3497ef85f143232ee5f9a65aac33fa323f4f2a9546848d2cd` |
| 적용 결과 ISO 크기 | 2,811,789,312 바이트 (원본과 같음) |
| 적용 결과 ISO SHA-1 | `5dfaf565260e762b5a3929afd9acc32ad726b51d` |
| 적용 결과 ISO SHA-256 | `52412e4f08f21ae91a3e90f564e7a5725a62cf21a706bf2c702e21228025b0a9` |

원본 게임 파일은 사용자가 별도로 준비해야 합니다.

## 패치 적용 방법

### Windows 에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Ultraman - Fighting Evolution 3 (Japan).iso'
```

위 표와 다르면 적용을 중단하세요. BIN/CUE 로 바꾼 이미지나 CHD·CSO 에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `UltramanFE3_PS2_KO_v1.0.xdelta` 를 받습니다.
2. xdelta3 패치를 지원하는 도구의 **Apply Patch** 기능을 엽니다.
3. **Patch** 에 xdelta 파일, **Source File** 에 해시가 일치하는 원본 `.iso` 를 선택합니다.
4. **Output File** 에 새 파일명(예: `Ultraman - Fighting Evolution 3 (Japan) (Korean).iso`)을 지정합니다.

xdelta 는 호환성을 위해 2차 압축과 파일 경로 헤더 없이 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Ultraman - Fighting Evolution 3 (Japan).iso' '.\UltramanFE3_PS2_KO_v1.0.xdelta' '.\Ultraman - Fighting Evolution 3 (Japan) (Korean).iso'
```

해시를 자동 검사하는 도구도 있습니다(Python 3 + xdelta3 필요, 기존 출력 파일은 덮어쓰지 않음).

```powershell
python tools/apply_release.py --xdelta '.\xdelta3.exe' --source '.\Ultraman - Fighting Evolution 3 (Japan).iso' --patch '.\UltramanFE3_PS2_KO_v1.0.xdelta' --output '.\Ultraman - Fighting Evolution 3 (Japan) (Korean).iso'
```

### PCSX2 에서 실행

새 `.iso` 를 여세요. 원본판의 세이브 스테이트는 불러오지 마세요(실행파일 내용이 다름). 메모리 카드 세이브 데이터는 원본판과 호환됩니다(저장 형식은 건드리지 않음).

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 메뉴·시스템 | 타이틀 메뉴, 옵션, VS·리플레이·뷰 모드, 버튼 안내 바, 메모리 카드 메시지, 기동 시 경고 화면 |
| 울트라 모드 | 스토리 목록 20, 미션 설명 20, 미션 제목 20, 힌트 20, 미션 평가 항목 21, 결과 화면, 이벤트 자막 8장 |
| 캐릭터 | 선택 화면 이름(실행파일의 표시 폭 표 308칸 수정), 대전 화면 이름 40, 프로필 37, 필살기 목록 39 |
| 커스텀 모드 | 기술 설명 81, 타입·커스텀 목록, 항목 제목 |
| 튜토리얼 | 조피의 대사 그림 7장(약 110줄), 말풍선 13 |
| 기타 | 해금 알림 98, 배틀 스테이지 지역·대사 목록 |

### 번역 원칙

- 기계번역 없이 화면과 원작을 보고 직접 번역했습니다.
- 글꼴은 원본의 굵은 고딕에 맞춰 NanumSquare Neo(제목 Heavy, 본문 ExtraBold/Bold)를 쓰고, 원본의 색·외곽선·광채·기울임을 맞췄습니다.
- 게임이 원래 일본어 글자 폭만큼만 잘라서 표시하는 그림(튜토리얼 대사, 대전 화면 이름, 메시지)은 원문 폭 안에 맞췄습니다.
- 고유명사·기술명은 `translation/glossary.md` 용어집을 따릅니다(울트라세븐, 발탄 성인, 스페시움 광선 등).

### 번역하지 않은 것

- 제목 로고(ウルトラマン)와 원래 영어로 된 그림(LOADING, STORY SELECT, FIGHT, WIN/LOSE 등), 저작권 표기.
- 동영상(IPU) — 대사 유무를 확인하지 않았고 자막을 넣지 않았습니다.

## 알려진 한계

- 인게임 확인은 PCSX2 v2.2.0 으로 타이틀·캐릭터 선택·대전·튜토리얼·스토리 선택·미션 설명 화면까지 했습니다. 결과·커스텀·해금 알림 등은 그림 단위로만 확인했습니다.
- 원문 폭이 좁았던 이름·문구는 가로로 압축되어 조금 좁아 보일 수 있습니다.
- 다른 화면에서 글자 끝이 잘리는 곳을 발견하면 이슈로 알려 주세요. 실기에서의 동작은 확인하지 못했습니다.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `tools/` | 빌드·검증 도구 (Python). `extract.py` 원본 추출, `g_*.py` 그림 묶음별 한글 렌더, `build.py` 전체 빌드, `apply_release.py` 해시 검사 적용 |
| `translation/img/*.json` | 그림별 한국어 번역·배치 데이터 ⚠️ 스포일러 |
| `translation/glossary.md` | 용어집 |
| `validation/` | 빌드 검증 기록 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md) 를 참고하세요.
