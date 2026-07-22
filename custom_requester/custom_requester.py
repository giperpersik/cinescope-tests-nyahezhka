from pydantic import BaseModel
import time
import json
import logging
import os

class CustomRequester:
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.session.headers = self.base_headers.copy()
        self.logger = logging.getLogger(__name__)

    def send_request(self, method, endpoint, data=None, params=None, expected_status=200, need_logging=True, **kwargs):
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        if isinstance(data, BaseModel):
            data = json.loads(data.model_dump_json(exclude_unset=True))

        # 1 Извлекаем (удаляем из kwargs) параметр token, если он был передан
        token = kwargs.pop("token", None)
        if token:
            # 2 Берем существующий словарь заголовков из kwargs или создаем новый пустой
            headers = kwargs.setdefault("headers", {})
            # 3 Записываем туда заголовок авторизации
            headers["authorization"] = f"Bearer {token}"
        response = self.session.request(method, url, json=data, params=params, **kwargs)
        duration = time.time() - start_time

        if need_logging:
            self.log_request_and_response(response, duration)

        if expected_status is not None:
            allowed_statuses = expected_status if isinstance(expected_status, (list, tuple)) else [expected_status]
            if response.status_code not in allowed_statuses:
                raise ValueError(
                    f"Unexpected status code: {response.status_code}. Expected one of: {allowed_statuses}"
                )

        return response

    def _update_session_headers(self, headers):
        self.session.headers.update(headers)

    def _reset_headers(self):
        self.session.headers.pop("Authorization", None)
        self.headers = self.base_headers.copy()


    def log_request_and_response(self, response, duration=None):
        try:
            request = response.request
            GREEN = '\033[32m'
            RED = '\033[31m'
            RESET = '\033[0m'

            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                elif isinstance(request.body, str):
                    body = request.body
                body = f"-d '{body}' \n" if body and body != '{}' else ''

            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code
            is_success = response.ok
            response_data = response.text

            try:
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

            duration_str = f"\tDURATION: {duration:.2f}s\n" if duration is not None else ""

            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            if not is_success:
                self.logger.info(
                    f"\tSTATUS_CODE: {RED}{response_status}{RESET}\n"
                    f"{duration_str}"
                    f"\tDATA: {RED}{response_data}{RESET}"
                )
            else:
                self.logger.info(
                    f"\tSTATUS_CODE: {GREEN}{response_status}{RESET}\n"
                    f"{duration_str}"
                    f"\tDATA:\n{response_data}"
                )
            self.logger.info(f"{'=' * 80}\n")
        except Exception as e:
            self.logger.error(f"\nLogging failed: {type(e)} - {e}")