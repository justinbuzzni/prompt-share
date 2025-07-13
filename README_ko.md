# Claude Prompt Share

Claude AI 대화 데이터를 동기화, 관리, 조회할 수 있는 종합 도구입니다. 동기화 도구와 웹 기반 뷰어 두 가지 주요 구성 요소로 이루어져 있습니다.

## 🌟 주요 기능

### 동기화 도구 (`claude_sync.py`)
- **자동 백업**: Claude 대화를 로컬 저장소에서 MongoDB로 동기화
- **저장소 기반 필터링**: GitHub 소유자 또는 개별 저장소별로 동기화
- **보안**: 민감한 정보(API 키, 비밀번호, 토큰) 자동 마스킹
- **Git 통합**: Git 설정에서 저장소 소유자를 정확하게 감지

### 웹 뷰어
- **모던 UI**: Material-UI 컴포넌트를 사용한 React 기반 프론트엔드
- **FastAPI 백엔드**: 고성능 API 서버
- **프로젝트 구성**: 저장소 이름별로 그룹화된 프로젝트 보기
- **검색 기능**: 메시지와 프로젝트 검색
- **실시간 업데이트**: 최신 대화 시간 표시

## 📋 필수 요구사항

- Python 3.8+
- Node.js 16+
- MongoDB 4.4+
- Claude Desktop App (로컬 대화 데이터용)

## 🚀 빠른 시작

### 1. 저장소 복제
```bash
git clone https://github.com/your-username/prompt-share.git
cd prompt-share
```

### 2. 환경 변수 설정
프로젝트 루트에 `.env` 파일 생성:
```env
MONGODB_URL=localhost:27017
MONGODB_USER=your_username
MONGODB_PASSWORD=your_password
MONGODB_DATABASE=claude_prompts
```

### 3. 의존성 설치

**Python 의존성:**
```bash
pip install -r requirements.txt
```

**프론트엔드 의존성:**
```bash
cd claude-viewer-frontend
npm install
```

### 4. 동기화 실행
```bash
# 모든 대화 동기화
python claude_sync.py

# 저장소 소유자별 동기화
python claude_sync.py -o buzzni

# 특정 저장소 동기화
python claude_sync.py -r prompt-share hsmoa
```

### 5. 웹 뷰어 시작

**백엔드 API 서버:**
```bash
python api_server.py
# API는 http://localhost:15011 에서 실행
```

**프론트엔드 개발 서버:**
```bash
cd claude-viewer-frontend
npm start
# 프론트엔드는 http://localhost:3000 에서 실행
```

## 📖 상세 사용법

### 동기화 도구

#### 대화형 모드
```bash
python claude_sync.py
```
다음 중 선택:
1. 저장소 소유자별 선택
2. 저장소 이름별 선택
3. 전체 동기화

#### 명령줄 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--list`, `-l` | 사용 가능한 소유자와 저장소 목록 표시 | `python claude_sync.py -l` |
| `--owners`, `-o` | 저장소 소유자별 동기화 | `python claude_sync.py -o buzzni anthropic` |
| `--repos`, `-r` | 특정 저장소 동기화 | `python claude_sync.py -r repo1 repo2` |
| `--all`, `-a` | 프롬프트 없이 전체 동기화 | `python claude_sync.py -a` |
| `--no-redaction` | 보안 마스킹 비활성화 | `python claude_sync.py --no-redaction` |

### 웹 뷰어 기능

#### 프로젝트 보기
- **그룹 보기**: 저장소 이름별로 그룹화된 프로젝트
- **플랫 보기**: 모든 프로젝트 목록
- **워크스페이스 배지**: main/release/feature 브랜치 시각적 표시

#### 메시지 표시
- 코드 블록 구문 강조
- 마크다운 렌더링
- 상대 시간 포함 타임스탬프 표시
- 빈 메시지 필터링

## 🔒 보안 기능

동기화 도구는 다음을 자동으로 감지하고 마스킹합니다:
- API 키 (OpenAI, Google, AWS 등)
- 비밀번호 및 인증 토큰
- 개인 키 (SSH, RSA)
- 데이터베이스 연결 문자열
- JWT 토큰
- 신용카드 번호

예시:
```
원본: sk-1234567890abcdefghijklmnop
마스킹: [REDACTED_API_KEY]
```

## 🏗️ 아키텍처

### 데이터 흐름
```
Claude Desktop App
    ↓
~/.claude/projects/ (로컬 저장소)
    ↓
claude_sync.py (추출 및 보안)
    ↓
MongoDB (보안 저장소)
    ↓
FastAPI Backend (api_server.py)
    ↓
React Frontend (웹 뷰어)
```

### MongoDB 스키마
- **projects**: 프로젝트 메타데이터와 세션 목록
- **sessions**: 개별 대화 세션
- **messages**: 메타데이터가 포함된 전체 메시지 기록

## 🔧 설정

### MongoDB 인덱스
최적의 성능을 위해 도구가 자동으로 인덱스를 생성합니다:
- Projects: `id` (고유), `path`, `created_at`
- Sessions: `id` (고유), `project_id`, `created_at`
- Messages: `session_id`, `timestamp`, 텍스트 검색

### 환경 변수
| 변수 | 설명 | 기본값 |
|------|------|--------|
| `MONGODB_URL` | MongoDB 연결 URL | `localhost:27017` |
| `MONGODB_USER` | MongoDB 사용자명 | - |
| `MONGODB_PASSWORD` | MongoDB 비밀번호 | - |
| `MONGODB_DATABASE` | 데이터베이스 이름 | `claude_prompts` |
| `PORT` | API 서버 포트 | `15011` |

## 🤝 기여하기

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다 - 자세한 내용은 LICENSE 파일을 참조하세요.

## 🙏 감사의 말

- Claude AI 커뮤니티를 위해 제작
- 아름다운 인터페이스를 위한 Material-UI 사용
- 고성능 API 서빙을 위한 FastAPI 구동