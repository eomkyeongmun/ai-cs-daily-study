#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from openai import OpenAI

TEMPLATE_FILE = Path("templates/note_template.md")


def load_topics(topics_file: Path) -> dict:
    with open(topics_file, encoding="utf-8") as f:
        return json.load(f)


def save_topics(topics_file: Path, data: dict):
    with open(topics_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_today_topic(data: dict) -> tuple:
    idx = data["current_index"] % len(data["topics"])
    return data["topics"][idx], idx


def build_prompt(topic: dict) -> str:
    return f"""당신은 CS 학습 노트 작성 전문가입니다.
다음 주제로 심층적인 학습 노트를 한국어로 작성해주세요.

카테고리: {topic['category']}
주제: {topic['topic']}
세부주제: {topic['subtopic']}

다음 형식으로 각 섹션을 작성하세요. 각 섹션은 마크다운 형식으로 작성하며,
섹션 구분은 반드시 아래 구분자를 사용하세요:

[CORE_CONCEPT]
핵심 개념 설명 (300자 이상, 정의, 목적, 왜 중요한지 포함)

[INTERNAL_MECHANISM]
내부 동작 원리 (구체적인 동작 과정, 다이어그램 설명 포함)

[REAL_SYSTEM]
실제 시스템 연결 (Linux, AWS, GCP, Nginx 등 실제 사례)

[CLOUD_CONNECTION]
클라우드 연결 (Docker, K8s, AWS 서비스와의 연관성)

[SECURITY_CONNECTION]
보안 연결 (이 개념과 관련된 보안 이슈, 취약점, 모범 사례)

[INTERVIEW_QUESTIONS]
면접 질문 5개 (각 질문에 핵심 답변 포인트 포함)
형식:
**Q1. 질문내용**
> 핵심 답변: ...

[RELATED_CONCEPTS]
관련 개념 Obsidian 링크 형식으로 5개 이상
형식: - [[개념명]] - 연관 이유 한 줄
"""


def generate_note(topic: dict) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    system_prompt = (
        "당신은 CS 학습 노트 작성 전문가입니다. "
        "반드시 사실에 근거한 내용만 작성하세요. "
        "확실하지 않거나 검증하기 어려운 내용은 반드시 '⚠️ 확인 필요: ' 접두사를 붙여 표시하세요. "
        "수치, 버전, 날짜 등 구체적 데이터는 틀릴 수 있으므로 신중하게 작성하세요."
    )

    response = client.responses.create(
        model="gpt-5.5",
        instructions=system_prompt,
        input=build_prompt(topic),
        reasoning={"effort": "medium"},
        max_output_tokens=8000,
    )
    return response.output_text


def parse_sections(content: str) -> dict:
    sections = {
        "CORE_CONCEPT": "",
        "INTERNAL_MECHANISM": "",
        "REAL_SYSTEM": "",
        "CLOUD_CONNECTION": "",
        "SECURITY_CONNECTION": "",
        "INTERVIEW_QUESTIONS": "",
        "RELATED_CONCEPTS": "",
    }
    keys = list(sections.keys())
    for i, key in enumerate(keys):
        start_marker = f"[{key}]"
        end_marker = f"[{keys[i+1]}]" if i + 1 < len(keys) else None
        start = content.find(start_marker)
        if start == -1:
            continue
        start += len(start_marker)
        end = content.find(end_marker) if end_marker else len(content)
        sections[key] = content[start:end].strip()
    return sections


def build_note(topic: dict, sections: dict, date_str: str) -> str:
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        template = f.read()

    category_tag = topic["category"].replace(" ", "-").replace("/", "-")
    title = f"{topic['topic']} - {topic['subtopic']}"

    note = template
    note = note.replace("{{DATE}}", date_str)
    note = note.replace("{{CATEGORY}}", topic["category"])
    note = note.replace("{{TOPIC}}", topic["topic"])
    note = note.replace("{{SUBTOPIC}}", topic["subtopic"])
    note = note.replace("{{CATEGORY_TAG}}", category_tag)
    note = note.replace("{{TITLE}}", title)
    for key, val in sections.items():
        note = note.replace("{{" + key + "}}", val)
    return note


def save_note(note: str, topic: dict, date_str: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{date_str}-{topic['topic'].replace('/', '-').replace(' ', '-')}.md"
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(note)
    return filepath


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <topics_file>")
        print("  e.g. python generate.py topics_cs.json")
        sys.exit(1)

    topics_file = Path(sys.argv[1])
    data = load_topics(topics_file)
    topic, idx = get_today_topic(data)
    output_dir = Path(data.get("output_dir", "output"))
    date_str = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")

    print(f"[{data['category_label']}] Generating: {topic['topic']} - {topic['subtopic']}")

    raw = generate_note(topic)
    sections = parse_sections(raw)
    note = build_note(topic, sections, date_str)
    filepath = save_note(note, topic, date_str, output_dir)

    data["current_index"] = (idx + 1) % len(data["topics"])
    save_topics(topics_file, data)

    print(f"Saved: {filepath}")
    return str(filepath)


if __name__ == "__main__":
    main()
