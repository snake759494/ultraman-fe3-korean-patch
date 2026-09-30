# 빌드 검증 기록 (v1.0, 2026-09-30)

```
단독 322 FUM멤버 169 FUM항목 59
이름 UV 폭 수정 308
완료 Ultraman - Fighting Evolution 3 (Japan) (Korean).iso
```

- 교체한 그림: 단독 POM 322장 + FUM 멤버 169개(같은 그림이 여러 묶음에 중복 수록).
- DFS 재압축기: 원본 FUM 멤버 해제 → 재압축 → 해제 왕복 일치 확인.
- xdelta 역적용: 원본 ISO + `UltramanFE3_PS2_KO_v1.0.xdelta` → 결과 SHA-1 `5dfaf565260e762b5a3929afd9acc32ad726b51d` 일치.
- PCSX2 v2.2.0 화면 확인: 기동·타이틀 메뉴, VS 캐릭터 선택(이름 폭), 대전 화면 이름, 튜토리얼 대사(줄 끝 잘림 없음), 스토리 선택, 미션 설명.
