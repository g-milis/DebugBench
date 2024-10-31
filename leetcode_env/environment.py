import os
import time
from datetime import datetime

import dotenv
import gym
import leetcode
import leetcode.auth

from .types import LeetCodeSubmission
from .utils.leetcode import id_from_slug

dotenv.load_dotenv()


LEETCODE_SESSION_COOKIE = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMTU0NDc5MzciLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI1Zjk1MGVhMDlmNTdkMDA2OGM5MmM1MmQ5NDM4ZmU5NDMxNWJiZGQ4NzlhMWNlYTliZWQwNTFlMGVlOTZlNTcwIiwiaWQiOjE1NDQ3OTM3LCJlbWFpbCI6Im1pbGlzMjc0MDBAZ21haWwuY29tIiwidXNlcm5hbWUiOiJBYXdIYTdLemptIiwidXNlcl9zbHVnIjoiQWF3SGE3S3pqbSIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLmNvbS91c2Vycy9BYXdIYTdLemptL2F2YXRhcl8xNzMwNDA4Nzc4LnBuZyIsInJlZnJlc2hlZF9hdCI6MTczMDQxNjA3NSwiaXAiOiIxMjkuMi4xOTIuMTA5IiwiaWRlbnRpdHkiOiI5ZmFlNzg5NDg5MGZlMjFjZDc3MDkwYWYxMTRhYTJjZCIsInNlc3Npb25faWQiOjc3MjI1MDI4LCJkZXZpY2Vfd2l0aF9pcCI6WyI3MzM0YzFhNjdjODM4ZWI0MGI1OTA4ZmM2ZjE4MGUwNCIsIjEyOS4yLjE5Mi4xMDkiXX0.XnrCVXLI7yYmAqauzakt2l1iMMddoYrYjanZ5MAes2M"

class LeetCodeEnv(gym.Env):
    """
    Gym environment for LeetCode submissions
    """

    metadata = {"render.modes": ["human"]}

    def __init__(self, cooldown=0):
        super(LeetCodeEnv, self).__init__()
        self.__configure_leetcode()
        self.reward = False
        self.last_run = None
        self.cooldown = cooldown  # To avoid rate limit

    def __configure_leetcode(self):
        configuration = leetcode.Configuration()

        # From Dev Tools/Application/Cookies/LEETCODE_SESSION
        leetcode_session = os.environ["LEETCODE_SESSION"]

        csrf_token = "fZDx5AaokwvZWB9FD3NhEa8agd7SLIj7ri7xXColXR2xdGgteKScoCOMoqDnV2YU"
        # if "LEETCODE_CSRF_TOKEN" in os.environ:
        #     csrf_token = "fZDx5AaokwvZWB9FD3NhEa8agd7SLIj7ri7xXColXR2xdGgteKScoCOMoqDnV2YU" #os.environ["LEETCODE_CSRF_TOKEN"]
        # else:
        #     try:
        #         csrf_token = leetcode.auth.get_csrf_cookie(leetcode_session)
        #     except KeyError as e:
        #         raise KeyError(
        #             "Could not find CSRF token in cookies. Set the token manually in an LEETCODE_CSRF_TOKEN environment variable."
        #         ) from e

        configuration.api_key["x-csrftoken"] = csrf_token
        configuration.api_key["csrftoken"] = csrf_token
        configuration.api_key["LEETCODE_SESSION"] = leetcode_session
        configuration.api_key["Referer"] = "https://leetcode.com"
        configuration.debug = False

        self.api_instance = leetcode.DefaultApi(leetcode.ApiClient(configuration))

    def step(self, action: LeetCodeSubmission):
        """
        Sends a submission to LeetCode and returns the result

        Args:
            action (LeetCodeSubmission): LeetCodeSubmission object

        Returns:
            status (str): 'Accepted' | 'Runtime Error'| 'Wrong Answer' | 'Submission Timed-Out' | 'Unknown'
            reward (bool): True if status is 'Accepted', False otherwise
            done (bool): True if status is 'Accepted', False otherwise
            submission_result (dict): LeetCode API response
        """
        submission_result = self.__send_submission(action)

        reward, status = self.__calculate_reward(submission_result)

        self.reward = reward

        done = self.is_done()

        return status, reward, done, submission_result

    def reset(self):
        self.reward = False

    def __send_submission(self, sub: LeetCodeSubmission):
        self.__wait_for_cooldown()

        if sub.question_id is None:
            sub.question_id = id_from_slug(sub.question_slug, self.api_instance)

        submission = leetcode.Submission(
            judge_type="large",
            typed_code=sub.code,
            question_id=sub.question_id,
            test_mode=False,
            lang=sub.lang.value,
        )

        submission_id = self.api_instance.problems_problem_submit_post(
            problem=sub.question_slug, body=submission
        )

        time.sleep(sub.timeout)

        submission_result = self.api_instance.submissions_detail_id_check_get(
            id=submission_id.submission_id
        )

        return submission_result

    def __calculate_reward(self, submission_result):
        if submission_result == {"state": "STARTED"}:
            status_msg = "Submission Timed-Out"

        elif (
            "status" in submission_result.keys()
            and submission_result["status"] == "PENDING"
        ):
            status_msg = "Submission Timed-Out"

        elif "status_msg" in submission_result.keys():
            status_msg = submission_result[
                "status_msg"
            ]  # 'Accepted' | 'Runtime Error'| 'Wrong Answer'

        else:
            status_msg = "Unknown"

        return status_msg == "Accepted", status_msg

    def __wait_for_cooldown(self):
        if self.last_run == None:
            self.last_run = datetime.now()
        else:
            while (datetime.now() - self.last_run).total_seconds() < self.cooldown:
                time.sleep(0.1)
            self.last_run = datetime.now()

    def is_done(self):
        return self.reward
