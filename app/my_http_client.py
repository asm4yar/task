from datetime import datetime
from typing import Optional

import httpx
from httpx_socks import SyncProxyTransport


def create_http_client(
        proxy: Optional[str] = None,
        log_file: Optional[str] = None,
        verify: bool = True,
) -> httpx.Client:
    """
    Фабрика для создания httpx.Client с прокси и логированием

    :param proxy: "http://...", "socks5://..." или None
    :param log_file: путь к файлу логов (None - логи в консоль)
    :param verify: проверять SSL
    """

    def _log_request(request: httpx.Request):
        try:
            log_entry = f"\n[REQUEST] {datetime.now()}\n{request.method} {request.url}\n"
            if request.content:
                try:
                    log_entry += f"Body: {request.content.decode()}\n"
                except (UnicodeDecodeError, AttributeError):
                    log_entry += "Body: <binary data>\n"

            if log_file:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
            else:
                print(log_entry)
        except Exception as e:
            print(f"Error logging request: {e}")

    def _log_response(response: httpx.Response):
        try:
            if not response.is_closed:
                try:
                    response.read()  # Принудительно читаем тело, если оно еще не прочитано
                except Exception as e:
                    print(f"Couldn't read streaming response: {e}")
                    return

            log_entry = f"\n[RESPONSE] {datetime.now()}\n{response.status_code} {response.url}\n"
            try:
                log_entry += f"Body: {response.text}\n"
            except (UnicodeDecodeError, AttributeError):
                log_entry += "Body: <binary data>\n"

            if log_file:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
            else:
                print(log_entry)
        except Exception as e:
            print(f"Error logging response: {e}")

    transport = (
        SyncProxyTransport.from_url(proxy, verify=verify)
        if proxy and proxy.startswith("socks5://")
        else httpx.HTTPTransport(proxy=proxy, verify=verify)
    )

    return httpx.Client(
        transport=transport,
        event_hooks={
            'request': [_log_request],
            # 'response': [_log_response],
        },
        verify=verify,
    )
