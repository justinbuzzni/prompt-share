# Claude Viewer - Premium React Frontend

고급스럽고 현대적인 Claude 대화 뷰어입니다. 최고의 UX를 제공하며 사용자에게 감동을 선사합니다.

## 주요 특징

### 디자인 하이라이트
- **프리미엄 다크 테마**: 보라색과 핑크색 그라데이션을 활용한 세련된 디자인
- **유동적인 애니메이션**: Framer Motion을 활용한 부드러운 전환 효과
- **글래스모피즘 UI**: 반투명 효과와 블러를 활용한 현대적인 인터페이스
- **반응형 디자인**: 모든 디바이스에서 완벽하게 작동

### 주요 기능
- 프로젝트 목록 보기 (세션 수, 업데이트 시간 표시)
- 세션별 대화 내용 확인
- 메시지 필터링 (User/Assistant)
- 실시간 검색 기능
- 코드 하이라이팅 지원
- 메시지 복사 기능

## 실행 방법

### 1. Backend API 서버 실행
```bash
# 프로젝트 루트에서
python api_server.py
```

### 2. Frontend 실행
```bash
# Frontend 디렉토리로 이동
cd claude-viewer-frontend

# 개발 서버 시작
npm start
```

### 3. 브라우저에서 확인
- Frontend: http://localhost:3000
- API: http://localhost:5000/api

## 기술 스택

### Frontend
- React + TypeScript
- Material-UI (MUI)
- Framer Motion (애니메이션)
- React Router (라우팅)
- Axios (API 통신)
- React Syntax Highlighter (코드 하이라이팅)

### Backend
- Flask (Python)
- Flask-CORS
- PyMongo
- MongoDB

## UI/UX 특징

### 애니메이션
- 페이지 전환 시 부드러운 fade-in/out
- 카드 hover 시 확대 및 그림자 효과
- 배경의 동적 그라데이션 애니메이션
- 스태거드 애니메이션으로 순차적 등장 효과

### 색상 테마
- Primary: 보라색 (#7C3AED)
- Secondary: 핑크색 (#EC4899)
- 다크 배경에 밝은 악센트 색상
- 그라데이션을 활용한 깊이감 표현

### 사용자 경험
- 직관적인 네비게이션 (빵부스러기)
- 실시간 검색 및 필터링
- 메시지 복사 기능
- 반응형 레이아웃
- 로딩 상태 표시

## 환경 설정

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:5000/api
```

### Backend (.env)
```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=claude_prompts
```

## 빌드 및 배포

### Frontend 빌드
```bash
cd claude-viewer-frontend
npm run build
```

빌드된 파일은 `build/` 디렉토리에 생성됩니다.

### Production 환경 설정
1. API 서버를 production 환경에 배포
2. Frontend의 `.env` 파일에서 `REACT_APP_API_URL`을 production API URL로 변경
3. 빌드 후 정적 파일 호스팅 서비스에 배포

## 추가 개발 아이디어

1. **검색 개선**
   - 전체 텍스트 검색
   - 날짜 범위 필터
   - 정규식 검색 지원

2. **시각화**
   - 대화 통계 대시보드
   - 워드 클라우드
   - 시간대별 활동 그래프

3. **export 기능**
   - 대화 내용 PDF 내보내기
   - Markdown 형식 내보내기
   - 선택적 백업

4. **사용자 설정**
   - 테마 커스터마이징
   - 폰트 크기 조절
   - 애니메이션 속도 설정