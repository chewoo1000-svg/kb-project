#!/usr/bin/env bash
# 저장소 owner가 push 직후 1회 실행. gh CLI 로그인 필요.
#   bash .github/scripts/setup_github.sh <owner/repo> [collaborator1 collaborator2 ...]
set -e
REPO="$1"; shift
[ -z "$REPO" ] && { echo "usage: bash .github/scripts/setup_github.sh <owner/repo> [github-id ...]"; exit 1; }

echo "== 협업자 초대 (write 권한)"
for u in "$@"; do
  gh api -X PUT "repos/$REPO/collaborators/$u" -f permission=push >/dev/null && echo "  invited: $u"
done

echo "== 브랜치 보호: main (PR 필수, 리뷰 1명, force-push 금지)"
for b in main; do
  gh api -X PUT "repos/$REPO/branches/$b/protection" \
    --input - >/dev/null <<JSON
{"required_status_checks":null,"enforce_admins":false,
 "required_pull_request_reviews":{"required_approving_review_count":1,"dismiss_stale_reviews":false},
 "restrictions":null,"allow_force_pushes":false,"allow_deletions":false}
JSON
  echo "  protected: $b"
done

echo "== 라벨"
gh label create task --repo "$REPO" --color 0E8A16 --force >/dev/null

echo "== Issue 7개 생성"
python3 - "$REPO" <<'PY'
import json, subprocess, sys
repo = sys.argv[1]
for it in json.load(open(".github/scripts/issues.json")):
    out = subprocess.run(["gh","issue","create","--repo",repo,"--title",it["title"],"--body",it["body"],"--label","task"],
                         capture_output=True, text=True)
    print("  ", out.stdout.strip() or out.stderr.strip())
PY

echo
echo "완료. 다음: 각 Issue에 담당자(Assignees) 지정 → 팀원은 TEAM_GUIDE.md 대로 clone 후 개인 이름 브랜치 생성."
