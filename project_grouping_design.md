# 프로젝트 그룹화 아키텍처 설계

## 현재 상황 분석

### 프로젝트 패턴
- 같은 프로젝트가 여러 경로에 존재
- 예: "aplus/meet" 프로젝트
  - `/workspace/hsmoa/backend/projects/aplus/meet` (메인)
  - `/workspace/hsmoa/backend/release/projects/aplus/meet` (릴리즈)
  - `/workspace/aplus/meet/fix/stt/projects/aplus/meet` (STT 수정)
  - `/workspace/meet/export/fix/projects/aplus/meet` (export 수정)

## 추천 아키텍처: 하이브리드 접근법

### 1. 데이터 모델 개선

```python
# models.py에 추가
class Project(BaseModel):
    id: str
    path: str
    project_name: str  # 추출된 실제 프로젝트명 (예: "aplus/meet")
    workspace_type: str  # "main", "release", "feature", etc.
    branch_info: str  # 작업 브랜치 정보 (예: "fix/stt", "push")
    sessions: List[str]
    # ... 기존 필드들
```

### 2. 동기화 시 프로젝트명 추출

```python
# utils.py에 추가
def extract_project_info(path: str) -> dict:
    """경로에서 프로젝트 정보 추출"""
    # 패턴: /projects/{domain}/{service}
    match = re.search(r'/projects/(.+?)(?:/|$)', path)
    if match:
        project_name = match.group(1)
    else:
        # projects 폴더가 없는 경우 마지막 폴더명 사용
        project_name = path.split('/')[-1]
    
    # workspace 타입 판단
    if '/hsmoa/backend/release/' in path:
        workspace_type = 'release'
    elif '/hsmoa/backend/' in path:
        workspace_type = 'main'
    else:
        workspace_type = 'feature'
    
    # 브랜치 정보 추출
    branch_info = extract_branch_info(path)
    
    return {
        'project_name': project_name,
        'workspace_type': workspace_type,
        'branch_info': branch_info
    }
```

### 3. API 엔드포인트 개선

```python
# api_server.py
@app.get("/api/projects/grouped")
async def get_projects_grouped(group_by: str = "name"):
    """그룹화된 프로젝트 목록 반환"""
    if group_by == "name":
        # 프로젝트명으로 그룹화
        grouped = {}
        for project in projects:
            name = project['project_name']
            if name not in grouped:
                grouped[name] = {
                    'project_name': name,
                    'workspaces': []
                }
            grouped[name]['workspaces'].append(project)
        return list(grouped.values())
    else:
        # 기존 방식 (플랫 리스트)
        return projects
```

### 4. 프론트엔드 개선

```typescript
// 그룹화된 프로젝트 표시
interface GroupedProject {
  project_name: string;
  workspaces: Project[];
  totalSessions: number;
  totalMessages: number;
  lastUpdated: Date;
}

// ProjectsGroupedView.tsx
const ProjectsGroupedView: React.FC = () => {
  const [viewMode, setViewMode] = useState<'grouped' | 'flat'>('grouped');
  
  return (
    <Box>
      <ToggleButtonGroup value={viewMode} onChange={setViewMode}>
        <ToggleButton value="grouped">그룹화</ToggleButton>
        <ToggleButton value="flat">전체 목록</ToggleButton>
      </ToggleButtonGroup>
      
      {viewMode === 'grouped' ? (
        <GroupedProjectList />
      ) : (
        <FlatProjectList />
      )}
    </Box>
  );
};
```

## 장점

1. **유연성**: 사용자가 보기 방식 선택 가능
2. **성능**: 백엔드에서 미리 처리하여 프론트엔드 부담 감소
3. **확장성**: 다른 그룹화 방식 추가 용이 (날짜별, 타입별 등)
4. **데이터 무결성**: 원본 데이터 구조 유지
5. **점진적 마이그레이션**: 기존 API와 호환 유지

## 구현 우선순위

1. **Phase 1**: 프로젝트명 추출 로직 구현 (백엔드)
2. **Phase 2**: 그룹화 API 엔드포인트 추가
3. **Phase 3**: 프론트엔드 토글 뷰 구현
4. **Phase 4**: 추가 그룹화 옵션 (선택사항)

## 대안 비교

### 옵션 1: DB 레벨 그룹화 (비추천)
- 장점: API 응답 빠름
- 단점: 데이터 구조 변경 필요, 유연성 부족

### 옵션 2: 프론트엔드만 처리 (비추천)
- 장점: 백엔드 변경 불필요
- 단점: 대량 데이터 시 성능 이슈, 중복 처리

### 옵션 3: 하이브리드 (추천) ✅
- 장점: 성능과 유연성 균형, 점진적 개선 가능
- 단점: 초기 구현 복잡도 약간 높음