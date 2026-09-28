# GitHub Commit 규칙

## 1. Branch

각자 개인 Branch에서 작업한다.

고준환 Branch:

``` text
joonhwanko
```

작업을 시작하기 전에 `main`의 최신 내용을 가져온다.

``` bash
git checkout joonhwanko
git pull origin main
```

------------------------------------------------------------------------

## 2. Commit Message 형식

``` text
[이름] type: 작업 내용
```

고준환 예시:

``` text
[고준환] feat: 종목별 평가금액 및 수익률 계산 추가
```

------------------------------------------------------------------------

## 3. Commit Type

  Type         의미                    예시
  ------------ ----------------------- --------------------------
  `feat`       새로운 기능·분석 추가   수익률 계산 기능 추가
  `fix`        오류 수정               수익률 계산 오류 수정
  `data`       데이터 수집·전처리      포트폴리오 데이터 전처리
  `test`       결과 검증               SQL과 Pandas 결과 비교
  `refactor`   코드 구조 개선          계산 로직 함수화
  `docs`       문서 작성·수정          README 분석 결과 추가
  `chore`      환경설정 등 기타 작업   패키지 설정 수정

------------------------------------------------------------------------

## 4. 고준환 Commit 예시

``` bash
git add .
git commit -m "[고준환] data: 포트폴리오 데이터 전처리"
git push origin joonhwanko
```

``` bash
git add .
git commit -m "[고준환] feat: 종목별 평가금액 및 수익률 계산 추가"
git push origin joonhwanko
```

``` bash
git add .
git commit -m "[고준환] test: SQL과 Pandas 수익률 계산 결과 검증"
git push origin joonhwanko
```

오류를 수정했다면:

``` bash
git add .
git commit -m "[고준환] fix: 수익률 계산 오류 수정"
git push origin joonhwanko
```

------------------------------------------------------------------------

## 5. 권장 Commit 방식

한 번에 모든 작업을 하나의 Commit으로 올리지 않고 의미 있는 작업 단위로
나눈다.

``` text
[고준환] data: 포트폴리오 데이터 전처리
[고준환] feat: 종목별 평가금액 및 수익률 계산 추가
[고준환] test: SQL과 Pandas 수익률 계산 결과 검증
```

각 팀원은 **의미 있는 Commit을 최소 2회 이상** 남긴다.

------------------------------------------------------------------------

## 6. 피해야 할 Commit Message

``` text
❌ [고준환] 수정
❌ [고준환] 코드 수정
❌ [고준환] test
❌ [고준환] 최종
❌ [고준환] 최종2
```

작업 내용을 알 수 있도록 작성한다.

``` text
✅ [고준환] feat: 포트폴리오 수익률 계산 추가
✅ [고준환] fix: 결측 주가 데이터 처리 오류 수정
✅ [고준환] test: SQL과 Pandas 평가손익 결과 비교
```

------------------------------------------------------------------------

## 핵심 규칙

``` text
Branch: 개인 Branch 사용
작업 전: git pull origin main
Commit: [이름] type: 작업 내용
Push: git push origin <개인 Branch>
```

고준환:

``` bash
git checkout joonhwanko
git pull origin main

# 작업 후
git add .
git commit -m "[고준환] feat: 작업 내용"
git push origin joonhwanko
```
