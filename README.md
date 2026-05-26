# ai-cs-daily-study

**매일 아침 CS 학습 노트를 자동 생성**하는 Obsidian 볼트.
OpenAI(`gpt-5.5`)로 3개 카테고리의 노트를 하나씩 만들고, GitHub Actions가 커밋·푸시까지 자동으로 처리합니다.

> 면접 대비·CS 복습용. 매일 5시에 새 노트가 도착합니다.

---

## 카테고리

| 카테고리 | 토픽 파일 | 출력 폴더 |
|---|---|---|
| CS 기초 지식 | `topics_cs.json` | `CS 기초 지식/` |
| 백엔드 + 클라우드 | `topics_backend.json` | `백엔드 + 클라우드/` |
| 자료구조 및 알고리즘 | `topics_algo.json` | `자료구조 및 알고리즘/` |

각 토픽 파일은 `current_index`를 갖고 있어 매일 다음 주제로 회전합니다.
한 사이클이 끝나면 `current_index = -1`로 표시하고 더 이상 생성하지 않습니다.

---

## 노트 구조 (`templates/note_template.md`)

각 노트는 7개 섹션으로 구성됩니다:

1. **핵심 개념** — 정의, 목적, 중요성
2. **내부 동작 원리** — 동작 과정, 다이어그램 설명
3. **실제 시스템 연결** — Linux, AWS, GCP, Nginx 등
4. **클라우드 연결** — Docker, K8s, AWS 서비스
5. **보안 연결** — 취약점, 모범 사례
6. **면접 질문** — Q&A 5개 (핵심 답변 포인트 포함)
7. **관련 개념** — `[[Obsidian 링크]]` 5개 이상

> 모델이 확실하지 않은 내용은 `⚠️ 확인 필요:` 접두사로 표시하도록 시스템 프롬프트에 강제되어 있습니다.

---

## 자동화

`.github/workflows/daily-study.yml`:

- **스케줄**: 매일 05:00 KST (`cron: '0 20 * * *'`)
- 3개 카테고리를 순차 생성 → `git commit` → `git push`
- 커밋 메시지: `📚 Daily Study: YYYY-MM-DD`
- 수동 실행: Actions 탭 → **Run workflow** (workflow_dispatch)

---

## Repo 구조

```
ai-cs-daily-study/
├── .github/workflows/
│   └── daily-study.yml          ← 매일 5시 KST 자동 실행
├── generate.py                  ← 노트 생성 스크립트
├── templates/
│   └── note_template.md         ← 7-섹션 마크다운 템플릿
│
├── topics_cs.json               ← CS 기초 주제 큐 + current_index
├── topics_backend.json          ← 백엔드/클라우드 주제 큐
├── topics_algo.json             ← 자료구조/알고리즘 주제 큐
│
├── CS 기초 지식/                  ← 생성된 노트
├── 백엔드 + 클라우드/              ← 생성된 노트
├── 자료구조 및 알고리즘/            ← 생성된 노트
│
└── .obsidian/                   ← Obsidian 볼트 설정·플러그인
```

---

## 필요한 Secrets

GitHub repo → Settings → Secrets and variables → Actions:

| Secret | 용도 |
|---|---|
| `OPENAI_API_KEY` | `generate.py`에서 OpenAI Responses API 호출 |

`GITHUB_TOKEN`은 GitHub가 자동 주입합니다.

---

## 로컬 실행

```bash
pip install openai==1.82.0
export OPENAI_API_KEY=...

python generate.py topics_cs.json
python generate.py topics_backend.json
python generate.py topics_algo.json
```

각 실행은 해당 카테고리의 `current_index`를 1 증가시킵니다.

---

## 토픽 추가 / 수정

`topics_*.json`을 편집:

```json
{
  "category_label": "CS 기초 지식",
  "output_dir": "CS 기초 지식",
  "current_index": 0,
  "topics": [
    { "category": "운영체제", "topic": "CPU", "subtopic": "..." }
  ]
}
```

`current_index`를 `-1`로 두면 해당 카테고리는 휴면 상태로 들어갑니다.

---

## Obsidian에서 열기

이 저장소 자체가 Obsidian 볼트입니다. Obsidian → **Open folder as vault** → 이 폴더 선택.
`obsidian-git` 플러그인이 동봉되어 있어 풀/푸시도 GUI에서 가능합니다.
