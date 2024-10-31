import os
# import sys
# sys.path.append("leetcode-hard-gym/leetcode_env")

from leetcode_env.environment import LeetCodeEnv
from leetcode_env.types import LeetCodeSubmission, ProgrammingLanguage


LEETCODE_SESSION_COOKIE = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhY2NvdW50X3ZlcmlmaWVkX2VtYWlsIjpudWxsLCJfYXV0aF91c2VyX2lkIjoiMTU0NDc5MzciLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI1Zjk1MGVhMDlmNTdkMDA2OGM5MmM1MmQ5NDM4ZmU5NDMxNWJiZGQ4NzlhMWNlYTliZWQwNTFlMGVlOTZlNTcwIiwiaWQiOjE1NDQ3OTM3LCJlbWFpbCI6Im1pbGlzMjc0MDBAZ21haWwuY29tIiwidXNlcm5hbWUiOiJBYXdIYTdLemptIiwidXNlcl9zbHVnIjoiQWF3SGE3S3pqbSIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLmNvbS91c2Vycy9kZWZhdWx0X2F2YXRhci5qcGciLCJyZWZyZXNoZWRfYXQiOjE3MzA0MDg3NzgsImlwIjoiMTI5LjIuMTkyLjEwOSIsImlkZW50aXR5IjoiNzZmMzIyY2NlNDkxNzMwMGJkZTNjY2YxYmMzOWVjNDAiLCJzZXNzaW9uX2lkIjo3NzIyMTEyNCwiZGV2aWNlX3dpdGhfaXAiOlsiZjllNDZjNTk3NDhhYWQ5NGIyZjBmZTczNDNhMDA3YTkiLCIxMjkuMi4xOTIuMTA5Il19.UEZ7emxsV9F9_Xpj0fGtsGHgc1GprsS_Jp9C-jxsrAY"


class LeetCodeTester(object):
    def __init__(self):
        os.environ['LEETCODE_SESSION'] = LEETCODE_SESSION_COOKIE
        self.env = LeetCodeEnv(cooldown=15)
        self.lang_dict = {
            "python3": ProgrammingLanguage.PYTHON3,
            "java": ProgrammingLanguage.JAVA,
            "cpp": ProgrammingLanguage.CPP,
        }

    def test(self, code: str, task_id: str, language: str) -> tuple[bool, dict]:
        lang = self.lang_dict.get(language)
        sub = LeetCodeSubmission(code=code, lang=lang, question_slug=task_id)
        status, reward, done, submission_result = self.env.step(sub)
        return reward, submission_result


if __name__ == '__main__':
    tester = LeetCodeTester()
    task_id = "make-number-of-distinct-characters-equal"
    code = "class Solution:\n\n    def insertAndRemove(self, mp, toInsert..."  # abbreviated
    print(tester.test(code, task_id, "python3"))
